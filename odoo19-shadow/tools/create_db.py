import requests
import sys

def create_db(base: str, master_pwd: str, name: str, admin_login: str, admin_password: str, lang: str = "zh_TW"):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "master_pwd": master_pwd,
            "name": name,
            "demo": False,
            "lang": lang,
            "login": admin_login,
            "password": admin_password,
        },
    }
    r = requests.post(base + "/web/database/create", json=payload, timeout=300)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18069"
    name = sys.argv[2] if len(sys.argv) > 2 else "wuchang_shadow19"
    out = create_db(base, "odoo", name, "admin", "odoo")
    print(out)
