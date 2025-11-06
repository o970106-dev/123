from odoo_jsonrpc import OdooClient, OdooRPCError


URL = "http://34.80.194.190"
LOGIN = "admin@wuchang.line"
PASSWORD = "poiuY926"


def main():
    client = OdooClient(URL)
    dbs = client.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if not dbs:
        print("[error] No databases found on server")
        return
    db = dbs[0]
    try:
        client.authenticate(db, LOGIN, PASSWORD)
        me = client.search_read("res.users", [["login", "=", LOGIN]], ["id", "name", "login", "active"], limit=1)
        base_url = client.call_kw("ir.config_parameter", "get_param", [], {"key": "web.base.url"})
        print("[ok] login succeeded")
        print("db:", db)
        print("user:", me)
        print("web.base.url:", base_url)
    except OdooRPCError as e:
        print("[rpc_error]", str(e))
    except Exception as e:
        print("[error]", str(e))


if __name__ == "__main__":
    main()
