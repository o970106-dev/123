import json
import os
from odoo_jsonrpc import OdooClient, OdooRPCError


def load_config(path: str = "config.json") -> dict:
    if not os.path.exists(path):
        alt = os.path.join(os.path.dirname(__file__), "config.example.json")
        if not os.path.exists(alt):
            raise FileNotFoundError("Missing config file, please create config.json or keep config.example.json")
        path = alt
        print(f"[info] Using example config: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    try:
        cfg = load_config()
        url = cfg.get("odoo_url")
        db = cfg.get("odoo_db")
        user = cfg.get("odoo_user")
        password = cfg.get("odoo_password")

        if not all([url, db, user, password]):
            raise ValueError("Odoo config missing from config.json. Please add odoo_url, odoo_db, odoo_user, and odoo_password.")

        print(f"[info] connecting to {url}")
        client = OdooClient(url)
    except Exception as e:
        print(f"[error] Failed to load config or create client: {e}")
        return

    try:
        client.authenticate(db, user, password)
        me = client.search_read("res.users", [["login", "=", user]], ["id", "name", "login", "active"], limit=1)
        base_url = client.call_kw("ir.config_parameter", "get_param", [], {"key": "web.base.url"})
        print("[ok] login succeeded")
        print("db:", db)
        print("user:", me)
        print("web.base.url:", base_url)
    except Exception as e:
        print(f"[error] login failed for {user}:", str(e))


if __name__ == "__main__":
    main()
