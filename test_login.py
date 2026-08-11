from odoo_jsonrpc import OdooClient, OdooRPCError
from shared_config import load_config


def main():
    config = load_config()
    odoo_config = config.get('odoo', {})

    url = odoo_config.get('url')
    db = odoo_config.get('db')
    login = odoo_config.get('login')
    password = odoo_config.get('password')

    if not all([url, db, login, password]):
        print("[error] Odoo configuration is missing in config.json")
        return

    client = OdooClient(url)
    try:
        dbs = client.list_databases() or []
        if isinstance(dbs, dict) and dbs.get("databases"):
            dbs = dbs["databases"]
        if not dbs:
            print("[error] No databases found on server")
            return
        print("[info] available databases:", dbs)

        if db not in dbs:
            print(f"[warn] Target database '{db}' not found on server. Using the first one found: '{dbs[0]}'")
            db = dbs[0]

        print("[info] selected db:", db)

        client.authenticate(db, login, password)
        me = client.search_read("res.users", [["login", "=", login]], ["id", "name", "login", "active"], limit=1)
        base_url = client.call_kw("ir.config_parameter", "get_param", [], {"key": "web.base.url"})

        print("[ok] login succeeded")
        print("db:", db)
        print("user:", me)
        print("web.base.url:", base_url)

    except Exception as e:
        print(f"[error] An error occurred: {e}")


if __name__ == "__main__":
    main()
