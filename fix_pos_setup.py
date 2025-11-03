import sys
from typing import Optional

from odoo_jsonrpc import OdooClient, OdooRPCError


URL = "http://34.80.194.190"
LOGIN = "admin@wuchang.life"
PASSWORD = "poiuY926"


def ensure_db(client: OdooClient) -> str:
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
        ["id", "name", "company_id", "currency_id", "iface_customer_facing_display"],
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
        "iface_customer_facing_display": False,
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

    # attempt to open via pos.config method
    try:
        client.call_kw("pos.config", "open_session_cb", [[cfg_id]], {})
    except OdooRPCError as e:
        print(f"[warn] open_session_cb failed: {e}")

    sessions = client.search_read(
        "pos.session",
        [["config_id", "=", cfg_id]],
        ["id", "name", "state"],
        limit=1,
    )
    if sessions:
        sid = sessions[0]["id"]
        state = sessions[0]["state"]
        if state != "opened":
            try:
                client.call_kw("pos.session", "action_pos_session_open", [[sid]], {})
            except OdooRPCError as e:
                print(f"[warn] action_pos_session_open failed: {e}")
        return sid
    return None


def ensure_product_for_pos(client: OdooClient, name: str) -> int:
    tmpls = client.search_read(
        "product.template",
        [["name", "=", name]],
        ["id", "name", "uom_id", "available_in_pos"],
        limit=1,
    )
    if not tmpls:
        raise RuntimeError(f"Product template {name} not found")
    tmpl = tmpls[0]
    # pick a reasonable UoM
    candidates = ["Units", "Unit", "個", "件", "pcs"]
    uom = None
    for nm in candidates:
        res = client.search_read(
            "uom.uom",
            [["name", "ilike", nm]],
            ["id", "name", "uom_type", "category_id"],
            limit=1,
        )
        if res:
            uom = res[0]
            break
    if not uom:
        res = client.search_read(
            "uom.uom",
            [["uom_type", "=", "reference"]],
            ["id", "name", "uom_type", "category_id"],
            limit=1,
        )
        if res:
            uom = res[0]

    updates = {}
    if not tmpl.get("uom_id") and uom:
        updates["uom_id"] = uom["id"]
    if not tmpl.get("available_in_pos"):
        updates["available_in_pos"] = True
    if updates:
        client.write("product.template", [tmpl["id"]], updates)
    return tmpl["id"]


def main():
    client = OdooClient(URL)
    db = ensure_db(client)
    client.authenticate(db, LOGIN, PASSWORD)

    print(f"[info] Authenticated to {URL} db={db} as {LOGIN}")

    cfg_id = ensure_pos_config(client)
    print(f"[info] pos.config id={cfg_id}")

    sid = open_pos_session(client, cfg_id)
    print(f"[info] pos.session id={sid}")

    pid = ensure_product_for_pos(client, "招牌咖啡")
    print(f"[info] product.template id={pid} ensured for POS")

    print("[done] POS 基本配置與會話已嘗試開啟，產品可用於 POS 且具備 UoM。")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[error] {e}")
        sys.exit(1)

