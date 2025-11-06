from odoo_jsonrpc import OdooClient, OdooRPCError


URL = "http://34.80.194.190"
OLD_LOGIN = "admin@wuchang.life"
PASSWORD = "poiuY926"
NEW_LOGIN = "admin@wuchang.line"


def main():
    client = OdooClient(URL)
    dbs = client.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if not dbs:
        print("[error] No databases found on server")
        return
    db = dbs[0]
    client.authenticate(db, OLD_LOGIN, PASSWORD)

    # If new login already exists, just report
    exists = client.search_read("res.users", [["login", "=", NEW_LOGIN]], ["id", "name", "active"], limit=1)
    if exists:
        print("[info] target login already exists:", exists)
        return

    users = client.search_read("res.users", [["login", "=", OLD_LOGIN]], ["id", "name", "login", "active"], limit=1)
    if not users:
        print("[error] old admin login not found:", OLD_LOGIN)
        return
    uid = users[0]["id"]
    # Update login and email (optional)
    client.call_kw("res.users", "write", [[uid], {"login": NEW_LOGIN, "email": NEW_LOGIN}], {})
    updated = client.search_read("res.users", [["id", "=", uid]], ["id", "name", "login", "email"], limit=1)
    print("[ok] updated:", updated)


if __name__ == "__main__":
    main()
