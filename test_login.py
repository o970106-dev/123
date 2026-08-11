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
        raise FileNotFoundError("config.json or config.example.json not found.")
    return json.loads(config_path.read_text(encoding="utf-8"))


def main():
    """Attempts to authenticate to Odoo using credentials from config."""
    try:
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
            print("[error] url, db, login, and password must be set in the 'odoo' config section.")
            return

        client = OdooClient(url)
        print(f"[*] Authenticating to {url} with db='{db}' and user='{login}'...")
        uid = client.authenticate(db, login, password)
        me = client.search_read("res.users", [["id", "=", uid]], ["name", "login"], limit=1)

        print("\n[ok] Login successful!")
        print(f"  - UID: {uid}")
        print(f"  - User: {me[0]['name']} ({me[0]['login']})")

    except FileNotFoundError as e:
        print(f"[error] {e}")
    except OdooRPCError as e:
        print(f"\n[fail] Odoo RPC Error: {e}")
    except Exception as e:
        print(f"\n[fail] An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
