import argparse
from datetime import datetime, date
from typing import Any, Dict, List, Optional

from odoo_jsonrpc import OdooClient


def ensure_db(odoo: OdooClient, db: Optional[str]) -> str:
    dbs = odoo.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if db:
        return db
    if not dbs:
        raise RuntimeError("No databases found on server")
    if len(dbs) > 1:
        # default to the first for this inspection, but warn
        return dbs[0]
    return dbs[0]


def parse_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


def fetch_menu_attachments(odoo: OdooClient, dt: Optional[date]) -> List[Dict[str, Any]]:
    fields = [
        "id",
        "name",
        "create_date",
        "write_date",
        "file_size",
        "mimetype",
        "store_fname",
        "checksum",
        "url",
        "res_model",
        "res_id",
        "type",
    ]
    names = ["menu", "菜單", "菜单"]
    all_records: Dict[int, Dict[str, Any]] = {}

    for nm in names:
        domain: List[Any] = [["type", "=", "binary"], ["name", "ilike", nm]]
        if dt:
            start = datetime(dt.year, dt.month, dt.day, 0, 0, 0).isoformat()
            end = datetime(dt.year, dt.month, dt.day, 23, 59, 59).isoformat()
            domain.extend([["write_date", ">=", start], ["write_date", "<=", end]])
        res = odoo.search_read("ir.attachment", domain, fields, limit=500) or []
        for r in res:
            all_records[r["id"]] = r

    return list(all_records.values())


def detect_corruption(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    bad: List[Dict[str, Any]] = []
    for r in records:
        fs = r.get("file_size") or 0
        store = r.get("store_fname")
        url = r.get("url")
        # binary attachment should have store_fname unless it's a URL attachment
        if (fs == 0 and not url) or (not store and not url):
            bad.append(r)
    return bad


def cron_info(odoo: OdooClient) -> List[Dict[str, Any]]:
    # Look for cleanup or auto vacuum jobs that might delete attachments
    jobs = odoo.search_read(
        "ir.cron",
        [["name", "ilike", "clean"], ["active", "=", True]],
        ["id", "name", "active", "nextcall", "interval_number", "interval_type"],
        limit=50,
    ) or []
    jobs += odoo.search_read(
        "ir.cron",
        [["name", "ilike", "vacuum"], ["active", "=", True]],
        ["id", "name", "active", "nextcall", "interval_number", "interval_type"],
        limit=50,
    ) or []
    return jobs


def main():
    ap = argparse.ArgumentParser(description="Inspect menu file history and retention in Odoo")
    ap.add_argument("--url", default="http://34.80.194.190")
    ap.add_argument("--db")
    ap.add_argument("--login", default="admin@wuchang.life")
    ap.add_argument("--password", default="poiuY926")
    ap.add_argument("--date", help="YYYY-MM-DD to filter attachments by write_date")
    args = ap.parse_args()

    dt = parse_date(args.date)
    client = OdooClient(args.url)
    db = ensure_db(client, args.db)
    client.authenticate(db, args.login, args.password)

    # Fetch menu-like attachments
    records = fetch_menu_attachments(client, dt)
    print(f"[info] attachments found: {len(records)} (db={db}, url={args.url})")
    if records:
        # Compute time range
        cds = [r.get("create_date") for r in records if r.get("create_date")]
        wds = [r.get("write_date") for r in records if r.get("write_date")]
        cds_sorted = sorted(cds)
        wds_sorted = sorted(wds)
        print(f"[range] create_date: {cds_sorted[0]} → {cds_sorted[-1]}" if cds_sorted else "[range] create_date: n/a")
        print(f"[range] write_date: {wds_sorted[0]} → {wds_sorted[-1]}" if wds_sorted else "[range] write_date: n/a")

        # Show a short list
        for r in records[:10]:
            print(
                f"- id={r['id']} name={r['name']} size={r.get('file_size')} mime={r.get('mimetype')} "
                f"write_date={r.get('write_date')} store={bool(r.get('store_fname'))} url={bool(r.get('url'))}"
            )

    # Detect corruption
    bad = detect_corruption(records)
    if bad:
        print(f"[warn] suspected corrupt/missing attachments: {len(bad)}")
        for r in bad[:10]:
            print(
                f"  * id={r['id']} name={r['name']} size={r.get('file_size')} store={r.get('store_fname')} url={r.get('url')}"
            )
    else:
        print("[ok] no obvious corrupt/missing attachments among matched records")

    # Cron cleanup jobs
    jobs = cron_info(client)
    if jobs:
        print("[cron] potential cleanup/vacuum jobs:")
        for j in jobs:
            print(
                f"  - id={j['id']} name={j['name']} next={j.get('nextcall')} interval={j.get('interval_number')} {j.get('interval_type')}"
            )
    else:
        print("[cron] no active cleanup/vacuum jobs detected by name")

    print("[hint] storage format: Odoo stores files as ir.attachment (DB records) with binary stored in filestore; not JSON/XML unless explicitly uploaded as such.")


if __name__ == "__main__":
    main()
