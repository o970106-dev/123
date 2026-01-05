import json
import os
from odoo_jsonrpc import OdooClient, OdooRPCError

CONFIG_PATH = "config.json"
CONFIG_EXAMPLE_PATH = "config.example.json"

def get_config():
    """Reads config, showing guidance if it's missing or incomplete."""
    if not os.path.exists(CONFIG_PATH):
        print(f"[error] Config file not found: {CONFIG_PATH}")
        print(f"        Please copy {CONFIG_EXAMPLE_PATH} to {CONFIG_PATH} and fill in your details.")
        return None

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    if "odoo" not in config:
        print(f"[error] 'odoo' section missing in {CONFIG_PATH}")
        print(f"        Please check the structure against {CONFIG_EXAMPLE_PATH}.")
        return None

    return config["odoo"]

def main():
    """Main diagnostic script."""
    odoo_config = get_config()
    if not odoo_config:
        return

    url = odoo_config.get("url")
    db = odoo_config.get("db")
    login = odoo_config.get("login")
    password = odoo_config.get("password")

    if not all([url, db, login, password]):
        print("[error] Odoo config is missing one or more required fields: url, db, login, password")
        return

    print(f"[info] Connecting to Odoo at {url}")
    client = OdooClient(url)

    try:
        dbs = client.list_databases() or []
        if isinstance(dbs, dict) and dbs.get("databases"):
            dbs = dbs["databases"]

        if not dbs:
            print("[warn] No databases found on server, or server is slow to respond.")
        else:
            print("[info] Available databases:", dbs)
            if db not in dbs:
                print(f"[warn] Target database '{db}' not found in list from server.")
    except Exception as e:
        print(f"[error] Failed to list databases: {e}")
        return

    print(f"[info] Attempting to authenticate to database '{db}' with user '{login}'...")
    try:
        client.authenticate(db, login, password)
        me = client.search_read("res.users", [["login", "=", login]], ["id", "name", "login", "active"], limit=1)
        base_url = client.call_kw("ir.config_parameter", "get_param", [], {"key": "web.base.url"})

        print("[ok] Login Succeeded!")
        print(f"  - Database: {db}")
        print(f"  - User: {me}")
        print(f"  - Web Base URL: {base_url}")

    except OdooRPCError as e:
        print(f"[error] Odoo RPC Error during login: {e}")
    except Exception as e:
        print(f"[error] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
