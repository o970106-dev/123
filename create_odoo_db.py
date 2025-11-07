import argparse
import requests


def create_db(base_url: str, master_pwd: str, db_name: str, admin_login: str, admin_password: str, lang: str = "zh_TW", demo: bool = False):
    base = base_url.rstrip('/')
    url = f"{base}/web/database/create"
    s = requests.Session()
    # fetch CSRF token
    s.get(f"{base}/web", timeout=30)
    csrf = s.cookies.get('csrf_token')
    # Odoo 19 expects form fields: master_pwd, name, lang, password, login, demo, csrf_token
    payload = {
        "master_pwd": master_pwd,
        "name": db_name,
        "demo": str(demo).lower(),
        "login": admin_login,
        "password": admin_password,
        "lang": lang,
        "csrf_token": csrf or "",
    }
    resp = s.post(url, data=payload, timeout=180)
    resp.raise_for_status()
    # When using form data, success returns HTML; we can return status code.
    return resp.status_code


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

