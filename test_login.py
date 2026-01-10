from odoo_jsonrpc import OdooClient


URL = "https://wuchang.life"
TARGET_DB = "wuchang_preview_20251107"

# Try common admin credential sets, first one that succeeds wins
CREDENTIALS = [
    ("admin", "odoo"),
    ("admin@wuchang.life", "poiuY926"),
]


def main():
    client = OdooClient(URL)
    dbs = client.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if not dbs:
        print("[error] No databases found on server")
        return
    print("[info] available databases:", dbs)
    db = TARGET_DB if TARGET_DB in dbs else dbs[0]
    print("[info] selected db:", db)

    last_err = None
    for login, password in CREDENTIALS:
        try:
            client.authenticate(db, login, password)
            me = client.search_read(
                "res.users", [["login", "=", login]],
                ["id", "name", "login", "active"], limit=1
            )
            base_url = client.call_kw(
                "ir.config_parameter", "get_param", [], {"key": "web.base.url"}
            )
            print("[ok] login succeeded")
            print("db:", db)
            print("user:", me)
            print("web.base.url:", base_url)
            return
        except Exception as e:
            last_err = e
            print(f"[warn] login failed for {login}:", str(e))

    if last_err:
        print("[error] all credential attempts failed:", str(last_err))


if __name__ == "__main__":
    main()
