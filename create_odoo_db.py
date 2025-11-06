import argparse
import requests


def create_db(base_url: str, master_pwd: str, db_name: str, admin_login: str, admin_password: str, lang: str = "zh_TW", demo: bool = False):
    url = f"{base_url.rstrip('/')}/web/database/create"
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "master_pwd": master_pwd,
            "db_name": db_name,
            "demo": demo,
            "login": admin_login,
            "password": admin_password,
            "lang": lang,
        },
    }
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(str(data["error"]))
    return data.get("result")


def main():
    ap = argparse.ArgumentParser(description="Create Odoo database via JSON-RPC")
    ap.add_argument("--url", required=True)
    ap.add_argument("--master", required=True, help="Odoo master password (ADMIN_PASSWORD)")
    ap.add_argument("--db", required=True, help="Database name to create")
    ap.add_argument("--admin", default="admin", help="Admin login")
    ap.add_argument("--password", required=True, help="Admin password")
    ap.add_argument("--lang", default="zh_TW")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    res = create_db(args.url, args.master, args.db, args.admin, args.password, args.lang, args.demo)
    print("[done] created db:", res)


if __name__ == "__main__":
    main()

