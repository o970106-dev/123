from typing import Any, Dict, List, Optional

from odoo_jsonrpc import OdooClient


URL = "http://34.80.194.190"
LOGIN = "admin@wuchang.life"
PASSWORD = "poiuY926"
PRODUCT_NAME = "招牌咖啡"


def ensure_db(odoo: OdooClient, db: Optional[str] = None) -> str:
    dbs = odoo.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if db:
        return db
    if not dbs:
        raise RuntimeError("No databases found on server")
    return dbs[0]


def find_product(odoo: OdooClient, name: str) -> Dict[str, Any]:
    res = odoo.search_read(
        "product.template",
        [["name", "=", name]],
        [
            "id",
            "name",
            "list_price",
            "available_in_pos",
            "uom_id",
            "uom_po_id",
            "categ_id",
            "product_variant_count",
            "product_variant_ids",
            "attribute_line_ids",
            "taxes_id",
            "supplier_taxes_id",
            "barcode",
            "default_code",
        ],
        limit=1,
    )
    if not res:
        res = odoo.search_read(
            "product.template",
            [["name", "ilike", name]],
            [
                "id",
                "name",
                "list_price",
                "available_in_pos",
                "uom_id",
                "uom_po_id",
                "categ_id",
                "product_variant_count",
                "product_variant_ids",
                "attribute_line_ids",
                "taxes_id",
                "supplier_taxes_id",
                "barcode",
                "default_code",
            ],
            limit=1,
        )
    if not res:
        raise RuntimeError(f"Product template not found: {name}")
    return res[0]


def name_get_many(odoo: OdooClient, model: str, ids: List[int]) -> List[str]:
    if not ids:
        return []
    data = odoo.search_read(model, [["id", "in", ids]], ["id", "name"], limit=len(ids)) or []
    names = []
    by_id = {d["id"]: d.get("name") for d in data}
    for i in ids:
        nm = by_id.get(i)
        names.append(nm if nm else str(i))
    return names


def main():
    client = OdooClient(URL)
    db = ensure_db(client)
    client.authenticate(db, LOGIN, PASSWORD)

    p = find_product(client, PRODUCT_NAME)
    # Resolve M2O names
    def fmt_m2o(val: Any) -> str:
        if isinstance(val, list) and len(val) == 2:
            return f"{val[0]}:{val[1]}"
        if isinstance(val, int):
            return str(val)
        return str(val) if val is not None else ""

    taxes = name_get_many(client, "account.tax", p.get("taxes_id") or [])
    supplier_taxes = name_get_many(client, "account.tax", p.get("supplier_taxes_id") or [])

    print(f"product.template id={p['id']} name={p['name']}")
    print(f"- list_price={p.get('list_price')}")
    print(f"- available_in_pos={p.get('available_in_pos')}")
    print(f"- uom_id={fmt_m2o(p.get('uom_id'))}")
    print(f"- uom_po_id={fmt_m2o(p.get('uom_po_id'))}")
    print(f"- categ_id={fmt_m2o(p.get('categ_id'))}")
    print(f"- product_variant_count={p.get('product_variant_count')}")
    print(f"- product_variant_ids={p.get('product_variant_ids')}")
    print(f"- attribute_line_ids={p.get('attribute_line_ids')}")
    print(f"- taxes_id={p.get('taxes_id')} names={', '.join(taxes)}")
    print(f"- supplier_taxes_id={p.get('supplier_taxes_id')} names={', '.join(supplier_taxes)}")
    print(f"- barcode={p.get('barcode')}")
    print(f"- default_code={p.get('default_code')}")

    # Beverage config relations
    model_exists = client.search_read("ir.model", [["model", "=", "pos.beverage.config"]], ["id"], limit=1)
    if model_exists:
        cfgs = client.search_read(
            "pos.beverage.config",
            [["product_tmpl_id", "=", p["id"]]],
            ["id", "name", "pos_category_id", "show_popup", "line_ids"],
            limit=10,
        ) or []
        if cfgs:
            for c in cfgs:
                print(
                    f"pos.beverage.config id={c['id']} name={c['name']} show_popup={c.get('show_popup')} "
                    f"pos_category_id={fmt_m2o(c.get('pos_category_id'))} line_ids={c.get('line_ids')}"
                )
        else:
            print("pos.beverage.config: none")
    else:
        print("pos.beverage.config: model_not_found")


if __name__ == "__main__":
    main()
