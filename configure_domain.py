from odoo_jsonrpc import OdooClient, OdooRPCError


URL = "http://34.80.194.190"
LOGIN = "admin@wuchang.line"
PASSWORD = "poiuY926"

PARAMS = {
    "web.base.url": "https://wuchang.life",
    "web.base.url.freeze": "True",
    "proxy_mode": "True",
}


def main():
    client = OdooClient(URL)
    dbs = client.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if not dbs:
        print("[error] No databases found on server")
        return
    db = dbs[0]
    client.authenticate(db, LOGIN, PASSWORD)

    before = {}
    for k in PARAMS.keys():
        try:
            before[k] = client.call_kw("ir.config_parameter", "get_param", [], {"key": k})
        except OdooRPCError as e:
            before[k] = f"<rpc_error:{str(e)}>"

    for k, v in PARAMS.items():
        client.call_kw("ir.config_parameter", "set_param", [], {"key": k, "value": v})

    after = {}
    for k in PARAMS.keys():
        try:
            after[k] = client.call_kw("ir.config_parameter", "get_param", [], {"key": k})
        except OdooRPCError as e:
            after[k] = f"<rpc_error:{str(e)}>"

    print("db:", db)
    print("before:", before)
    print("after:", after)


if __name__ == "__main__":
    main()

