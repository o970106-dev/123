import argparse
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

try:
    from openpyxl import load_workbook
except Exception as e:
    load_workbook = None  # will error at runtime with a clear message

from odoo_jsonrpc import OdooClient, OdooRPCError


def load_config(path: str = "config.json") -> dict:
    """Loads config, falling back to example."""
    if not os.path.exists(path):
        alt = os.path.join(os.path.dirname(__file__), "config.example.json")
        if not os.path.exists(alt):
            raise FileNotFoundError("Missing config: create config.json or keep config.example.json")
        path = alt
        print(f"[info] Using example config: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def guess_columns(headers: List[str]) -> Dict[str, int]:
    """Best-effort column name guessing for common menu formats.
    Returns a mapping: {"name": idx, "price": idx, "category": idx, "sku": idx}
    """
    lowered = [h.strip().lower() for h in headers]

    def find(candidates: List[str]) -> Optional[int]:
        # Prefer exact/specific matches by scanning candidates first, then headers
        for cand in candidates:
            c = cand.strip().lower()
            for i, h in enumerate(lowered):
                if h == c or c in h:
                    return i
        return None

    name_idx = find([
        "name", "品名", "商品", "品項", "menu", "項目", "名稱", "主商品名稱",
    ])
    price_idx = find([
        "price", "售價", "單價", "價格", "價", "list_price", "主商品價格",
    ])
    category_idx = find([
        "category", "類別", "分類", "pos類別", "pos category", "主商品類別",
    ])
    sku_idx = find([
        "sku", "code", "條碼", "barcode", "貨號", "型號", "主商品代碼", "主商品料號", "主商品編號",
    ])
    combo_idx = find([
        "套用加購選單", "加購題型選單", "加購組合", "題型選項組合編號", "選項組合編號",
    ])

    mapping: Dict[str, int] = {}
    if name_idx is not None:
        mapping["name"] = name_idx
    if price_idx is not None:
        mapping["price"] = price_idx
    if category_idx is not None:
        mapping["category"] = category_idx
    if sku_idx is not None:
        mapping["sku"] = sku_idx
    if combo_idx is not None:
        mapping["combo_id"] = combo_idx
    return mapping


def read_excel(path: str, sheet: Optional[str] = None) -> Tuple[List[Dict[str, Any]], List[str]]:
    if load_workbook is None:
        raise RuntimeError("缺少 openpyxl，請先安裝：pip install openpyxl")
    wb = load_workbook(path, data_only=True)
    ws = wb[sheet] if sheet and sheet in wb.sheetnames else wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return [], []
    headers = [str(c).strip() if c is not None else "" for c in rows[0]]
    mapping = guess_columns(headers)

    def get_val(r: List[Any], idx: Optional[int]) -> Any:
        if idx is None:
            return None
        return r[idx] if idx < len(r) else None

    items: List[Dict[str, Any]] = []
    for r in rows[1:]:
        name = get_val(r, mapping.get("name"))
        price = get_val(r, mapping.get("price"))
        category = get_val(r, mapping.get("category"))
        sku = get_val(r, mapping.get("sku"))
        combo_id = get_val(r, mapping.get("combo_id"))

        if name is None or (isinstance(name, str) and not name.strip()):
            continue

        # normalize price
        p: Optional[float] = None
        if price is not None:
            try:
                if isinstance(price, str):
                    # remove currency symbols and commas
                    price = re.sub(r"[^0-9.\-]", "", price)
                p = float(price)  # may raise ValueError
            except Exception:
                p = None

        items.append({
            "name": str(name).strip(),
            "price": p,
            "category": str(category).strip() if isinstance(category, str) else category,
            "sku": str(sku).strip() if isinstance(sku, str) else sku,
            "combo_id": str(combo_id).strip() if isinstance(combo_id, str) else combo_id,
        })

    return items, headers


def _attribute_type_from_group(group_name: str) -> str:
    g = (group_name or "").strip().lower()
    if any(k in g for k in ["甜", "sweet"]):
        return "sweetness"
    if any(k in g for k in ["溫度", "冰", "熱", "temp", "temperature"]):
        return "temperature"
    if any(k in g for k in ["尺寸", "大小", "size"]):
        return "size"
    return "other"


def read_combo_options(path: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    解析 Excel 的『加購題型選項組合』與『加購選項項目』兩個分頁，
    回傳 mapping: combo_id -> list of {type, name, price}
    """
    if load_workbook is None:
        raise RuntimeError("缺少 openpyxl，請先安裝：pip install openpyxl")
    wb = load_workbook(path, data_only=True)
    combos: Dict[str, str] = {}
    if "加購題型選項組合" in wb.sheetnames:
        ws = wb["加購題型選項組合"]
        rows = list(ws.iter_rows(values_only=True))
        for r in rows[1:]:
            cid = r[0]
            name = r[1]
            if cid:
                combos[str(cid)] = str(name or "")
    mapping: Dict[str, List[Dict[str, Any]]] = {}
    if "加購選項項目" in wb.sheetnames:
        ws2 = wb["加購選項項目"]
        rows2 = list(ws2.iter_rows(values_only=True))
        # 預期欄位：題型選項組合編號, 加購題型, 加購選項顯示名稱, 加購選項價格
        for r in rows2[1:]:
            cid = r[0]
            group = r[1]  # 加購題型
            opt_name = r[4] if len(r) > 4 else r[3]  # 顯示名稱
            price_raw = r[5] if len(r) > 5 else None
            price: Optional[float] = None
            if price_raw is not None:
                try:
                    price = float(str(price_raw).replace(",", ""))
                except Exception:
                    price = None
            if cid and opt_name:
                k = str(cid)
                lst = mapping.setdefault(k, [])
                lst.append({
                    "type": _attribute_type_from_group(str(group or "")),
                    "name": str(opt_name),
                    "price": price or 0.0,
                })
    return mapping


def ensure_db(odoo: OdooClient, db: Optional[str]) -> str:
    if db:
        return db
    dbs = odoo.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if not dbs:
        raise RuntimeError("No databases found on server")
    return dbs[0]


def ensure_pos_category(odoo: OdooClient, name: str) -> int:
    cats = odoo.search_read("pos.category", [["name", "=", name]], ["id"], limit=1)
    if cats:
        return cats[0]["id"]
    return odoo.create("pos.category", {"name": name})


def create_or_update_product(
    odoo: OdooClient,
    name: str,
    list_price: Optional[float],
    category_id: Optional[int],
    update_existing: bool = True,
) -> Tuple[int, str]:
    # find existing template by name (exact match)
    existing = odoo.search_read(
        "product.template", [["name", "=", name]], ["id", "list_price", "available_in_pos"], limit=1
    )
    pos_cat_field = "pos_category_id"

    def vals(base_price: Optional[float], cat_id: Optional[int]) -> Dict[str, Any]:
        v: Dict[str, Any] = {
            "name": name,
            "sale_ok": True,
            "available_in_pos": True,
            "type": "consu",
        }
        if base_price is not None:
            v["list_price"] = base_price
        if cat_id is not None:
            v[pos_cat_field] = cat_id
        return v

    # create or update
    if existing:
        pid = existing[0]["id"]
        action = "skipped"
        if update_existing:
            try:
                odoo.write("product.template", [pid], vals(list_price, category_id))
                action = "updated"
            except OdooRPCError:
                # fallback field name used by older Odoo
                pos_cat_field_backup = "pos_categ_id"
                try:
                    backup_vals = vals(list_price, None)
                    if category_id is not None:
                        backup_vals[pos_cat_field_backup] = category_id
                    odoo.write("product.template", [pid], backup_vals)
                    action = "updated"
                except OdooRPCError as e2:
                    raise e2
        return pid, action

    try:
        new_id = odoo.create("product.template", vals(list_price, category_id))
        return new_id, "created"
    except OdooRPCError:
        # fallback field name
        pos_cat_field = "pos_categ_id"
        new_id = odoo.create("product.template", vals(list_price, category_id))
        return new_id, "created"


def main() -> None:
    # Load config first to set defaults
    cfg = load_config()
    odoo_cfg = cfg.get("odoo", {})

    ap = argparse.ArgumentParser(description="Import POS menu from Excel into Odoo")
    ap.add_argument("--source", required=True, help="Excel file path (.xlsx)")
    ap.add_argument("--sheet", help="Sheet name (default: active)")
    ap.add_argument("--url", default=odoo_cfg.get("url"), help="Odoo base URL")
    ap.add_argument("--login", default=odoo_cfg.get("login"), help="Odoo login")
    ap.add_argument("--password", default=odoo_cfg.get("password"), help="Odoo password")
    ap.add_argument("--db", default=odoo_cfg.get("db"), help="Database name (optional)")
    ap.add_argument("--apply", action="store_true", help="Apply changes to Odoo (default: dry-run)")
    ap.add_argument("--update-existing", action="store_true", help="Update existing products if found")
    ap.add_argument("--skip-ambiguous", action="store_true", help="Skip items with uncertain fields (price/category/combo)")
    ap.add_argument("--no-config", action="store_true", help="Do not create beverage config even if combo exists")
    ap.add_argument("--only-combo", action="store_true", help="Only include/apply items whose combo has options (skip items without題型)")
    ap.add_argument("--dump", help="Write prepared payload JSON to file without connecting")
    args = ap.parse_args()

    items, headers = read_excel(args.source, args.sheet)
    combo_map = read_combo_options(args.source)
    if not items:
        print("[error] No rows parsed from Excel. Headers:", headers)
        return

    print(f"[info] Parsed {len(items)} items. Sample:")
    for s in items[:5]:
        print("  -", s)

    # 顯示加購題型解析摘要（前 2 個不同 combo）
    shown = 0
    seen: set = set()
    for it in items:
        cid = it.get("combo_id")
        if not cid or cid in seen:
            continue
        seen.add(cid)
        lines = combo_map.get(str(cid)) or []
        print(f"[info] Combo {cid}: {len(lines)} options")
        for ln in lines[:6]:
            print("    -", ln)
        shown += 1
        if shown >= 2:
            break

    # 價格驗算展示：列出前 5 筆商品的尺寸價格表，並以 M 作為基準價
    print("[check] Price tables for first 5 items (M-baseline):")
    cnt = 0
    for it in items:
        base = it.get("price") or 0.0
        cid = str(it.get("combo_id") or "")
        sizes = [ln for ln in (combo_map.get(cid) or []) if ln.get("type") == "size"]
        if not sizes:
            continue
        m_extra = next((ln.get("price") or 0.0 for ln in sizes if str(ln.get("name")).strip().upper() == "M"), 0.0)
        base_m = round(base + m_extra, 2)
        tbl = {ln["name"]: round(base + (ln.get("price") or 0.0), 2) for ln in sizes}
        default = "M" if any(str(ln.get("name")).strip().upper() == "M" for ln in sizes) else None
        print(f"    - {it.get('name')} base_M={base_m} default={default} table={tbl}")
        cnt += 1
        if cnt >= 5:
            break

    if not args.apply:
        # Optional offline dump: build payload using M-baseline and normalized size extras
        if args.dump:
            payload = []
            for it in items:
                name = str(it.get("name") or "").strip()
                if not name:
                    continue
                price = it.get("price")
                cat_name = str(it.get("category") or "").strip()
                combo_id = str(it.get("combo_id") or "").strip()
                # ambiguity check
                reasons = []
                if price is None:
                    reasons.append("price")
                if not cat_name:
                    reasons.append("category")
                if combo_id and not (combo_map.get(combo_id) or []):
                    reasons.append("combo")
                if args.skip_ambiguous and reasons:
                    continue
                # optional: require題型（combo）才建入/輸出
                lines_for_combo = combo_map.get(combo_id) or []
                if args.only_combo and not lines_for_combo:
                    # 無題型或題型無選項，略過此商品
                    continue
                sizes_for_item = [ln for ln in (combo_map.get(combo_id) or []) if ln.get("type") == "size"]
                m_extra_apply = next((ln.get("price") or 0.0 for ln in sizes_for_item if str(ln.get("name")).strip().upper() == "M"), 0.0)
                price_m = round((price or 0.0) + m_extra_apply, 2)
                config_lines = []
                lines = combo_map.get(combo_id) or []
                if not args.no_config and lines:
                    m_extra_cfg = next((ln.get("price") or 0.0 for ln in lines if ln.get("type") == "size" and str(ln.get("name")).strip().upper() == "M"), 0.0)
                    for ln in lines:
                        is_size = ln["type"] == "size"
                        is_m = is_size and str(ln.get("name")).strip().upper() == "M"
                        adj_price = (ln.get("price") or 0.0) - (m_extra_cfg if is_size else 0.0)
                        config_lines.append({
                            "attribute_type": ln["type"],
                            "name": ln["name"],
                            "selected": bool(is_m),
                            "price": round(adj_price, 2),
                        })
                payload.append({
                    "name": name,
                    "sku": it.get("sku"),
                    "category": cat_name,
                    "combo_id": combo_id,
                    "price_m": price_m,
                    "config": None if (args.no_config or not config_lines) else {
                        "show_popup": True,
                        "pos_category_name": cat_name or None,
                        "lines": config_lines,
                    },
                })
            with open(args.dump, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            print(f"[dump] Wrote prepared payload with {len(payload)} items to {args.dump}")
        else:
            print("[dry-run] Not applying changes. Use --apply to write to Odoo.")
        return

    client = OdooClient(args.url)
    db = ensure_db(client, args.db)
    client.authenticate(db, args.login, args.password)
    print(f"[info] Authenticated to {args.url}, db={db} as {args.login}")

    # cache categories
    cat_cache: Dict[str, int] = {}

    created, updated, skipped = 0, 0, 0
    for it in items:
        name = str(it.get("name") or "").strip()
        if not name:
            continue
        price = it.get("price")
        cat_name = str(it.get("category") or "").strip()
        combo_id = str(it.get("combo_id") or "").strip()
        # determine ambiguity
        reasons = []
        if price is None:
            reasons.append("price")
        if not cat_name:
            reasons.append("category")
        if combo_id and not (combo_map.get(combo_id) or []):
            reasons.append("combo")
        if args.skip_ambiguous and reasons:
            print(f"[skip] ambiguous item '{name}' reasons={reasons}")
            skipped += 1
            continue
        # 若要求只有題型才建入，無題型則略過
        lines_for_combo = combo_map.get(combo_id) or []
        if args.only_combo and not lines_for_combo:
            print(f"[skip] no combo/options for '{name}'")
            skipped += 1
            continue
        cat_id: Optional[int] = None
        if cat_name:
            cat_id = cat_cache.get(cat_name)
            if cat_id is None:
                cat_id = ensure_pos_category(client, cat_name)
                cat_cache[cat_name] = cat_id

        # 以 M 作為基準，重算產品主售價
        sizes_for_item = [ln for ln in (combo_map.get(combo_id) or []) if ln.get("type") == "size"]
        m_extra_apply = next((ln.get("price") or 0.0 for ln in sizes_for_item if str(ln.get("name")).strip().upper() == "M"), 0.0)
        price_m = (price or 0.0) + m_extra_apply

        pid, action = create_or_update_product(
            client, name=name, list_price=price_m, category_id=cat_id, update_existing=args.update_existing
        )
        if action == "created":
            created += 1
        elif action == "updated":
            updated += 1
        else:
            skipped += 1
        print(f"[ok] {action}: product.template(id={pid}) name='{name}' price={price} cat='{cat_name}'")

        # 建立/更新飲品客製設定（若加購題型存在且模型可用）
        if not args.no_config:
            try:
                model_exists = client.search_read("ir.model", [["model", "=", "pos.beverage.config"]], ["id"], limit=1)
            except OdooRPCError:
                model_exists = []
        else:
            model_exists = []
        if combo_id and model_exists:
            cfg = client.search_read(
                "pos.beverage.config",
                [["product_tmpl_id", "=", pid]],
                ["id"],
                limit=1,
            )
            cfg_id: Optional[int] = cfg[0]["id"] if cfg else None
            lines = combo_map.get(combo_id) or []
            # 準備 Odoo 寫入命令：清除舊行，加入新行
            # 標記尺寸中加價為 0 的選項為預設選中，以符合主商品基準價格（有些以 S、有些以 M）
            cmd = [(5, 0, 0)]
            # 將尺寸加價以 M 為基準重新正規化，並將 M 標記為預設選中
            m_extra_cfg = next((ln.get("price") or 0.0 for ln in lines if ln.get("type") == "size" and str(ln.get("name")).strip().upper() == "M"), 0.0)
            for ln in lines:
                is_size = ln["type"] == "size"
                is_m = is_size and str(ln.get("name")).strip().upper() == "M"
                adj_price = (ln.get("price") or 0.0) - (m_extra_cfg if is_size else 0.0)
                selected = True if is_m else False
                cmd.append((0, 0, {"attribute_type": ln["type"], "name": ln["name"], "selected": selected, "price": adj_price}))
            vals = {"name": f"{name}設定", "product_tmpl_id": pid, "show_popup": True, "line_ids": cmd}
            if cat_id:
                vals["pos_category_id"] = cat_id
            if cfg_id:
                client.write("pos.beverage.config", [cfg_id], vals)
            else:
                client.create("pos.beverage.config", vals)

    print(f"[summary] created={created}, updated={updated}, skipped={skipped}")


if __name__ == "__main__":
    main()
