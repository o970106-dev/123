import json
from collections import defaultdict
from typing import Dict, List, Tuple

from odoo_jsonrpc import OdooClient


URL = "http://127.0.0.1:18069"
DB = "wuchang_preview_20251107"
LOGIN = "admin@wuchang.life"
PW = "poiuY926"


def main():
    client = OdooClient(URL)
    client.authenticate(DB, LOGIN, PW)

    # List POS-available product templates (main items)
    products = client.search_read(
        "product.template",
        [["available_in_pos", "=", True]],
        ["id", "name", "available_in_pos"],
        limit=500,
    )

    # Build mapping: product -> addon lines
    mapping: Dict[str, List[Dict]] = {}
    global_counts: Dict[Tuple[str, str], int] = defaultdict(int)

    for p in products:
        tmpl_id = p["id"]
        name = p["name"]
        # Fetch beverage config(s) for this product
        configs = client.search_read(
            "pos.beverage.config",
            [["product_tmpl_id", "=", tmpl_id]],
            ["id", "name", "show_popup", "pos_category_id", "line_ids"],
        )
        lines_out: List[Dict] = []
        for cfg in configs:
            line_ids = cfg.get("line_ids") or []
            if line_ids:
                # read lines
                lines = client.search_read(
                    "pos.beverage.config.line",
                    [["id", "in", line_ids]],
                    ["id", "attribute_type", "name", "price", "selected"],
                )
                for ln in lines:
                    lines_out.append(
                        {
                            "attribute_type": ln.get("attribute_type") or "other",
                            "name": ln.get("name") or "",
                            "price": ln.get("price") or 0.0,
                            "selected": ln.get("selected") or False,
                        }
                    )
                    key = (ln.get("attribute_type") or "other", ln.get("name") or "")
                    global_counts[key] += 1

        mapping[name] = lines_out

    # Compute unique attribute values per product (appear only once globally)
    unique_per_product: Dict[str, List[Dict]] = {}
    for name, lines in mapping.items():
        uniq = []
        for ln in lines:
            key = (ln["attribute_type"], ln["name"])
            if global_counts.get(key, 0) == 1:
                uniq.append(ln)
        unique_per_product[name] = uniq

    # Write JSON reports
    with open("menu_addon_mapping.json", "w", encoding="utf-8") as f:
        json.dump({"mapping": mapping, "global_counts": {f"{k[0]}::{k[1]}": v for k, v in global_counts.items()}}, f, ensure_ascii=False, indent=2)
    with open("menu_addon_unique.json", "w", encoding="utf-8") as f:
        json.dump({"unique": unique_per_product}, f, ensure_ascii=False, indent=2)

    # Write a simple CSV for quick review
    with open("menu_addon_mapping.csv", "w", encoding="utf-8") as f:
        f.write("product,attribute_type,name,price,selected\n")
        for prod, lines in mapping.items():
            if not lines:
                f.write(f"{prod},,,,)\n")
                continue
            for ln in lines:
                f.write(
                    f"{prod},{ln['attribute_type']},{ln['name']},{ln['price']},{ln['selected']}\n"
                )

    print("[ok] generated reports: menu_addon_mapping.json, menu_addon_unique.json, menu_addon_mapping.csv")


if __name__ == "__main__":
    main()
