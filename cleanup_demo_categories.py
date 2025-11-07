from odoo_jsonrpc import OdooClient, OdooRPCError


URL = 'http://127.0.0.1:18069'
DB = 'wuchang_preview_20251107'
LOGIN = 'admin'
PW = 'odoo'


def main():
    client = OdooClient(URL)
    client.authenticate(DB, LOGIN, PW)
    print('[info] authenticated to', URL, 'db=', DB)

    # Identify demo categories we introduced or typical placeholders
    demo_names = ['飲品', 'Demo', '示範', '示例']
    demo_ids = []
    for nm in demo_names:
        res = client.search_read('pos.category', [['name', '=', nm]], ['id', 'name'])
        demo_ids.extend([r['id'] for r in res])
    demo_ids = list(set(demo_ids))
    print('[info] demo pos.category ids:', demo_ids)

    # Detach products from demo categories
    if demo_ids:
        # product.template with demo pos_categ_ids
        prods = client.search_read(
            'product.template',
            [['pos_categ_ids', 'in', demo_ids]],
            ['id', 'name'],
        )
        print('[info] products using demo categories:', [p['name'] for p in prods])
        for p in prods:
            try:
                client.write('product.template', [p['id']], {'pos_categ_ids': [(3, cid, 0) for cid in demo_ids]})
            except OdooRPCError as e:
                print('[warn] detach demo cat failed for', p['name'], e)

    # Delete demo categories (may require closing open POS sessions)
    if demo_ids:
        try:
            # close opened sessions to allow category deletion
            opened = client.search_read('pos.session', [['state', '=', 'opened']], ['id', 'config_id'])
            closed_session_ids = []
            for s in opened:
                sid = s['id']
                try:
                    client.call_kw('pos.session', 'action_pos_session_closing_control', [[sid]], {})
                except OdooRPCError:
                    pass
                try:
                    client.call_kw('pos.session', 'action_pos_session_close', [[sid]], {})
                    closed_session_ids.append(sid)
                except OdooRPCError as e:
                    print('[warn] close session failed:', sid, e)

            client.call_kw('pos.category', 'unlink', [demo_ids], {})
            print('[done] removed demo pos.category ids:', demo_ids)
            # optionally reopen a session for config 1
            cfgs = client.search_read('pos.config', [], ['id'], limit=1)
            if cfgs:
                cfg_id = cfgs[0]['id']
                try:
                    sid = client.create('pos.session', {'config_id': cfg_id})
                    client.call_kw('pos.session', 'action_pos_session_open', [[sid]], {})
                    print('[info] reopened session id', sid)
                except OdooRPCError:
                    pass
        except OdooRPCError as e:
            print('[warn] delete demo categories failed:', e)

    # Align the showcase product back to its original category if beverage config exists
    tmpls = client.search_read('product.template', [['name', '=', '招牌咖啡']], ['id', 'name'], limit=1)
    if tmpls:
        pid = tmpls[0]['id']
        cfgs = client.search_read('pos.beverage.config', [['product_tmpl_id', '=', pid]], ['id', 'pos_category_id'], limit=1)
        if cfgs:
            pos_cat = cfgs[0].get('pos_category_id')
            cat_id = pos_cat[0] if isinstance(pos_cat, list) and pos_cat else None
            if cat_id:
                try:
                    # prefer multi-category relation if available
                    client.write('product.template', [pid], {'pos_categ_ids': [(6, 0, [cat_id])]})
                except OdooRPCError:
                    client.write('product.template', [pid], {'pos_category_id': cat_id})
                print('[done] product "招牌咖啡" assigned to original POS category id', cat_id)
        else:
            print('[info] no beverage config found for 招牌咖啡; skip reassign')

    print('[done] demo cleanup complete')


if __name__ == '__main__':
    main()
