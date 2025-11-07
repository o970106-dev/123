from typing import Optional

from odoo_jsonrpc import OdooClient, OdooRPCError


URL = "http://127.0.0.1:18069"
DB = "wuchang_preview_20251107"
LOGIN = "admin@wuchang.life"
PW = "poiuY926"


def open_pos_session(client: OdooClient, cfg_id: int) -> Optional[int]:
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
            return sid
        except OdooRPCError as e:
            print(f"[warn] action_pos_session_open failed: {e}")
    return None


def main() -> None:
    client = OdooClient(URL)
    client.authenticate(DB, LOGIN, PW)
    cfgs = client.search_read("pos.config", [], ["id", "name", "company_id", "currency_id"], limit=1) or []
    if not cfgs:
        print("[error] No pos.config found. Install POS module and create a POS config first.")
        return
    cfg_id = cfgs[0]["id"]
    sid = open_pos_session(client, cfg_id)
    if sid:
        print(f"[ok] POS session opened id={sid} config_id={cfg_id}")
    else:
        print("[error] Unable to open POS session.")


if __name__ == "__main__":
    main()

