import argparse
from typing import Any, Dict, List

from odoo_jsonrpc import OdooClient


def ensure_db(odoo: OdooClient, db_arg: str | None) -> str:
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
        ["id", "name", "product_variant_count", "available_in_pos", "uom_id"],
        limit=1,
    )
    if not res:
        raise RuntimeError(f"找不到產品模板：{name}")
    return res[0]


def list_attribute_lines(odoo: OdooClient, tmpl_id: int) -> List[Dict[str, Any]]:
    return odoo.search_read(
        "product.template.attribute.line",
        [["product_tmpl_id", "=", tmpl_id]],
        ["id", "attribute_id", "value_ids"],
    )


def main():
    parser = argparse.ArgumentParser(description="驗證指定產品的變體與屬性行狀態")
    parser.add_argument("--url", required=True)
    parser.add_argument("--db")
    parser.add_argument("--login", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--product", default="招牌咖啡")
    args = parser.parse_args()

    odoo = OdooClient(args.url)
    db = ensure_db(odoo, args.db)
    odoo.authenticate(db, args.login, args.password)

    tmpl = find_template(odoo, args.product)
    tid = tmpl["id"]
    lines = list_attribute_lines(odoo, tid)
    print("模板：", {k: tmpl[k] for k in ["id", "name", "product_variant_count", "available_in_pos"]})
    print("屬性行數量：", len(lines))
    if lines:
        for ln in lines:
            attr = ln.get("attribute_id")
            attr_name = attr[1] if isinstance(attr, list) and len(attr) == 2 else None
            print(f" - line_id={ln['id']} attribute={attr_name} values={ln.get('value_ids')}")
    else:
        print("[ok] 屬性行為空，產品不再生成變體。")

    # 顯示實際變體產品數量（product.product）
    variants = odoo.search_read(
        "product.product",
        [["product_tmpl_id", "=", tid]],
        ["id", "display_name"],
        limit=50,
    )
    print("現有變體 product.product 記錄數：", len(variants))
    if variants:
        print("示例：", [v["display_name"] for v in variants[:10]])


if __name__ == "__main__":
    main()

