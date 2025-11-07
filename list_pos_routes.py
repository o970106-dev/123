from odoo_jsonrpc import OdooClient


def main():
    url = 'http://127.0.0.1:18069'
    db = 'wuchang_preview_20251107'
    login = 'admin'
    pw = 'odoo'

    client = OdooClient(url)
    client.authenticate(db, login, pw)

    # call_kw expects [ids, *args]; routing_map is @api.model
    routes = client.call_kw('ir.http', 'routing_map', [ [] ], {})
    # routes is a list of dicts with 'route' keys
    pos_routes = [r for r in routes if 'route' in r and ('pos' in r['route'] or 'point_of_sale' in r['route'])]
    print('Found routes related to POS:')
    for r in pos_routes:
        print(r)

    print('Total route count:', len(routes))


if __name__ == '__main__':
    main()
