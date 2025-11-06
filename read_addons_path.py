from odoo_jsonrpc import OdooClient


URL = "http://34.80.194.190"
LOGIN = "admin@wuchang.life"
PASSWORD = "poiuY926"


def main():
    client = OdooClient(URL)
    dbs = client.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if not dbs:
        raise RuntimeError("No databases returned")
    db = dbs[0]
    client.authenticate(db, LOGIN, PASSWORD)
    val = client.call_kw("ir.config_parameter", "get_param", [], {"key": "addons_path"})
    print("addons_path:", val)


if __name__ == "__main__":
    main()

