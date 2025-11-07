import argparse
from odoo_jsonrpc import OdooClient


def main():
    ap = argparse.ArgumentParser(description="Quick login to a specific Odoo DB")
    ap.add_argument("--url", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--login", required=True)
    ap.add_argument("--password", required=True)
    args = ap.parse_args()

    client = OdooClient(args.url)
    dbs = client.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    print("[info] available databases:", dbs)
    client.authenticate(args.db, args.login, args.password)
    me = client.search_read("res.users", [["login", "=", args.login]], ["id", "name", "login", "active"], limit=1)
    print("[ok] login succeeded", me)


if __name__ == "__main__":
    main()

