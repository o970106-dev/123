import json
import os
import sys
from odoo_jsonrpc import OdooClient, OdooRPCError

def load_config(config_path='config.json'):
    if not os.path.exists(config_path):
        print(f"[警告] 未找到 {config_path}，将尝试使用 config.example.json", file=sys.stderr)
        config_path = 'config.example.json'
        if not os.path.exists(config_path):
            print(f"[错误] {config_path} 也不存在，请创建您的 config.json", file=sys.stderr)
            sys.exit(1)

    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    config = load_config()
    odoo_config = config.get('odoo', {})

    url = odoo_config.get('url')
    db = odoo_config.get('db')
    login = odoo_config.get('login')
    password = odoo_config.get('password')

    if not all([url, db, login, password]) or 'your_' in url:
        print("[error] Odoo configuration in config.json is missing, incomplete, or still using placeholder values.")
        print("Please copy config.example.json to config.json and fill in your actual Odoo credentials.")
        return

    client = OdooClient(url)
    try:
        client.authenticate(db, login, password)
        me = client.search_read("res.users", [["login", "=", login]], ["id", "name", "login", "active"], limit=1)
        base_url = client.call_kw("ir.config_parameter", "get_param", [], {"key": "web.base.url"})
        print("[ok] login succeeded")
        print("db:", db)
        print("user:", me)
        print("web.base.url:", base_url)
    except OdooRPCError as e:
        print(f"[error] login failed for {login}:", str(e))
    except Exception as e:
        print(f"[error] an unexpected error occurred:", str(e))

if __name__ == "__main__":
    main()
