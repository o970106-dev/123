import argparse
import requests


def create_db(base_url: str, master_pwd: str, db_name: str, admin_login: str, admin_password: str, lang: str = "zh_TW", demo: bool = False):
    base = base_url.rstrip("/")
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "id": 1,
        "params": {
            "master_pwd": master_pwd,
            "name": db_name,
            "demo": demo,
            "lang": lang,
            "login": admin_login,
            "password": admin_password,
        },
    }
    r = requests.post(f"{base}/web/database/create", json=payload, timeout=300)
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser(description="Create Odoo DB via JSON-RPC (supports custom admin login)")
    ap.add_argument("--url", required=True)
    ap.add_argument("--master", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--admin", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--lang", default="zh_TW")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    out = create_db(args.url, args.master, args.db, args.admin, args.password, args.lang, args.demo)
    print(out)


if __name__ == "__main__":
    main()
