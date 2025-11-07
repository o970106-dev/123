import argparse
import html
import re
from typing import Any, Dict, List, Optional

from odoo_jsonrpc import OdooClient, OdooRPCError


def pick_description_field(client: OdooClient) -> Optional[str]:
    """Pick an HTML description field from product.template.
    Prefer 'website_description' > 'description' > 'description_sale'.
    """
    fields: Dict[str, Any] = client.call_kw("product.template", "fields_get", [], {"attributes": ["type"]}) or {}
    candidates = ["website_description", "description", "description_sale"]
    for f in candidates:
        if f in fields:
            return f
    return None


def strip_html(text: str) -> str:
    if not text:
        return ""
    # Remove leading and trailing <p>...</p> if present
    text = re.sub(r"^\s*<p>(.*)</p>\s*$", r"\1", text, flags=re.DOTALL)
    # Remove all remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Unescape entities
    text = html.unescape(text)
    # Normalize whitespace
    return "".join(text.split()) if "\n" in text or "\r" in text else text.strip()


def find_product(client: OdooClient, tmpl_id: Optional[int], name: Optional[str]) -> Dict[str, Any]:
    fields = ["id", "name"]
    if tmpl_id:
        res = client.search_read("product.template", [["id", "=", tmpl_id]], fields, limit=1)
    else:
        res = client.search_read("product.template", [["name", "=", name]], fields, limit=1)
    if not res:
        raise RuntimeError("Product template not found")
    return res[0]


def main():
    ap = argparse.ArgumentParser(description="Sanitize main product HTML description and inject into name using '產品{text}' format")
    ap.add_argument("--url", default="http://127.0.0.1:18069")
    ap.add_argument("--db", default="wuchang_preview_20251107")
    ap.add_argument("--login", default="admin@wuchang.life")
    ap.add_argument("--password", default="poiuY926")
    ap.add_argument("--tmpl-id", type=int, help="Target product.template ID (e.g., 80)")
    ap.add_argument("--name", help="Target product.template name (e.g., 仲夏海鹽檸檬)")
    ap.add_argument("--dry-run", action="store_true", help="Only show before/after without writing")
    args = ap.parse_args()

    client = OdooClient(args.url)
    client.authenticate(args.db, args.login, args.password)

    # Pick description field to read
    desc_field = pick_description_field(client)
    if not desc_field:
        raise RuntimeError("No description field found on product.template")

    # Resolve product
    p = find_product(client, args.tmpl_id, args.name)
    pid = p["id"]

    # Read current description
    recs = client.search_read("product.template", [["id", "=", pid]], ["id", "name", desc_field], limit=1)
    rec = recs[0]
    before_name = rec.get("name") or ""
    before_desc = rec.get(desc_field) or ""

    cleaned = strip_html(before_desc)
    # Fallback: if description is empty, use current name as content to match template
    if not cleaned:
        cleaned = before_name or ""
    target_name = f"產品{cleaned}" if cleaned else before_name

    result: Dict[str, Any] = {
        "product_id": pid,
        "desc_field": desc_field,
        "before": {"name": before_name, "description": before_desc},
        "after": {"name": target_name, "description": cleaned},
        "written": False,
    }

    if not args.dry_run:
        # Write cleaned description back to a plain-text field if available; otherwise keep original field
        updates: Dict[str, Any] = {"name": target_name}
        # Write cleaned back to original description field to ensure no tags remain
        updates[desc_field] = cleaned
        client.write("product.template", [pid], updates)
        result["written"] = True

    print(result)


if __name__ == "__main__":
    main()

