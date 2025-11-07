import argparse
from odoo_jsonrpc import OdooClient, OdooRPCError


def main():
    ap = argparse.ArgumentParser(description="Set admin login/email and password on a specific DB")
    ap.add_argument("--url", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--login", required=True, help="Target admin login to set (e.g., admin@domain)")
    ap.add_argument("--password", required=True, help="New password to set")
    ap.add_argument("--auth-login", help="Current admin login for authentication")
    ap.add_argument("--auth-password", help="Current admin password for authentication")
    args = ap.parse_args()

    client = OdooClient(args.url)

    # Prefer authenticating with provided credentials; fallback to default admin/odoo
    auth_login = args.auth_login or args.login
    auth_password = args.auth_password or args.password
    try:
        client.authenticate(args.db, auth_login, auth_password)
    except Exception:
        # Try legacy default
        client.authenticate(args.db, "admin", "odoo")

    # Find Administrator (id usually 2)
    user = client.search_read("res.users", [["id", "=", 2]], ["id", "name", "login", "partner_id"], limit=1)
    if not user:
        raise RuntimeError("Administrator user not found")
    uid = user[0]["id"]
    partner_id = user[0].get("partner_id") and user[0]["partner_id"][0]

    # Update login and password
    client.write("res.users", [uid], {"login": args.login, "password": args.password})
    if partner_id:
        client.write("res.partner", [partner_id], {"email": args.login})
    print({"status": "ok", "user_id": uid, "new_login": args.login})


if __name__ == "__main__":
    main()
