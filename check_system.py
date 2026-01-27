
import json
import os
import sys
import paramiko
from odoo_jsonrpc import OdooClient, OdooRPCError

def load_config(path: str) -> dict:
    """載入設定檔，如果不存在則嘗試使用範例檔"""
    if not os.path.exists(path):
        alt_path = os.path.join(os.path.dirname(__file__), "config.example.json")
        if not os.path.exists(alt_path):
            print("❌ 錯誤：找不到 `config.json` 或 `config.example.json`。")
            sys.exit(1)
        print(f"⚠️ 警告：找不到 `{path}`，將使用範例設定 `{alt_path}`。")
        path = alt_path

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def check_ssh_connection(config: dict):
    """檢查 SSH 連線狀態"""
    print(" Checking SSH 連線中...")
    host = config.get("host")
    port = config.get("port", 22)
    user = config.get("user")
    key_path = config.get("key_path")
    password = config.get("password")

    if not all([host, user]):
        print("❌ SSH 錯誤：設定檔中缺少 `host` 或 `user`。")
        return

    client = None
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"   - 正在連線至 {user}@{host}:{port}...")
        client.connect(
            hostname=host,
            port=port,
            username=user,
            key_filename=key_path,
            password=password,
            timeout=10
        )

        print("   - 連線成功！正在執行遠端指令 `uname -a`...")
        stdin, stdout, stderr = client.exec_command("uname -a")
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if output:
            print(f"   - 遠端回應：{output}")
            print("✅ SSH 連線正常。")
        else:
            print(f"❌ SSH 錯誤：指令執行失敗。{error}")

    except paramiko.AuthenticationException:
        print("❌ SSH 錯誤：認證失敗，請檢查您的金鑰路徑或密碼。")
    except paramiko.SSHException as e:
        print(f"❌ SSH 錯誤：連線時發生錯誤 - {e}")
    except Exception as e:
        print(f"❌ 發生未預期的錯誤：{e}")
    finally:
        if client:
            client.close()

def check_odoo_connection(config: dict):
    """檢查 Odoo 連線狀態"""
    print("\n Checking Odoo 連線中...")
    url = config.get("odoo_url")
    db = config.get("odoo_db")
    login = config.get("odoo_login")
    password = config.get("odoo_password")

    if not all([url, db, login, password]):
        print("❌ Odoo 錯誤：設定檔中缺少 `odoo_url`, `odoo_db`, `odoo_login`, 或 `odoo_password`。")
        return

    try:
        print(f"   - 正在連線至 Odoo 伺服器：{url}")
        client = OdooClient(url, timeout=10)

        print(f"   - 正在認證資料庫 `{db}`...")
        client.authenticate(db, login, password)

        print("   - 認證成功！正在取得 `web.base.url`...")
        web_base_url = client.call_kw("ir.config_parameter", "get_param", [], {"key": "web.base.url"})

        print(f"   - Odoo 的 `web.base.url` 是：{web_base_url}")
        print("✅ Odoo 連線正常。")

    except OdooRPCError as e:
        print(f"❌ Odoo RPC 錯誤：{e}")
    except Exception as e:
        print(f"❌ 發生未預期的錯誤：{e}")

def main():
    """主執行函數"""
    config_path = "config.json"
    config = load_config(config_path)

    check_ssh_connection(config)
    check_odoo_connection(config)

if __name__ == "__main__":
    main()
