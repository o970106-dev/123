import argparse
from typing import Any, Dict, List

from odoo_jsonrpc import OdooClient


def ensure_db(odoo: OdooClient, db: str | None = None) -> str:
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


def read_product_template(odoo: OdooClient, name: str) -> Dict[str, Any]:
    tmpls = odoo.search_read(
        "product.template",
        [["name", "=", name]],
        [
            "id",
            "name",
            "list_price",
            "available_in_pos",
            "uom_id",
            "attribute_line_ids",
        ],
        limit=1,
    )
    if not tmpls:
        raise RuntimeError(f"Product template not found: {name}")
    return tmpls[0]


def read_attribute_lines(odoo: OdooClient, tmpl_id: int) -> List[Dict[str, Any]]:
    lines = odoo.search_read(
        "product.template.attribute.line",
        [["product_tmpl_id", "=", tmpl_id]],
        ["id", "attribute_id"],
    )
    # enrich with PTAV values and price extras
    enriched: List[Dict[str, Any]] = []
    for ln in lines:
        attr = ln.get("attribute_id")
        attr_name = attr[1] if isinstance(attr, list) and len(attr) == 2 else None
        ptav = odoo.search_read(
            "product.template.attribute.value",
            [["attribute_line_id", "=", ln["id"]]],
            ["id", "name", "price_extra", "product_attribute_value_id"],
        )
        values = [
            {
                "name": v.get("name"),
                "price_extra": v.get("price_extra") or 0.0,
                "pav_id": (v.get("product_attribute_value_id") or [None])[0],
                "ptav_id": v.get("id"),
            }
            for v in ptav
        ]
        enriched.append({"line_id": ln["id"], "attribute": attr_name, "values": values})
    return enriched


def read_variants(odoo: OdooClient, tmpl_id: int) -> List[Dict[str, Any]]:
    return odoo.search_read(
        "product.product",
        [["product_tmpl_id", "=", tmpl_id]],
        ["id", "display_name", "available_in_pos"],
        limit=50,
    )


def main():
    parser = argparse.ArgumentParser(description="讀取指定產品的飲品客製化相關設定")
    parser.add_argument("--url", required=True)
    parser.add_argument("--db")
    parser.add_argument("--login", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--product", default="招牌咖啡")
    args = parser.parse_args()

    client = OdooClient(args.url)
    db = ensure_db(client, args.db)
    client.authenticate(db, args.login, args.password)

    tmpl = read_product_template(client, args.product)
    lines = read_attribute_lines(client, tmpl["id"])
    variants = read_variants(client, tmpl["id"])

    print("[模板]")
    print({
        "id": tmpl["id"],
        "name": tmpl["name"],
        "list_price": tmpl.get("list_price"),
        "available_in_pos": tmpl.get("available_in_pos"),
        "uom": (tmpl.get("uom_id") or [None, None])[1],
        "attribute_line_count": len(lines),
    })

    print("[屬性行]")
    if not lines:
        print("(無)")
    for ln in lines:
        print({
            "attribute": ln["attribute"],
            "values": [{"name": v["name"], "price_extra": v["price_extra"]} for v in ln["values"]],
        })

    print("[變體 product.product]")
    print({"count": len(variants), "examples": [v["display_name"] for v in variants[:10]]})


if __name__ == "__main__":
    main()

