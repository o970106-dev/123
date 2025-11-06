from odoo_jsonrpc import OdooClient


def main():
    url = 'http://34.80.194.190'
    login = 'admin@wuchang.life'
    pw = 'poiuY926'
    module_name = 'pos_beverage_modifier'

    print('Connecting to Odoo at', url)
    client = OdooClient(url)
    dbs = client.list_databases() or []
    if isinstance(dbs, dict) and dbs.get('databases'):
        dbs = dbs['databases']
    if not dbs:
        raise RuntimeError('No databases found on server')
    db = dbs[0]
    print('Using DB:', db)
    client.authenticate(db, login, pw)

    print('Updating app list...')
    client.call_kw('ir.module.module', 'update_list', [], {})
    print('Updated app list')

    mods = client.search_read('ir.module.module', [('name', '=', module_name)], ['id', 'name', 'state'])
    print('Module record:', mods)
    if not mods:
        raise RuntimeError(f'Module {module_name} not found after update_list')

    mid = mods[0]['id']
    print('Upgrading module...', module_name)
    client.call_kw('ir.module.module', 'button_immediate_upgrade', [[mid]], {})
    after = client.search_read('ir.module.module', [('id', '=', mid)], ['id', 'name', 'state'])
    print('Module state after upgrade:', after)
    print('Done: module upgraded with backend views/models.')


if __name__ == '__main__':
    main()
