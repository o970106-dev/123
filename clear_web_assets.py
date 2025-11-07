from typing import List, Dict

from odoo_jsonrpc import OdooClient, OdooRPCError


URL = "http://127.0.0.1:18069"
DB = "wuchang_preview_20251107"
LOGIN = "admin@wuchang.life"
PASSWORD = "poiuY926"


def main():
    client = OdooClient(URL)
    client.authenticate(DB, LOGIN, PASSWORD)

    # Clear various server-side caches that affect asset building
    try:
        client.call_kw("ir.qweb", "clear_caches", [], {})
    except OdooRPCError:
        pass
    try:
        client.call_kw("ir.ui.view", "clear_caches", [], {})
    except OdooRPCError:
        pass
    try:
        client.call_kw("ir.http", "clear_caches", [], {})
    except OdooRPCError:
        pass

    # Remove previously built asset attachments so Odoo rebuilds them
    attachments: List[Dict] = client.search_read(
        "ir.attachment",
        [["url", "ilike", "/web/assets/"], ["type", "=", "binary"]],
        ["id", "name", "url"],
        limit=2000,
    ) or []
    if attachments:
        ids = [a["id"] for a in attachments]
        try:
            client.call_kw("ir.attachment", "unlink", [ids], {})
            print(f"[done] removed {len(ids)} asset attachments; assets will rebuild on next load")
        except OdooRPCError as e:
            print("[warn] failed to unlink assets:", e)
    else:
        print("[info] no prebuilt asset attachments found to remove")

    print("[ok] caches cleared. Please refresh login page or try incognito.")


if __name__ == "__main__":
    main()

