from odoo_jsonrpc import OdooClient, OdooRPCError
import sys
import json
import os

CONFIG_FILE = "config.json"

def load_config():
    """Loads Odoo configuration from config.json."""
    if not os.path.exists(CONFIG_FILE):
        print(f"[error] Configuration file '{CONFIG_FILE}' not found.")
        print(f"[info] Please copy 'config.example.json' to '{CONFIG_FILE}' and fill in your details.")
        sys.exit(1)

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    if "odoo" not in config:
        print(f"[error] 'odoo' section is missing in '{CONFIG_FILE}'.")
        sys.exit(1)

    required_keys = ["url", "db", "login", "password"]
    for key in required_keys:
        if key not in config["odoo"] or not config["odoo"][key]:
            print(f"[error] Missing or empty value for required key '{key}' in the 'odoo' section of '{CONFIG_FILE}'.")
            sys.exit(1)

    return config["odoo"]

def main():
    """
    Connects to the Odoo server using credentials from config.json,
    authenticates, and prints basic system information.
    """
    config = load_config()
    url = config["url"]
    db = config["db"]
    login = config["login"]
    password = config["password"]

    print(f"[info] Connecting to Odoo server at {url}")
    client = OdooClient(url)

    try:
        # 1. Verify the target database exists on the server
        dbs = client.list_databases() or []
        if isinstance(dbs, dict) and dbs.get("databases"):
            dbs = dbs["databases"]

        if not dbs:
            print("[error] No databases found on the server.")
            sys.exit(1)

        print(f"[info] Available databases: {dbs}")

        if db not in dbs:
            print(f"[error] The specified database '{db}' was not found on the server.")
            print(f"[info] Please check the 'db' value in '{CONFIG_FILE}'.")
            sys.exit(1)

        print(f"[info] Attempting to authenticate to database: '{db}'")

        # 2. Authenticate
        client.authenticate(db, login, password)
        print("[ok] Authentication successful!")

        # 3. Get user info
        user_info = client.search_read(
            "res.users",
            [["login", "=", login]],
            ["id", "name", "login", "active"],
            limit=1
        )
        print(f"[info] Logged in as: {user_info}")

        # 4. Get a system parameter as a health check
        base_url = client.call_kw(
            "ir.config_parameter", "get_param", [], {"key": "web.base.url"}
        )
        print(f"[info] System parameter 'web.base.url': {base_url}")

        print("\n[success] Odoo system check passed.")

    except OdooRPCError as e:
        print(f"\n[error] An Odoo RPC error occurred: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[error] An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
