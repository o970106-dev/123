import json
import os
from odoo_jsonrpc import OdooClient, OdooRPCError


def load_config():
    """Loads configuration from config.json or falls back to config.example.json."""
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"[warn] '{config_path}' not found. Falling back to 'config.example.json'.")
        print("Please copy 'config.example.json' to 'config.json' and fill in your actual credentials.")
        config_path = "config.example.json"

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    config = load_config().get("odoo", {})
    if not config.get("url"):
        print("[error] Odoo URL not found in config. Please check your config.json.")
        return

    url = config["url"]
    target_db = config.get("db")
    login = config.get("login")
    password = config.get("password")

    if not all([target_db, login, password]):
        print("[error] Missing Odoo db, login, or password in config.")
        return

    try:
        client = OdooClient(url)
        dbs = client.list_databases() or []
        if isinstance(dbs, dict) and dbs.get("databases"):
            dbs = dbs["databases"]

        if not dbs:
            print("[error] No databases found on server")
            return

        print("[info] available databases:", dbs)

        if target_db not in dbs:
            print(f"[error] Target DB '{target_db}' not found in available databases.")
            # Optionally, fallback to the first DB
            # db = dbs[0]
            # print(f"[info] Falling back to first available db: {db}")
            return

        db = target_db
        print("[info] selected db:", db)

        client.authenticate(db, login, password)
        me = client.search_read("res.users", [["login", "=", login]], ["id", "name", "login", "active"], limit=1)
        base_url = client.call_kw("ir.config_parameter", "get_param", [], {"key": "web.base.url"})

        print("[ok] login succeeded")
        print("  db:", db)
        print("  user:", me)
        print("  web.base.url:", base_url)

    except OdooRPCError as e:
        print(f"[error] Odoo RPC error: {e.fault_code} - {e.fault_string}")
    except Exception as e:
        print(f"[error] An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
