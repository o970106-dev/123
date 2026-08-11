from odoo_jsonrpc import OdooClient, OdooRPCError

from utils import load_config


def main():
    cfg = load_config()
    odoo_cfg = cfg.get("odoo", {})
    url = odoo_cfg.get("url")
    db = odoo_cfg.get("db")
    login = odoo_cfg.get("login")
    password = odoo_cfg.get("password")

    if not all([url, db, login, password]):
        print("[error] Odoo config missing in config.json (url, db, login, password)")
        return

    client = OdooClient(url)
    try:
        client.authenticate(db, login, password)
        me = client.search_read("res.users", [["login", "=", login]], ["id", "name", "login"], limit=1)
        print("[ok] Login successful")
        print("  - URL:", url)
        print("  - DB:", db)
        print("  - User:", me[0] if me else "N/A")
    except OdooRPCError as e:
        print(f"[error] Login failed: {e.fault_code} - {e.fault_string}")
    except Exception as e:
        print(f"[error] An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
