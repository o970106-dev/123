import argparse
import json
from typing import Any, Dict, List, Optional

from odoo_jsonrpc import OdooClient, OdooRPCError


def read_main_items(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in ("items", "products", "menu", "data"):
            if k in data and isinstance(data[k], list):
                return data[k]
    return []


def find_product(odoo: OdooClient, name: str, sku: Optional[str]) -> Optional[Dict[str, Any]]:
    if sku:
        res = odoo.search_read(
            "product.template",
            [["default_code", "=", sku]],
            ["id", "name", "default_code", "list_price", "available_in_pos", "categ_id"],
            limit=1,
        )
        if res:
            return res[0]
    res = odoo.search_read(
        "product.template",
        [["name", "=", name]],
        ["id", "name", "default_code", "list_price", "available_in_pos", "categ_id"],
        limit=1,
    )
    return res[0] if res else None


def main() -> None:
    ap = argparse.ArgumentParser(description="Update list_price from main_items.json (use price_m only)")
    ap.add_argument("--file", default="main_items.json", help="Path to main_items.json")
    ap.add_argument("--apply", action="store_true", help="Apply changes to Odoo (default: dry-run)")
    ap.add_argument("--url", default="http://127.0.0.1:18069", help="Odoo base URL")
    ap.add_argument("--login", default="admin@wuchang.life", help="Odoo login")
    ap.add_argument("--password", default="poiuY926", help="Odoo password")
    ap.add_argument("--db", default="wuchang_preview_20251107", help="Database name")
    # Categories that should update price only (same behavior for all items here)
    ap.add_argument(
        "--price-only-categories",
        nargs="*",
        default=["簡餐", "手沖咖啡", "咖啡豆", "濾掛咖啡"],
        help="Categories that we explicitly only set price for",
    )
    args = ap.parse_args()

    items = read_main_items(args.file)
    if not items:
        print("[error] No items parsed from", args.file)
        return

    client = OdooClient(args.url)
    client.authenticate(args.db, args.login, args.password)

    updated = 0
    skipped_no_price = 0
    not_found = 0
    preview = 0

    for it in items:
        name = str(it.get("name") or "").strip()
        if not name:
            continue
        sku = it.get("sku") or None
        price_m = it.get("price_m")
        category_name = str(it.get("pos_category_name") or it.get("category") or "").strip()

        if price_m is None:
            skipped_no_price += 1
            print(f"[skip] no price_m in main_items: name={name} sku={sku}")
            continue

        p = find_product(client, name, sku)
        if not p:
            not_found += 1
            print(f"[warn] product not found: name={name} sku={sku}")
            continue

        if not args.apply:
            preview += 1
            print(f"[dry-run] set list_price={price_m}: id={p['id']} name={name} category={category_name}")
            continue

        try:
            client.write("product.template", [p["id"]], {"list_price": price_m})
            updated += 1
            print(f"[ok] updated list_price={price_m}: id={p['id']} name={name}")
        except OdooRPCError as e:
            print(f"[error] write failed: id={p['id']} name={name} err={e}")

    if args.apply:
        print(f"[summary] updated={updated} skipped_no_price={skipped_no_price} not_found={not_found}")
    else:
        print(f"[summary] dry-run count={preview} skipped_no_price={skipped_no_price} not_found={not_found}")


if __name__ == "__main__":
    main()

