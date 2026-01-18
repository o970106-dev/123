from odoo_jsonrpc import OdooClient, OdooRPCError
from shared_config import load_config

def main():
    try:
        config = load_config("config.json")
        odoo_config = config.get("odoo")
        if not odoo_config:
            print("[error] 設定檔中缺少 `odoo` 區段。")
            return

        url = odoo_config.get("url")
        db = odoo_config.get("db")
        login = odoo_config.get("login")
        password = odoo_config.get("password")

        if not all([url, db, login, password]):
            print("[error] Odoo 設定不完整，`url`, `db`, `login`, `password` 都是必填項。")
            return

        client = OdooClient(url)

        print(f"[info] 嘗試使用帳號 '{login}' 登入資料庫 '{db}'...")
        client.authenticate(db, login, password)

        me = client.search_read("res.users", [["login", "=", login]], ["id", "name", "login", "active"], limit=1)
        base_url = client.call_kw("ir.config_parameter", "get_param", [], {"key": "web.base.url"})

        print("[ok] 登入成功！")
        print(f"  資料庫 (DB): {db}")
        print(f"  使用者資訊: {me}")
        print(f"  網站根目錄 URL (web.base.url): {base_url}")

    except FileNotFoundError as e:
        print(f"[error] {e}")
    except OdooRPCError as e:
        print(f"[error] Odoo RPC 錯誤: {e}")
    except Exception as e:
        print(f"[error] 發生未預期的錯誤: {e}")


if __name__ == "__main__":
    main()
