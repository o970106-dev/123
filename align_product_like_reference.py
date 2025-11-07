import argparse
from typing import Any, Dict, List, Optional

from odoo_jsonrpc import OdooClient, OdooRPCError


def ensure_db(odoo: OdooClient, db_arg: Optional[str]) -> str:
    if db_arg:
        return db_arg
    dbs = odoo.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if not dbs:
        raise RuntimeError("未能取得資料庫清單，請用 --db 指定")
    if len(dbs) > 1:
        raise RuntimeError(f"偵測到多個資料庫：{dbs}，請用 --db 指定其中之一")
    return dbs[0]


def find_template(odoo: OdooClient, name: str) -> Dict[str, Any]:
    res = odoo.search_read(
        "product.template",
        [["name", "=", name]],
        [
            "id",
            "name",
            "available_in_pos",
            "uom_id",
            "pos_categ_id",
            "type",
            "sale_ok",
            "purchase_ok",
            "active",
            "product_variant_count",
        ],
        limit=1,
    )
    if not res:
        raise RuntimeError(f"找不到產品模板：{name}")
    return res[0]


def fields_get(odoo: OdooClient, model: str) -> Dict[str, Any]:
    try:
        return odoo.call_kw(model, "fields_get", [], {"attributes": ["string", "type"]}) or {}
    except OdooRPCError:
        return {}


def list_attribute_lines(odoo: OdooClient, tmpl_id: int) -> List[Dict[str, Any]]:
    return odoo.search_read(
        "product.template.attribute.line",
        [["product_tmpl_id", "=", tmpl_id]],
        ["id", "attribute_id", "value_ids"],
    )


def unlink_records(odoo: OdooClient, model: str, ids: List[int]) -> None:
    if not ids:
        return
    odoo.call_kw(model, "unlink", [ids], {})


def copy_template_core(odoo: OdooClient, ref: Dict[str, Any], target_id: int) -> None:
    # 安全地複製核心欄位（避免價格等營業資料被覆蓋）
    vals: Dict[str, Any] = {}
    if ref.get("available_in_pos") is not None:
        vals["available_in_pos"] = bool(ref["available_in_pos"])  # 強制啟用 POS 顯示
    if ref.get("uom_id"):
        vals["uom_id"] = ref["uom_id"][0] if isinstance(ref["uom_id"], list) else ref["uom_id"]
    if ref.get("pos_categ_id"):
        vals["pos_categ_id"] = ref["pos_categ_id"][0] if isinstance(ref["pos_categ_id"], list) else ref["pos_categ_id"]
    if ref.get("type"):
        vals["type"] = ref["type"]
    if ref.get("sale_ok") is not None:
        vals["sale_ok"] = bool(ref["sale_ok"])  # 能銷售
    if ref.get("active") is not None:
        vals["active"] = bool(ref["active"])  # 非封存
    if vals:
        odoo.write("product.template", [target_id], vals)


def remove_variants_and_attrs(odoo: OdooClient, tmpl_id: int) -> Dict[str, int]:
    # 刪除屬性行，避免再生成變體
    lines = list_attribute_lines(odoo, tmpl_id)
    unlink_records(odoo, "product.template.attribute.line", [ln["id"] for ln in lines])
    # 刪除現有變體（保留第一個）
    variants = odoo.search_read(
        "product.product",
        [["product_tmpl_id", "=", tmpl_id]],
        ["id", "display_name"],
        limit=500,
    )
    removed = 0
    if len(variants) > 1:
        keep_id = variants[0]["id"]
        drop_ids = [v["id"] for v in variants[1:]]
        unlink_records(odoo, "product.product", drop_ids)
        removed = len(drop_ids)
    return {"attrs_removed": len(lines), "variants_removed": removed}


def read_beverage_config(odoo: OdooClient, tmpl_id: int) -> Optional[Dict[str, Any]]:
    # 如果沒有安裝 pos_beverage_modifier 或 point_of_sale，要容錯
    if not fields_get(odoo, "pos.beverage.config"):
        return None
    cfgs = odoo.search_read(
        "pos.beverage.config",
        [["product_tmpl_id", "=", tmpl_id]],
        ["id", "name", "pos_category_id", "show_popup", "line_ids"],
        limit=1,
    )
    if not cfgs:
        return None
    cfg = cfgs[0]
    lines: List[Dict[str, Any]] = []
    if cfg.get("line_ids"):
        for lid in cfg["line_ids"]:
            ln = odoo.read("pos.beverage.config.line", [lid], ["attribute_type", "name", "price", "selected"]) or []
            if ln:
                lines.append(ln[0])
    return {
        "name": cfg.get("name") or "Beverage Config",
        "pos_category_id": (cfg.get("pos_category_id") or [None, None])[0],
        "show_popup": bool(cfg.get("show_popup", True)),
        "lines": lines,
    }


def upsert_beverage_config(odoo: OdooClient, tmpl_id: int, ref_cfg: Dict[str, Any]) -> None:
    if not fields_get(odoo, "pos.beverage.config"):
        return
    existing = odoo.search_read(
        "pos.beverage.config",
        [["product_tmpl_id", "=", tmpl_id]],
        ["id"],
        limit=1,
    )
    cmds = [(5, 0, 0)]  # clear
    for ln in ref_cfg.get("lines", []):
        cmds.append(
            (
                0,
                0,
                {
                    "attribute_type": ln.get("attribute_type") or "other",
                    "name": ln.get("name") or "項目",
                    "price": float(ln.get("price") or 0.0),
                    "selected": bool(ln.get("selected")),
                },
            )
        )
    vals: Dict[str, Any] = {
        "name": ref_cfg.get("name") or "飲品設定",
        "product_tmpl_id": tmpl_id,
        "show_popup": bool(ref_cfg.get("show_popup", True)),
        "line_ids": cmds,
    }
    if ref_cfg.get("pos_category_id"):
        vals["pos_category_id"] = ref_cfg["pos_category_id"]

    if existing:
        odoo.write("pos.beverage.config", [existing[0]["id"]], vals)
    else:
        odoo.create("pos.beverage.config", vals)


def align_like_reference(
    odoo: OdooClient,
    ref_name: str,
    targets: List[str],
) -> List[Dict[str, Any]]:
    ref = find_template(odoo, ref_name)
    ref_cfg = read_beverage_config(odoo, ref["id"])  # may be None
    results: List[Dict[str, Any]] = []
    for name in targets:
        tmpl = find_template(odoo, name)
        stats = remove_variants_and_attrs(odoo, tmpl["id"])  # remove variants/attrs first
        copy_template_core(odoo, ref, tmpl["id"])  # copy POS flags/fields
        if ref_cfg:
            upsert_beverage_config(odoo, tmpl["id"], ref_cfg)
        results.append(
            {
                "target": name,
                "id": tmpl["id"],
                "attrs_removed": stats["attrs_removed"],
                "variants_removed": stats["variants_removed"],
                "pos_enabled": True,
            }
        )
    return results


def main():
    parser = argparse.ArgumentParser(description="以『海鹽檸檬』為參照，清理變體並同步 POS 設定")
    parser.add_argument("--url", required=True, help="Odoo 服務 URL，例如 http://127.0.0.1:18069")
    parser.add_argument("--db", required=False, help="資料庫名稱（可省略，將自動偵測唯一資料庫）")
    parser.add_argument("--login", required=True, help="管理員登入帳號")
    parser.add_argument("--password", required=True, help="管理員登入密碼")
    parser.add_argument("--reference", default="海鹽檸檬", help="參照產品名稱（默認：海鹽檸檬）")
    parser.add_argument(
        "--products",
        required=True,
        help="以逗號分隔的目標產品名稱清單，例如 '招牌咖啡,紅茶拿鐵'",
    )

    args = parser.parse_args()

    odoo = OdooClient(args.url)
    db = ensure_db(odoo, args.db)
    odoo.authenticate(db, args.login, args.password)

    targets = [p.strip() for p in args.products.split(",") if p.strip()]
    results = align_like_reference(odoo, args.reference, targets)
    print("[done] alignment summary:")
    for r in results:
        print(
            f" - {r['target']} (id={r['id']}): attrs_removed={r['attrs_removed']} variants_removed={r['variants_removed']} pos_enabled={r['pos_enabled']}"
        )


if __name__ == "__main__":
    main()

