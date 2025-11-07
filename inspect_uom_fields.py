from odoo_jsonrpc import OdooClient


def main():
    url = 'http://127.0.0.1:18069'
    db = 'wuchang_preview_20251107'
    login = 'admin'
    pw = 'odoo'

    client = OdooClient(url)
    client.authenticate(db, login, pw)
    fields = client.call_kw('uom.uom', 'fields_get', [[], []], {})
    print('uom.uom fields:', sorted(list(fields.keys()))[:50])


if __name__ == '__main__':
    main()
