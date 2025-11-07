import argparse
from odoo_jsonrpc import OdooClient


def main():
    ap = argparse.ArgumentParser(description="Install POS Restaurant (floors/tables) module")
    ap.add_argument("--url", default="http://127.0.0.1:18069")
    ap.add_argument("--db", default="wuchang_preview_20251107")
    ap.add_argument("--login", default="admin@wuchang.life")
    ap.add_argument("--password", default="poiuY926")
    args = ap.parse_args()

    modules = [
        "point_of_sale",
        "pos_restaurant",
        # keep beverage modifier if present in addons path
        "pos_beverage_modifier",
    ]

    client = OdooClient(args.url)
    client.authenticate(args.db, args.login, args.password)

    # update app list
    client.call_kw("ir.module.module", "update_list", [], {})

    for module_name in modules:
        mods = client.search_read(
            "ir.module.module", [("name", "=", module_name)], ["id", "name", "state"], limit=1
        )
        if not mods:
            print(f"[warn] module {module_name} not found after update_list")
            continue
        mid = mods[0]["id"]
        st = mods[0]["state"]
        if st != "installed":
            print(f"Installing module: {module_name}")
            client.call_kw("ir.module.module", "button_immediate_install", [[mid]], {})
            after = client.search_read(
                "ir.module.module", [("id", "=", mid)], ["id", "name", "state"], limit=1
            )
            print("Installed module state:", after)
        else:
            print(f"Module already installed: {module_name}")

    print("Done: pos_restaurant installed (if available) and POS ready.")


if __name__ == "__main__":
    main()

