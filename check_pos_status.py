import json
from odoo_jsonrpc import OdooClient


def main():
    url = "http://34.80.194.190"
    login = "admin@wuchang.life"
    pw = "poiuY926"

    print("Connecting to", url)
    client = OdooClient(url)
    dbs = client.list_databases()
    print("DBs:", dbs)
    if not dbs:
        print("No databases returned")
        return

    db = dbs[0]
    print("Using DB:", db)
    client.authenticate(db, login, pw)
    print("Authenticated as", login)

    configs = client.search_read(
        "pos.config",
        [],
        [
            "id",
            "name",
            "iface_customer_facing_display",
            "company_id",
            "pos_session_state",
            "currency_id",
        ],
        limit=50,
    )
    print("pos.config records:", json.dumps(configs, ensure_ascii=False))

    uoms = client.search_read("uom.uom", [], ["id", "name"], limit=10)
    print("UoM sample:", json.dumps(uoms, ensure_ascii=False))

    products = client.search_read(
        "product.product", [], ["id", "name", "uom_id"], limit=5
    )
    print("Product sample:", json.dumps(products, ensure_ascii=False))


if __name__ == "__main__":
    main()

