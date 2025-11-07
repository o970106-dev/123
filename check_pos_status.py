import json
from odoo_jsonrpc import OdooClient


def main():
    url = "http://127.0.0.1:18069"
    db_name = "wuchang_preview_20251107"
    login = "admin"
    pw = "odoo"

    print("Connecting to", url)
    client = OdooClient(url)
    dbs = client.list_databases()
    print("DBs:", dbs)
    if not dbs:
        print("No databases returned")
        return

    db = db_name if db_name in dbs else dbs[0]
    print("Using DB:", db)
    client.authenticate(db, login, pw)
    print("Authenticated as", login)

    # Determine available fields dynamically to avoid invalid-field errors across versions
    fields_info = client.call_kw("pos.config", "fields_get", [], {"attributes": ["string"]}) or {}
    candidate_fields = [
        "id",
        "name",
        "company_id",
        "currency_id",
        "pos_session_state",
        "current_session_id",
        "active",
    ]
    read_fields = [f for f in candidate_fields if f in fields_info]
    configs = client.search_read("pos.config", [], read_fields, limit=50)
    print("pos.config records:", json.dumps(configs, ensure_ascii=False))

    uoms = client.search_read("uom.uom", [], ["id", "name"], limit=10)
    print("UoM sample:", json.dumps(uoms, ensure_ascii=False))

    products = client.search_read(
        "product.product", [], ["id", "name", "uom_id"], limit=5
    )
    print("Product sample:", json.dumps(products, ensure_ascii=False))


if __name__ == "__main__":
    main()
