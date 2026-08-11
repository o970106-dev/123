import json
from pathlib import Path
from typing import Any, Dict

from odoo_jsonrpc import OdooClient, OdooRPCError


def load_config() -> Dict[str, Any]:
    """Loads config.json, falling back to the example."""
    config_path = Path("config.json")
    if not config_path.exists():
        print("[warn] config.json not found, using config.example.json")
        config_path = Path("config.example.json")
    if not config_path.exists():
        print("[error] No config file found. Please create config.json.")
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def main():
    """Runs a series of checks against the configured Odoo instance."""
    config = load_config()
    odoo_cfg = config.get("odoo")
    if not odoo_cfg:
        print("[error] 'odoo' section missing in config file.")
        return

    url = odoo_cfg.get("url")
    db = odoo_cfg.get("db")
    login = odoo_cfg.get("login")
    password = odoo_cfg.get("password")

    if not all([url, db, login, password]):
        print("[error] url, db, login, and password must be set in config.")
        return

    print(f"[*] Connecting to Odoo at {url}...")
    client = OdooClient(url)

    # 1. Check database listing
    try:
        dbs = client.list_databases() or []
        print(f"[ok] Successfully listed databases: {dbs}")
        if db not in dbs:
            print(f"[warn] Target DB '{db}' not in list.")
    except Exception as e:
        print(f"[fail] Could not list databases: {e}")
        return

    # 2. Check authentication
    try:
        uid = client.authenticate(db, login, password)
        print(f"[ok] Authenticated successfully. UID: {uid}")
    except OdooRPCError as e:
        print(f"[fail] Authentication failed: {e}")
        return
    except Exception as e:
        print(f"[fail] An unexpected error occurred during authentication: {e}")
        return

    # 3. Check basic data fetching
    try:
        base_url = client.call_kw("ir.config_parameter", "get_param", [], {"key": "web.base.url"})
        print(f"[ok] Fetched web.base.url: {base_url}")
    except OdooRPCError as e:
        print(f"[fail] Could not fetch system parameter: {e}")

    # 4. Check for custom model used by import script
    try:
        model_data = client.search_read(
            "ir.model", [["model", "=", "pos.beverage.config"]], ["id", "name"], limit=1
        )
        if model_data:
            print(f"[ok] Custom model 'pos.beverage.config' is available.")
        else:
            print("[warn] Custom model 'pos.beverage.config' not found. Imports may fail.")
    except OdooRPCError as e:
        print(f"[fail] Could not check for custom model: {e}")

    print("\n[info] Diagnosis complete.")


if __name__ == "__main__":
    main()
