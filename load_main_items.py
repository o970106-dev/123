import argparse
import json
from typing import Any, Dict, List, Optional

from odoo_jsonrpc import OdooClient


def read_menu_items(path: str) -> List[Dict[str, Any]]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    # fallback if payload wraps in a dict
    if isinstance(data, dict):
        for k in ('items', 'products', 'menu', 'data'):
            if k in data and isinstance(data[k], list):
                return data[k]
    return []


def unique_by_name(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for it in items:
        nm = it.get('name')
        if not nm or nm in seen:
            continue
        seen.add(nm)
        out.append(it)
    return out


def fetch_odoo_products(client: OdooClient, names: List[str]) -> Dict[str, Dict[str, Any]]:
    name_map: Dict[str, Dict[str, Any]] = {}
    for nm in names:
        res = client.search_read(
            'product.template',
            [["name", "=", nm]],
            ["id", "name", "available_in_pos"],
            limit=1,
        )
        if not res:
            res = client.search_read(
                'product.template',
                [["name", "ilike", nm]],
                ["id", "name", "available_in_pos"],
                limit=1,
            )
        if res:
            name_map[nm] = res[0]
    return name_map


def main():
    ap = argparse.ArgumentParser(description='Load main items from old menu payload and cross-check in Odoo')
    ap.add_argument('--file', default='menu_payload_m.json', help='Menu payload JSON file')
    ap.add_argument('--url', default='http://127.0.0.1:18069')
    ap.add_argument('--db', default='wuchang_preview_20251107')
    ap.add_argument('--login', default='admin@wuchang.life')
    ap.add_argument('--password', default='poiuY926')
    args = ap.parse_args()

    items = read_menu_items(args.file)
    items = unique_by_name(items)
    names = [it.get('name') for it in items if it.get('name')]

    client = OdooClient(args.url)
    client.authenticate(args.db, args.login, args.password)
    mp = fetch_odoo_products(client, names)

    enriched: List[Dict[str, Any]] = []
    for it in items:
        nm = it.get('name')
        o = mp.get(nm)
        enriched.append({
            'name': nm,
            'sku': it.get('sku'),
            'category': it.get('category'),
            'price_m': it.get('price_m'),
            'pos_category_name': (it.get('config') or {}).get('pos_category_name'),
            'exists_in_odoo': bool(o),
            'odoo_tmpl_id': (o or {}).get('id'),
            'available_in_pos': (o or {}).get('available_in_pos'),
        })

    with open('main_items.json', 'w', encoding='utf-8') as f:
        json.dump({'count': len(enriched), 'items': enriched}, f, ensure_ascii=False, indent=2)

    with open('main_items.csv', 'w', encoding='utf-8') as f:
        f.write('name,sku,category,price_m,pos_category_name,exists_in_odoo,odoo_tmpl_id,available_in_pos\n')
        for it in enriched:
            f.write(f"{it['name']},{it.get('sku','')},{it.get('category','')},{it.get('price_m','')},{it.get('pos_category_name','')},{it['exists_in_odoo']},{it.get('odoo_tmpl_id','')},{it.get('available_in_pos','')}\n")

    print('[ok] loaded main items:', len(enriched))
    print('[ok] outputs: main_items.json, main_items.csv')


if __name__ == '__main__':
    main()

