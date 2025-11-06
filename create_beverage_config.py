from typing import Any, Dict, List, Optional

from odoo_jsonrpc import OdooClient, OdooRPCError


URL = "http://34.80.194.190"
LOGIN = "admin@wuchang.life"
PASSWORD = "poiuY926"


def ensure_db(client: OdooClient) -> str:
    dbs = client.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if not dbs:
        raise RuntimeError("No databases returned")
    if len(dbs) > 1:
        # pick the first for now; in production, pass explicitly
        print(f"[warn] Multiple databases detected: {dbs}. Using first.")
    return dbs[0]


def ensure_product_template(client: OdooClient, name: str, base_price: float = 60.0) -> int:
    tmpls = client.search_read(
        "product.template",
        [["name", "=", name]],
        ["id", "name", "list_price", "available_in_pos", "uom_id"],
        limit=1,
    )
    if tmpls:
        return tmpls[0]["id"]
    # create minimal product template; base price can be adjusted later
    tmpl_id = client.create("product.template", {"name": name, "list_price": base_price, "type": "consu"})
    return tmpl_id


def ensure_uom_and_pos_flag(client: OdooClient, tmpl_id: int):
    tmpl = client.search_read(
        "product.template", [["id", "=", tmpl_id]], ["id", "uom_id", "available_in_pos"], limit=1
    )[0]
    updates: Dict[str, Any] = {}
    if not tmpl.get("available_in_pos"):
        updates["available_in_pos"] = True
    if not tmpl.get("uom_id"):
        # pick a reasonable UoM
        candidates = ["Units", "Unit", "個", "件", "pcs"]
        uom = None
        for nm in candidates:
            res = client.search_read("uom.uom", [["name", "ilike", nm]], ["id", "name"], limit=1)
            if res:
                uom = res[0]
                break
        if not uom:
            res = client.search_read("uom.uom", [["uom_type", "=", "reference"]], ["id", "name"], limit=1)
            if res:
                uom = res[0]
        if uom:
            updates["uom_id"] = uom["id"]
    if updates:
        client.write("product.template", [tmpl_id], updates)


def find_pos_category_id(client: OdooClient, preferred_names: List[str]) -> Optional[int]:
    for nm in preferred_names:
        res = client.search_read("pos.category", [["name", "ilike", nm]], ["id", "name"], limit=1)
        if res:
            return res[0]["id"]
    # fallback: pick any first category
    res = client.search_read("pos.category", [], ["id", "name"], limit=1)
    if res:
        return res[0]["id"]
    return None


def ensure_beverage_config(client: OdooClient, tmpl_id: int, pos_categ_id: Optional[int]) -> int:
    existing = client.search_read(
        "pos.beverage.config",
        [["product_tmpl_id", "=", tmpl_id]],
        ["id", "name", "product_tmpl_id", "pos_category_id", "show_popup"],
        limit=1,
    )
    vals: Dict[str, Any] = {
        "name": "招牌咖啡設定",
        "product_tmpl_id": tmpl_id,
        "show_popup": True,
    }
    if pos_categ_id:
        vals["pos_category_id"] = pos_categ_id

    lines_cmd = [
        (0, 0, {"attribute_type": "other", "name": "正常甜", "selected": False, "price": 0.0}),
        (0, 0, {"attribute_type": "other", "name": "微糖", "selected": False, "price": 0.0}),
        (0, 0, {"attribute_type": "other", "name": "無糖", "selected": False, "price": 0.0}),
        (0, 0, {"attribute_type": "other", "name": "去冰", "selected": False, "price": 0.0}),
        (0, 0, {"attribute_type": "other", "name": "熱飲", "selected": False, "price": 0.0}),
    ]
    vals["line_ids"] = lines_cmd

    if existing:
        cfg_id = existing[0]["id"]
        # replace lines and update flags/category
        write_vals = vals.copy()
        write_vals["line_ids"] = [(5, 0, 0)] + lines_cmd  # clear then add
        client.write("pos.beverage.config", [cfg_id], write_vals)
        return cfg_id
    return client.create("pos.beverage.config", vals)


def main():
    client = OdooClient(URL)
    db = ensure_db(client)
    client.authenticate(db, LOGIN, PASSWORD)
    print(f"[info] Authenticated to {URL} db={db} as {LOGIN}")

    tmpl_id = ensure_product_template(client, "招牌咖啡", base_price=60.0)
    ensure_uom_and_pos_flag(client, tmpl_id)
    print(f"[info] product.template id={tmpl_id} ready for POS")

    # locate a suitable POS category (若沒有則用任一可用類別)
    pos_categ_id = find_pos_category_id(client, ["咖啡", "Coffee", "飲品", "Beverages"]) or None

    cfg_id = ensure_beverage_config(client, tmpl_id, pos_categ_id)
    print(f"[info] pos.beverage.config id={cfg_id} created/updated for product {tmpl_id}")
    print("[done] 已建立/更新『招牌咖啡』的 Beverage 設定，包含預設 0 元的客製選項，並啟用彈窗。")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[error] {e}")
        raise
