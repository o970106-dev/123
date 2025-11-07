import argparse
import json
from typing import Any, Dict, List, Optional, Tuple

from odoo_jsonrpc import OdooClient, OdooRPCError


def read_payload(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in ("items", "products", "menu", "data"):
            if k in data and isinstance(data[k], list):
                return data[k]
    return []


def find_m_extra(lines: List[Dict[str, Any]]) -> Optional[float]:
    size_lines = [ln for ln in (lines or []) if (ln.get("attribute_type") or ln.get("type")) == "size"]
    # lines may use either keys: attribute_type/name/price or type/name/price depending on source
    for ln in size_lines:
        name = str(ln.get("name") or "").strip().upper()
        if name == "M":
            try:
                return float(ln.get("price") or 0.0)
            except Exception:
                return 0.0
    return None


def compute_price_m(item: Dict[str, Any]) -> Optional[float]:
    base_price = item.get("price")
    config = item.get("config") or {}
    lines = config.get("lines") or []
    m_extra = find_m_extra(lines)
    if base_price is None or m_extra is None:
        return None
    try:
        return round(float(base_price) + float(m_extra), 2)
    except Exception:
        return None


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
    ap = argparse.ArgumentParser(description="Update product list_price to M-size baseline using old payload add-ons")
    ap.add_argument("--file", default="menu_payload_m.json", help="Old menu payload JSON with config.lines")
    ap.add_argument("--apply", action="store_true", help="Apply changes to Odoo (default: dry-run)")
    ap.add_argument("--url", default="http://127.0.0.1:18069", help="Odoo base URL")
    ap.add_argument("--login", default="admin@wuchang.life", help="Odoo login")
    ap.add_argument("--password", default="poiuY926", help="Odoo password")
    ap.add_argument("--db", default="wuchang_preview_20251107", help="Database name")
    ap.add_argument("--skip-categories", nargs="*", default=["手沖咖啡", "簡餐"], help="Categories to skip variant/attribute ops (prices are still updated)")
    args = ap.parse_args()

    items = read_payload(args.file)
    if not items:
        print("[error] No items parsed from", args.file)
        return

    client = OdooClient(args.url)
    client.authenticate(args.db, args.login, args.password)

    updated = 0
    skipped_no_m = 0
    not_found = 0
    preview = 0

    for it in items:
        name = str(it.get("name") or "").strip()
        if not name:
            continue
        sku = it.get("sku") or None
        category_name = str(it.get("category") or it.get("pos_category_name") or "").strip()

        # Compute M price from payload config
        price_m = compute_price_m(it)
        if price_m is None:
            skipped_no_m += 1
            print(f"[skip] no M-size or base price missing: name={name} sku={sku}")
            continue

        p = find_product(client, name, sku)
        if not p:
            not_found += 1
            print(f"[warn] product not found in Odoo: name={name} sku={sku}")
            continue

        # We do not touch variants/attributes for any category, especially for 手沖咖啡/簡餐
        if not args.apply:
            preview += 1
            print(f"[dry-run] update list_price -> {price_m}: id={p['id']} name={name} sku={sku} category={category_name}")
            continue

        try:
            client.write("product.template", [p["id"]], {"list_price": price_m})
            updated += 1
            print(f"[ok] updated list_price={price_m}: id={p['id']} name={name}")
        except OdooRPCError as e:
            print(f"[error] write failed: id={p['id']} name={name} err={e}")

    if args.apply:
        print(f"[summary] updated={updated} skipped_no_m={skipped_no_m} not_found={not_found}")
    else:
        print(f"[summary] dry-run count={preview} skipped_no_m={skipped_no_m} not_found={not_found}")


if __name__ == "__main__":
    main()

