import argparse
from typing import Any, Dict, List, Optional

from odoo_jsonrpc import OdooClient


def ensure_db(odoo: OdooClient, db: str | None) -> str:
    if db:
        return db
    dbs = odoo.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if not dbs:
        raise RuntimeError("No databases found on server")
    if len(dbs) > 1:
        raise RuntimeError(f"Multiple databases detected: {dbs}. Please specify --db")
    return dbs[0]


def ensure_product_template(odoo: OdooClient, name: str, base_price: float) -> int:
    tmpls = odoo.search_read("product.template", [("name", "=", name)], ["id"], limit=1)
    if tmpls:
        return tmpls[0]["id"]
    return odoo.create("product.template", {"name": name, "list_price": base_price})


def ensure_uom_and_pos_flag(odoo: OdooClient, tmpl_id: int):
    tmpl = odoo.search_read(
        "product.template", [["id", "=", tmpl_id]], ["id", "uom_id", "available_in_pos"], limit=1
    )[0]
    updates: Dict[str, Any] = {}
    if not tmpl.get("available_in_pos"):
        updates["available_in_pos"] = True
    if not tmpl.get("uom_id"):
        candidates = ["Units", "Unit", "個", "件", "pcs"]
        uom = None
        for nm in candidates:
            res = odoo.search_read("uom.uom", [["name", "ilike", nm]], ["id", "name"], limit=1)
            if res:
                uom = res[0]
                break
        if not uom:
            res = odoo.search_read("uom.uom", [["uom_type", "=", "reference"]], ["id", "name"], limit=1)
            if res:
                uom = res[0]
        if uom:
            updates["uom_id"] = uom["id"]
    if updates:
        odoo.write("product.template", [tmpl_id], updates)


def ensure_attribute(odoo: OdooClient, name: str, display_type: str = "select") -> int:
    existing = odoo.search_read("product.attribute", [["name", "=", name]], ["id"], limit=1)
    if existing:
        return existing[0]["id"]
    return odoo.create("product.attribute", {"name": name, "display_type": display_type})


def ensure_attribute_values(odoo: OdooClient, attr_id: int, values: List[Dict[str, Any]]) -> List[int]:
    created_ids: List[int] = []
    for v in values:
        name = v["name"]
        price_extra = v.get("price_extra", 0.0)
        exist = odoo.search_read("product.attribute.value", [["name", "=", name], ["attribute_id", "=", attr_id]], ["id"], limit=1)
        if exist:
            created_ids.append(exist[0]["id"])
            continue
        vid = odoo.create("product.attribute.value", {"name": name, "attribute_id": attr_id, "price_extra": price_extra})
        created_ids.append(vid)
    return created_ids


def ensure_attribute_line(odoo: OdooClient, tmpl_id: int, attr_id: int, value_ids: List[int]):
    lines = odoo.search_read(
        "product.template.attribute.line",
        [["product_tmpl_id", "=", tmpl_id], ["attribute_id", "=", attr_id]],
        ["id"],
        limit=1,
    )
    if lines:
        odoo.write("product.template.attribute.line", [lines[0]["id"]], {"value_ids": [(6, 0, value_ids)]})
        return
    odoo.create(
        "product.template.attribute.line",
        {"product_tmpl_id": tmpl_id, "attribute_id": attr_id, "value_ids": [(6, 0, value_ids)]},
    )


def main():
    ap = argparse.ArgumentParser(description="Seed beverage template and attributes into Odoo")
    ap.add_argument("--url", required=True)
    ap.add_argument("--db")
    ap.add_argument("--login", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--name", default="招牌咖啡")
    ap.add_argument("--price", type=float, default=85.0)
    args = ap.parse_args()

    client = OdooClient(args.url)
    db = ensure_db(client, args.db)
    client.authenticate(db, args.login, args.password)

    tmpl_id = ensure_product_template(client, args.name, args.price)
    ensure_uom_and_pos_flag(client, tmpl_id)

    # Attributes
    map_values = {
        "甜度": [
            {"name": "正常糖 (100%)"},
            {"name": "少糖 (70%)"},
            {"name": "半糖 (50%)"},
            {"name": "微糖 (30%)"},
            {"name": "更換蔗糖"},
        ],
        "溫度": [
            {"name": "熱飲"},
            {"name": "溫飲"},
            {"name": "去冰"},
            {"name": "微冰"},
            {"name": "正常冰"},
            {"name": "冰沙"},
        ],
        "尺寸": [
            {"name": "大杯 (600cc)"},
            {"name": "中杯 (450cc)"},
            {"name": "小杯 (350cc)"},
        ],
    }

    for attr_name, values in map_values.items():
        aid = ensure_attribute(client, attr_name)
        vids = ensure_attribute_values(client, aid, values)
        ensure_attribute_line(client, tmpl_id, aid, vids)

    print(f"[done] seeded product.template id={tmpl_id} with attributes and zero-priced values")


if __name__ == "__main__":
    main()

