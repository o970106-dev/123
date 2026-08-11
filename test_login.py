import json
import os
from odoo_jsonrpc import OdooClient, OdooRPCError

def load_config(path: str) -> dict:
    """Safely loads a JSON config file, falling back to an example file."""
    if not os.path.exists(path):
        # Fallback to the example config if the main one doesn't exist
        alt_path = os.path.join(os.path.dirname(__file__), "config.example.json")
        if not os.path.exists(alt_path):
            raise FileNotFoundError("Config file not found. Please create 'config.json' or ensure 'config.example.json' is present.")
        print(f"[info] using example config: {alt_path}")
        path = alt_path

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    try:
        cfg = load_config("config.json")
        odoo_cfg = cfg.get("odoo")
        if not odoo_cfg:
            print("[error] 'odoo' section is missing from the config file.")
            return

        url = odoo_cfg.get("url")
        db = odoo_cfg.get("db")
        login = odoo_cfg.get("login")
        password = odoo_cfg.get("password")

        if not all([url, db, login, password]):
            print("[error] Incomplete Odoo config. 'url', 'db', 'login', and 'password' are required.")
            return

        client = OdooClient(url)

        print("[info] attempting to list databases...")
        dbs = client.list_databases() or []
        if isinstance(dbs, dict) and dbs.get("databases"):
            dbs = dbs["databases"]

        if not dbs:
            print("[warn] could not retrieve database list from server.")
        else:
            print("[info] available databases:", dbs)
            if db not in dbs:
                print(f"[warn] target db '{db}' not in server list.")

        print(f"[info] authenticating to db '{db}' with user '{login}'...")
        client.authenticate(db, login, password)

        me = client.search_read("res.users", [["login", "=", login]], ["id", "name", "login", "active"], limit=1)
        base_url = client.call_kw("ir.config_parameter", "get_param", [], {"key": "web.base.url"})

        print("\n[ok] login succeeded!")
        print("  db:", db)
        print("  user:", me)
        print("  web.base.url:", base_url)

    except (OdooRPCError, FileNotFoundError, KeyError) as e:
        print(f"\n[error] an error occurred: {e}")
    except Exception as e:
        print(f"\n[error] an unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
