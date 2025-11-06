from typing import Any, Dict, List, Optional
import os
import xml.etree.ElementTree as ET

from odoo_jsonrpc import OdooClient


URL = "http://34.80.194.190"
LOGIN = "admin@wuchang.life"
PASSWORD = "poiuY926"
PRODUCT_NAME = "招牌咖啡"
OUTPUT_FILENAME = f"product_{PRODUCT_NAME}.xml"


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
    fields = [
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
    ]
    res = odoo.search_read("product.template", [["name", "=", name]], fields, limit=1)
    if not res:
        res = odoo.search_read("product.template", [["name", "ilike", name]], fields, limit=1)
    if not res:
        raise RuntimeError(f"Product template not found: {name}")
    return res[0]


def name_get_many(odoo: OdooClient, model: str, ids: List[int]) -> Dict[int, str]:
    if not ids:
        return {}
    data = odoo.search_read(model, [["id", "in", ids]], ["id", "name"], limit=len(ids)) or []
    return {d["id"]: (d.get("name") or str(d["id"])) for d in data}


def fmt_m2o(elem: ET.Element, tag: str, val: Any):
    node = ET.SubElement(elem, tag)
    if isinstance(val, list) and len(val) == 2:
        node.set("id", str(val[0]))
        node.set("name", str(val[1]))
    elif isinstance(val, int):
        node.set("id", str(val))
    elif val in (None, False):
        node.set("null", "true")
    else:
        node.text = str(val)


def list_ids(elem: ET.Element, tag: str, ids: List[int], names: Optional[Dict[int, str]] = None):
    parent = ET.SubElement(elem, tag)
    for i in ids or []:
        it = ET.SubElement(parent, "id")
        it.text = str(i)
        if names and i in names:
            it.set("name", names[i])


def export_xml(product: Dict[str, Any], client: OdooClient) -> str:
    root = ET.Element("product")
    root.set("model", "product.template")
    root.set("id", str(product["id"]))
    root.set("name", str(product["name"]))

    fields = ET.SubElement(root, "fields")
    ET.SubElement(fields, "list_price").text = str(product.get("list_price"))
    ET.SubElement(fields, "available_in_pos").text = str(product.get("available_in_pos"))
    fmt_m2o(fields, "uom_id", product.get("uom_id"))
    fmt_m2o(fields, "uom_po_id", product.get("uom_po_id"))
    fmt_m2o(fields, "categ_id", product.get("categ_id"))

    ET.SubElement(fields, "product_variant_count").text = str(product.get("product_variant_count"))
    list_ids(fields, "product_variant_ids", product.get("product_variant_ids") or [])
    list_ids(fields, "attribute_line_ids", product.get("attribute_line_ids") or [])

    taxes_names = name_get_many(client, "account.tax", product.get("taxes_id") or [])
    supplier_taxes_names = name_get_many(client, "account.tax", product.get("supplier_taxes_id") or [])
    list_ids(fields, "taxes_id", product.get("taxes_id") or [], taxes_names)
    list_ids(fields, "supplier_taxes_id", product.get("supplier_taxes_id") or [], supplier_taxes_names)

    ET.SubElement(fields, "barcode").text = str(product.get("barcode"))
    ET.SubElement(fields, "default_code").text = str(product.get("default_code"))

    # Beverage config relations (if module installed)
    model_exists = client.search_read("ir.model", [["model", "=", "pos.beverage.config"]], ["id"], limit=1)
    relations = ET.SubElement(root, "relations")
    if model_exists:
        cfgs = client.search_read(
            "pos.beverage.config",
            [["product_tmpl_id", "=", product["id"]]],
            ["id", "name", "pos_category_id", "show_popup", "line_ids"],
            limit=50,
        ) or []
        cfg_parent = ET.SubElement(relations, "pos_beverage_config")
        for c in cfgs:
            cnode = ET.SubElement(cfg_parent, "config")
            cnode.set("id", str(c["id"]))
            cnode.set("name", str(c["name"]))
            ET.SubElement(cnode, "show_popup").text = str(c.get("show_popup"))
            fmt_m2o(cnode, "pos_category_id", c.get("pos_category_id"))
            list_ids(cnode, "line_ids", c.get("line_ids") or [])
    else:
        ET.SubElement(relations, "pos_beverage_config").set("status", "model_not_found")

    tree = ET.ElementTree(root)
    out_path = os.path.join(os.getcwd(), OUTPUT_FILENAME)
    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    return out_path


def main():
    client = OdooClient(URL)
    db = ensure_db(client)
    client.authenticate(db, LOGIN, PASSWORD)

    product = find_product(client, PRODUCT_NAME)
    path = export_xml(product, client)
    print(path)


if __name__ == "__main__":
    main()

