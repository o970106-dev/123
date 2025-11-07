import argparse
import json
from typing import Any, Dict, Optional, Tuple

from odoo_jsonrpc import OdooClient, OdooRPCError


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
    existing = odoo.search_read(
        "product.template", [["name", "=", name]], ["id", "list_price", "available_in_pos"], limit=1
    )
    # Odoo 19 使用 Many2many 欄位 'pos_categ_ids'；較舊版本可能為 'pos_category_id' 或 'pos_categ_id'
    pos_cat_fields = ["pos_categ_ids", "pos_category_id", "pos_categ_id"]

    def vals(base_price: Optional[float], cat_id: Optional[int], field: Optional[str] = None) -> Dict[str, Any]:
        v: Dict[str, Any] = {
            "name": name,
            "sale_ok": True,
            "available_in_pos": True,
            "type": "consu",
        }
        if base_price is not None:
            v["list_price"] = base_price
        if cat_id is not None:
            if field == "pos_categ_ids":
                # Many2many 賦值使用 (6, 0, [ids]) 指令
                v[field] = [(6, 0, [cat_id])]
            elif field:
                v[field] = cat_id
        return v

    if existing:
        pid = existing[0]["id"]
        action = "skipped"
        if update_existing:
            # 依序嘗試新版、多版本相容的欄位
            last_error: Optional[Exception] = None
            for field in pos_cat_fields:
                try:
                    odoo.write("product.template", [pid], vals(list_price, category_id, field))
                    action = "updated"
                    last_error = None
                    break
                except OdooRPCError as e:
                    last_error = e
            if last_error:
                # 若全部欄位都失敗，再嘗試不設類別僅更新價格與 available_in_pos
                try:
                    odoo.write("product.template", [pid], vals(list_price, None, None))
                    action = "updated"
                except OdooRPCError as e2:
                    raise e2
        return pid, action

    # 建立新產品時，優先使用 Odoo 19 欄位，其次相容欄位
    last_error: Optional[Exception] = None
    for field in pos_cat_fields:
        try:
            new_id = odoo.create("product.template", vals(list_price, category_id, field))
            return new_id, "created"
        except OdooRPCError as e:
            last_error = e
    # 若類別欄位皆不可用，則不設類別建立
    new_id = odoo.create("product.template", vals(list_price, None, None))
    return new_id, "created"


def main():
    ap = argparse.ArgumentParser(description="Apply prebuilt payload JSON to Odoo (M-baseline prices)")
    ap.add_argument("--url", required=True)
    ap.add_argument("--login", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--db")
    ap.add_argument("--payload", required=True, help="Path to JSON payload produced by import_pos_menu --dump")
    ap.add_argument("--update-existing", action="store_true")
    ap.add_argument("--no-config", action="store_true")
    ap.add_argument("--only-config", action="store_true", help="Only apply products that have beverage config lines (skip items without題型)")
    args = ap.parse_args()

    client = OdooClient(args.url)
    dbs = client.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    db = args.db or (dbs[0] if dbs else None)
    if not db:
        raise RuntimeError("No databases found; please pass --db")
    client.authenticate(db, args.login, args.password)
    print(f"[info] Authenticated to {args.url}, db={db} as {args.login}")

    with open(args.payload, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[info] Loaded payload items: {len(data)}")

    created, updated, skipped = 0, 0, 0
    for it in data:
        name = str(it.get("name") or "").strip()
        if not name:
            continue
        cat_name = str(it.get("category") or "").strip()
        price_m = it.get("price_m")

        cat_id = None
        if cat_name:
            cat_id = ensure_pos_category(client, cat_name)

        # 若要求僅套用有設定的商品，且此項目無設定，則跳過整筆（不建立產品）
        if args.only_config:
            cfg_probe = it.get("config")
            if not cfg_probe or not cfg_probe.get("lines"):
                print(f"[skip] no config for '{name}', respecting --only-config")
                skipped += 1
                continue

        pid, action = create_or_update_product(
            client, name=name, list_price=price_m, category_id=cat_id, update_existing=args.update_existing
        )
        if action == "created":
            created += 1
        elif action == "updated":
            updated += 1
        else:
            skipped += 1
        print(f"[ok] {action}: product.template(id={pid}) name='{name}' price_m={price_m} cat='{cat_name}'")

        if args.no_config:
            continue
        cfg = it.get("config")
        if not cfg or not cfg.get("lines"):
            continue
        # write/update beverage config
        existing_cfg = client.search_read(
            "pos.beverage.config", [["product_tmpl_id", "=", pid]], ["id"], limit=1
        )
        cfg_id = existing_cfg[0]["id"] if existing_cfg else None
        cmd = [(5, 0, 0)]
        for ln in cfg["lines"]:
            cmd.append((0, 0, {
                "attribute_type": ln.get("attribute_type"),
                "name": ln.get("name"),
                "selected": bool(ln.get("selected")),
                "price": float(ln.get("price") or 0.0),
            }))
        vals = {
            "name": f"{name}設定",
            "product_tmpl_id": pid,
            "show_popup": bool(cfg.get("show_popup", True)),
            "line_ids": cmd,
        }
        if cat_id:
            vals["pos_category_id"] = cat_id
        if cfg_id:
            client.write("pos.beverage.config", [cfg_id], vals)
        else:
            client.create("pos.beverage.config", vals)
        print(f"[ok] beverage config applied for product '{name}'")

    print(f"[summary] created={created}, updated={updated}, skipped={skipped}")


if __name__ == "__main__":
    main()
