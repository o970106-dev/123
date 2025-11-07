from odoo_jsonrpc import OdooClient


def main():
    client = OdooClient('http://127.0.0.1:18069')
    client.authenticate('wuchang_preview_20251107', 'admin', 'odoo')
    sessions = client.search_read('pos.session', [["state", "=", "opening_control"]], ["id"]) 
    for s in sessions:
        client.call_kw('pos.session', 'action_pos_session_open', [[s['id']]], {})
        print('[done] opened session', s['id'])


if __name__ == '__main__':
    main()
