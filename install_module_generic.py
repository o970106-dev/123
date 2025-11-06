import argparse
from odoo_jsonrpc import OdooClient


def ensure_db(odoo: OdooClient, db: str | None) -> str:
    if db:
        return db
    dbs = odoo.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if not dbs:
        raise RuntimeError("No databases found on server")
    if len(dbs) > 1:
        raise RuntimeError(f"Multiple databases detected: {dbs}. Please specify --db")
    return dbs[0]


def main():
    ap = argparse.ArgumentParser(description="Install or upgrade an Odoo module generically")
    ap.add_argument("--url", required=True)
    ap.add_argument("--db")
    ap.add_argument("--login", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--module", required=True)
    ap.add_argument("--upgrade", action="store_true")
    ap.add_argument("--update-list", action="store_true")
    args = ap.parse_args()

    client = OdooClient(args.url)
    db = ensure_db(client, args.db)
    client.authenticate(db, args.login, args.password)

    if args.update_list:
        client.call_kw("ir.module.module", "update_list", [], {})

    mods = client.search_read("ir.module.module", [("name", "=", args.module)], ["id", "name", "state"], limit=1)
    if not mods:
        raise RuntimeError(f"Module {args.module} not found after update_list")
    mid = mods[0]["id"]
    state = mods[0]["state"]

    if args.upgrade and state == "installed":
        client.call_kw("ir.module.module", "button_immediate_upgrade", [[mid]], {})
        after = client.search_read("ir.module.module", [("id", "=", mid)], ["id", "name", "state"], limit=1)
        print("[done] upgraded:", after)
        return

    if state != "installed":
        client.call_kw("ir.module.module", "button_immediate_install", [[mid]], {})
        after = client.search_read("ir.module.module", [("id", "=", mid)], ["id", "name", "state"], limit=1)
        print("[done] installed:", after)
    else:
        print("[info] already installed:", mods)


if __name__ == "__main__":
    main()

