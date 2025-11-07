import sys
import argparse
from typing import Optional

from odoo_jsonrpc import OdooClient, OdooRPCError


# Defaults for local shadow stack; can be overridden via CLI args
DEFAULT_URL = "http://127.0.0.1:18069"
DEFAULT_LOGIN = "admin"
DEFAULT_PASSWORD = "odoo"
DEFAULT_PRODUCT = "招牌咖啡"
DEFAULT_POS_CATEGORY = "飲品"


def ensure_db(client: OdooClient, db_arg: Optional[str] = None) -> str:
    if db_arg:
        return db_arg
    dbs = client.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if not dbs:
        raise RuntimeError("No databases returned")
    if len(dbs) > 1:
        # pick the first for now; in production, pass explicitly
        print(f"[warn] Multiple databases detected: {dbs}. Using first.")
    return dbs[0]


def ensure_pos_config(client: OdooClient) -> int:
    configs = client.search_read(
        "pos.config",
        [],
        ["id", "name", "company_id", "currency_id"],
        limit=1,
    )
    if configs:
        cfg_id = configs[0]["id"]
        # ensure currency
        if not configs[0].get("currency_id"):
            companies = client.search_read("res.company", [], ["id", "currency_id"], limit=1)
            if companies:
                curr = companies[0].get("currency_id")
                curr_id = curr[0] if isinstance(curr, list) and curr else None
                if curr_id:
                    client.write("pos.config", [cfg_id], {"currency_id": curr_id})
        return cfg_id

    # create minimal config
    companies = client.search_read("res.company", [], ["id", "currency_id"], limit=1)
    if not companies:
        raise RuntimeError("No res.company found")
    company_id = companies[0]["id"]
    curr = companies[0].get("currency_id")
    curr_id = curr[0] if isinstance(curr, list) and curr else None
    vals = {
        "name": "主 POS",
        "company_id": company_id,
    }
    if curr_id:
        vals["currency_id"] = curr_id
    cfg_id = client.create("pos.config", vals)
    return cfg_id


def open_pos_session(client: OdooClient, cfg_id: int) -> Optional[int]:
    # try to find opened session
    sessions = client.search_read(
        "pos.session",
        [["config_id", "=", cfg_id], ["state", "=", "opened"]],
        ["id", "name", "state"],
        limit=1,
    )
    if sessions:
        return sessions[0]["id"]

    # find any existing session
    sessions = client.search_read(
        "pos.session",
        [["config_id", "=", cfg_id]],
        ["id", "name", "state"],
        limit=1,
    )
    sid = None
    if sessions:
        sid = sessions[0]["id"]
    else:
        # create a fresh session
        try:
            sid = client.create("pos.session", {"config_id": cfg_id})
        except OdooRPCError as e:
            print(f"[warn] create pos.session failed: {e}")

    if sid:
        try:
            client.call_kw("pos.session", "action_pos_session_open", [[sid]], {})
        except OdooRPCError as e:
            print(f"[warn] action_pos_session_open failed: {e}")
        return sid
    return None


def ensure_pos_category(client: OdooClient, name: str) -> int:
    cats = client.search_read("pos.category", [["name", "=", name]], ["id"], limit=1)
    if cats:
        return cats[0]["id"]
    return client.create("pos.category", {"name": name})


def ensure_product_for_pos(client: OdooClient, name: str, pos_category_name: Optional[str] = None) -> int:
    tmpls = client.search_read(
        "product.template",
        [["name", "=", name]],
        ["id", "name", "uom_id", "available_in_pos", "type", "sale_ok"],
        limit=1,
    )
    if not tmpls:
        # create minimal template
        # pick a reasonable UoM first, then create
        candidates = ["Units", "Unit", "個", "件", "pcs"]
        uom = None
        for nm in candidates:
            res = client.search_read(
                "uom.uom",
                [["name", "ilike", nm]],
                ["id", "name"],
                limit=1,
            )
            if res:
                uom = res[0]
                break
        if not uom:
            res = client.search_read(
                "uom.uom",
                [],
                ["id", "name"],
                limit=1,
            )
            if res:
                uom = res[0]
        vals = {
            "name": name,
            "available_in_pos": True,
            "sale_ok": True,
            "type": "consu",
        }
        if uom:
            vals["uom_id"] = uom["id"]
        pid = client.create("product.template", vals)
        print(f"[info] created product.template id={pid} name='{name}'")
        tmpls = client.search_read(
            "product.template",
            [["id", "=", pid]],
            ["id", "name", "uom_id", "available_in_pos", "type", "sale_ok"],
            limit=1,
        )
    tmpl = tmpls[0]
    # pick a reasonable UoM
    candidates = ["Units", "Unit", "個", "件", "pcs"]
    uom = None
    for nm in candidates:
        res = client.search_read(
            "uom.uom",
            [["name", "ilike", nm]],
            ["id", "name"],
            limit=1,
        )
        if res:
            uom = res[0]
            break
    if not uom:
        res = client.search_read(
            "uom.uom",
            [],
            ["id", "name"],
            limit=1,
        )
        if res:
            uom = res[0]

    updates = {}
    if not tmpl.get("uom_id") and uom:
        updates["uom_id"] = uom["id"]
    if not tmpl.get("available_in_pos"):
        updates["available_in_pos"] = True
    # ensure type/sale_ok for POS visibility
    if not tmpl.get("type"):
        updates["type"] = "consu"
    if not tmpl.get("sale_ok"):
        updates["sale_ok"] = True
    if updates:
        client.write("product.template", [tmpl["id"]], updates)
    # clear attribute lines to avoid variant explosion
    try:
        client.write("product.template", [tmpl["id"]], {"attribute_line_ids": [(5, 0, 0)]})
    except OdooRPCError as e:
        print(f"[warn] clear attribute lines failed: {e}")

    # set POS category if requested
    if pos_category_name:
        cat_id = ensure_pos_category(client, pos_category_name)
        try:
            client.write("product.template", [tmpl["id"]], {"pos_categ_ids": [(6, 0, [cat_id])]})
        except OdooRPCError:
            try:
                client.write("product.template", [tmpl["id"]], {"pos_category_id": cat_id})
            except OdooRPCError as e2:
                print(f"[warn] set POS category failed: {e2}")
    return tmpl["id"]


def main():
    ap = argparse.ArgumentParser(description="Ensure POS config/session and make a product visible in POS")
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--login", default=DEFAULT_LOGIN)
    ap.add_argument("--password", default=DEFAULT_PASSWORD)
    ap.add_argument("--db")
    ap.add_argument("--product", default=DEFAULT_PRODUCT)
    ap.add_argument("--pos-category", dest="pos_category", default=DEFAULT_POS_CATEGORY)
    args = ap.parse_args()

    client = OdooClient(args.url)
    db = ensure_db(client, args.db)
    client.authenticate(db, args.login, args.password)

    print(f"[info] Authenticated to {args.url} db={db} as {args.login}")

    cfg_id = ensure_pos_config(client)
    print(f"[info] pos.config id={cfg_id}")

    sid = open_pos_session(client, cfg_id)
    print(f"[info] pos.session id={sid}")

    pid = ensure_product_for_pos(client, args.product, args.pos_category)
    print(f"[info] product.template id={pid} ensured for POS (category='{args.pos_category}')")

    print("[done] POS 基本配置與會話已嘗試開啟，產品可用於 POS 且具備 UoM。")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[error] {e}")
        sys.exit(1)
