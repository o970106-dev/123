import argparse
import json
from typing import Any, Dict, List, Optional, Tuple

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


def ensure_pos_category(odoo: OdooClient, name: str) -> Optional[int]:
    try:
        cats = odoo.search_read("pos.category", [["name", "=", name]], ["id"], limit=1)
        if cats:
            return cats[0]["id"]
        return odoo.create("pos.category", {"name": name})
    except OdooRPCError:
        # POS module might not be installed; skip category assignment
        return None


def resolve_pos_category_field(odoo: OdooClient) -> Optional[str]:
    # Detect available field name across Odoo versions
    try:
        fields = odoo.call_kw("product.template", "fields_get", [], {"attributes": ["string"]}) or {}
    except OdooRPCError:
        fields = {}
    if "pos_category_id" in fields:
        return "pos_category_id"
    if "pos_categ_id" in fields:
        return "pos_categ_id"
    return None


def find_existing_product(odoo: OdooClient, name: str, sku: Optional[str]) -> Optional[Dict[str, Any]]:
    # Prefer matching by default_code (SKU), fallback to exact name
    if sku:
        res = odoo.search_read(
            "product.template",
            [["default_code", "=", sku]],
            ["id", "name", "default_code", "list_price", "available_in_pos"],
            limit=1,
        )
        if res:
            return res[0]
    res = odoo.search_read(
        "product.template",
        [["name", "=", name]],
        ["id", "name", "default_code", "list_price", "available_in_pos"],
        limit=1,
    )
    return res[0] if res else None


def build_vals(
    name: str,
    price_m: Optional[float],
    sku: Optional[str],
    pos_category_field: Optional[str],
    pos_category_id: Optional[int],
) -> Dict[str, Any]:
    vals: Dict[str, Any] = {
        "name": name,
        "sale_ok": True,
        "available_in_pos": True,
        "type": "consu",
    }
    if price_m is not None:
        vals["list_price"] = price_m
    if sku:
        vals["default_code"] = sku
    if pos_category_field and pos_category_id:
        vals[pos_category_field] = pos_category_id
    return vals


def create_or_update_product(
    odoo: OdooClient,
    name: str,
    price_m: Optional[float],
    sku: Optional[str],
    category_name: Optional[str],
    update_existing: bool,
) -> Tuple[int, str]:
    pos_category_field = resolve_pos_category_field(odoo)
    cat_id = ensure_pos_category(odoo, category_name) if category_name else None

    existing = find_existing_product(odoo, name, sku)
    if existing:
        pid = existing["id"]
        if update_existing:
            vals = build_vals(name, price_m, sku, pos_category_field, cat_id)
            odoo.write("product.template", [pid], vals)
            return pid, "updated"
        return pid, "skipped"

    vals = build_vals(name, price_m, sku, pos_category_field, cat_id)
    new_id = odoo.create("product.template", vals)
    return new_id, "created"


def main() -> None:
    ap = argparse.ArgumentParser(description="Import main items from JSON into Odoo (no addon types)")
    ap.add_argument("--file", required=True, help="Path to main_items.json or payload JSON")
    ap.add_argument("--apply", action="store_true", help="Apply changes to Odoo (default: dry-run)")
    ap.add_argument("--update-existing", action="store_true", help="Update existing products if found")
    ap.add_argument("--url", default="http://127.0.0.1:18069", help="Odoo base URL")
    ap.add_argument("--login", default="admin@wuchang.life", help="Odoo login")
    ap.add_argument("--password", default="poiuY926", help="Odoo password")
    ap.add_argument("--db", default="wuchang_preview_20251107", help="Database name")
    args = ap.parse_args()

    items = read_main_items(args.file)
    if not items:
        print("[error] No items parsed from", args.file)
        return

    client = OdooClient(args.url)
    dbs = client.list_databases()
    if args.db and args.db in dbs:
        db = args.db
    else:
        db = dbs[0] if dbs else args.db
    client.authenticate(db, args.login, args.password)

    created = 0
    updated = 0
    skipped = 0

    for it in items:
        name = str(it.get("name") or "").strip()
        if not name:
            continue
        price_m = it.get("price_m")
        sku = it.get("sku") or None
        category_name = (it.get("pos_category_name") or it.get("category") or None)

        if not args.apply:
            # dry-run preview
            existing = find_existing_product(client, name, sku)
            action = "update" if (existing and args.update_existing) else ("skip" if existing else "create")
            print(f"[dry-run] {action}: name={name} sku={sku} price_m={price_m} category={category_name}")
            continue

        try:
            pid, action = create_or_update_product(
                client,
                name,
                price_m,
                sku,
                category_name,
                args.update_existing,
            )
            if action == "created":
                created += 1
            elif action == "updated":
                updated += 1
            else:
                skipped += 1
            print(f"[ok] {action}: product.template id={pid} name={name}")
        except OdooRPCError as e:
            print(f"[error] failed: name={name} sku={sku} err={e}")

    if args.apply:
        print(f"[summary] created={created} updated={updated} skipped={skipped}")
    else:
        print(f"[summary] dry-run completed for {len(items)} items")


if __name__ == "__main__":
    main()

