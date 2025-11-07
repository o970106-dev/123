from odoo_jsonrpc import OdooClient, OdooRPCError


def main():
    client = OdooClient('http://127.0.0.1:18069')
    client.authenticate('wuchang_preview_20251107', 'admin', 'odoo')
    sessions = client.search_read('pos.session', [], ['id', 'state'])
    print('found sessions:', sessions)
    for s in sessions:
        sid = s['id']
        st = s['state']
        try:
            if st == 'opening_control':
                client.call_kw('pos.session', 'action_pos_session_open', [[sid]], {})
                st = 'opened'
        except OdooRPCError as e:
            print('[warn] open failed for', sid, e)
        try:
            client.call_kw('pos.session', 'action_pos_session_closing_control', [[sid]], {})
        except OdooRPCError:
            pass
        try:
            client.call_kw('pos.session', 'action_pos_session_close', [[sid]], {})
            print('[done] closed session', sid)
        except OdooRPCError as e:
            print('[warn] close failed for', sid, e)


if __name__ == '__main__':
    main()
