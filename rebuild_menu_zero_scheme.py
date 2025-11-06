import argparse
from typing import Any, Dict, List

from odoo_jsonrpc import OdooClient


def ensure_db(odoo: OdooClient, db: str | None) -> str:
    if db:
        return db
    dbs = odoo.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if not dbs:
        raise RuntimeError("未能取得資料庫清單")
    if len(dbs) > 1:
        raise RuntimeError(f"偵測到多個資料庫：{dbs}，請用 --db 指定其中之一")
    return dbs[0]


def find_uom(odoo: OdooClient) -> int | None:
    candidates = ["Units", "Unit", "個", "件", "pcs"]
    for nm in candidates:
        res = odoo.search_read("uom.uom", [["name", "ilike", nm]], ["id", "name"], limit=1)
        if res:
            return res[0]["id"]
    res = odoo.search_read("uom.uom", [["uom_type", "=", "reference"]], ["id", "name"], limit=1)
    if res:
        return res[0]["id"]
    return None


def zero_price_extras_for_template(odoo: OdooClient, tmpl_id: int) -> None:
    lines = odoo.search_read(
        "product.template.attribute.line",
        [["product_tmpl_id", "=", tmpl_id]],
        ["id"],
    )
    for ln in lines:
        ptavs = odoo.search_read(
            "product.template.attribute.value",
            [["attribute_line_id", "=", ln["id"]]],
            ["id", "price_extra"],
        )
        for v in ptavs:
            if v.get("price_extra"):
                odoo.write("product.template.attribute.value", [v["id"]], {"price_extra": 0.0})


def rebuild_product(odoo: OdooClient, name: str, base_price: float) -> List[int]:
    tmpls = odoo.search_read("product.template", [["name", "=", name]], ["id", "name", "uom_id", "available_in_pos"])
    if not tmpls:
        tid = odoo.create("product.template", {"name": name, "list_price": base_price, "type": "consu", "available_in_pos": True})
        zero_price_extras_for_template(odoo, tid)
        return [tid]

    uom_id = find_uom(odoo)
    ids: List[int] = []
    for t in tmpls:
        updates: Dict[str, Any] = {"list_price": base_price, "available_in_pos": True}
        if not t.get("uom_id") and uom_id:
            updates["uom_id"] = uom_id
        odoo.write("product.template", [t["id"]], updates)
        zero_price_extras_for_template(odoo, t["id"])
        ids.append(t["id"])
    return ids


def main():
    parser = argparse.ArgumentParser(description="重建菜單並套用前端加價方案（後端屬性零加價）")
    parser.add_argument("--url", required=True)
    parser.add_argument("--db")
    parser.add_argument("--login", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--product", default="招牌咖啡")
    parser.add_argument("--price", type=float, default=85.0, help="產品基礎售價（默認 85.0）")
    args = parser.parse_args()

    odoo = OdooClient(args.url)
    db = ensure_db(odoo, args.db)
    odoo.authenticate(db, args.login, args.password)

    ids = rebuild_product(odoo, args.product, args.price)
    print(f"[ok] 菜單重建完成，產品 '{args.product}' 已設定基礎價 {args.price}，模板 ids={ids}")


if __name__ == "__main__":
    main()

