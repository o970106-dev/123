from odoo_jsonrpc import OdooClient


URL = "http://127.0.0.1:18069"
DB = "wuchang_preview_20251107"
LOGIN = "admin"
PW = "odoo"


def main():
    client = OdooClient(URL)
    client.authenticate(DB, LOGIN, PW)
    # Administrator is typically id=2
    users = client.search_read("res.users", [["id", "=", 2]], ["id", "name", "login", "email", "active"], limit=1)
    print("admin_user:", users)


if __name__ == "__main__":
    main()

