import json
import os
from odoo_jsonrpc import OdooClient, OdooRPCError


def load_config(path: str = "config.json") -> dict:
    if not os.path.exists(path):
        alt = os.path.join(os.path.dirname(__file__), "config.example.json")
        if not os.path.exists(alt):
            raise FileNotFoundError("Missing config file: create config.json or copy config.example.json")
        path = alt
        print(f"[info] Using example config: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    try:
        cfg = load_config()
        odoo_cfg = cfg.get("odoo")
        if not odoo_cfg:
            print("[error] 'odoo' section missing in config")
            return

        url = odoo_cfg.get("url")
        db = odoo_cfg.get("db")
        login = odoo_cfg.get("login")
        password = odoo_cfg.get("password")

        if not all([url, db, login, password]):
            print("[error] Odoo config is incomplete (url, db, login, password)")
            return

        client = OdooClient(url)

        print("[info] trying to connect to odoo server...")
        dbs = client.list_databases() or []
        if isinstance(dbs, dict) and dbs.get("databases"):
            dbs = dbs["databases"]

        print("[info] available databases:", dbs)
        if db not in dbs:
            print(f"[warn] target db '{db}' not found on server, please check config.json")
            # Fallback for demonstration
            if not dbs:
                print("[error] No databases found on server")
                return
            db = dbs[0]
            print(f"[info] falling back to first available db: {db}")

        print(f"[info] authenticating with db:'{db}' user:'{login}'")
        client.authenticate(db, login, password)
        me = client.search_read("res.users", [["login", "=", login]], ["id", "name", "login", "active"], limit=1)
        base_url = client.call_kw("ir.config_parameter", "get_param", [], {"key": "web.base.url"})

        print("[ok] login succeeded")
        print("  db:", db)
        print("  user:", me)
        print("  web.base.url:", base_url)

    except FileNotFoundError as e:
        print(f"[error] {e}")
    except OdooRPCError as e:
        print(f"[error] Odoo RPC error: {e}")
    except Exception as e:
        print(f"[error] an unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
