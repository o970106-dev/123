from odoo_jsonrpc import OdooClient


def main():
    # Local preview instance
    url = 'http://127.0.0.1:18069'
    db = 'wuchang_preview_20251107'
    login = 'admin'
    pw = 'odoo'

    # Ensure core POS route is available, then custom addon
    modules = [
        'point_of_sale',
        'pos_beverage_modifier',
    ]

    print('Connecting to Odoo at', url)
    client = OdooClient(url)
    # Authenticate directly to target DB
    client.authenticate(db, login, pw)
    print('Using DB:', db)

    print('Updating app list...')
    client.call_kw('ir.module.module', 'update_list', [], {})
    print('Updated app list')

    for module_name in modules:
        mods = client.search_read('ir.module.module', [('name', '=', module_name)], ['id', 'name', 'state'])
        print('Module record:', mods)
        if not mods:
            raise RuntimeError(f'Module {module_name} not found after update_list')

        mid = mods[0]['id']
        st = mods[0]['state']
        if st != 'installed':
            print('Installing module...', module_name)
            client.call_kw('ir.module.module', 'button_immediate_install', [[mid]], {})
            after = client.search_read('ir.module.module', [('id', '=', mid)], ['id', 'name', 'state'])
            print('Installed module state:', after)
            if not after or after[0]['state'] != 'installed':
                raise RuntimeError(f'Module {module_name} installation did not complete')
        else:
            print(f'Module {module_name} already installed')

    print('Done: POS core and beverage addon ready.')


if __name__ == '__main__':
    main()
