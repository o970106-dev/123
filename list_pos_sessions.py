from odoo_jsonrpc import OdooClient


def main():
    client = OdooClient('http://127.0.0.1:18069')
    client.authenticate('wuchang_preview_20251107', 'admin', 'odoo')
    sessions = client.search_read('pos.session', [], ['id', 'name', 'state', 'config_id'])
    print('sessions:', sessions)


if __name__ == '__main__':
    main()
