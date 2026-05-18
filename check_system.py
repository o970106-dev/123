import paramiko
from odoo_jsonrpc import OdooClient, OdooRPCError
from shared_config import load_config

def check_ssh_connection(config):
    """Tests the SSH connection."""
    try:
        ssh_config = config.get("ssh", {})
        host = ssh_config.get("host")
        port = ssh_config.get("port", 22)
        user = ssh_config.get("user")
        auth_method = ssh_config.get("auth_method", "key")
        key_path = ssh_config.get("key_path")
        password = ssh_config.get("password")

        if not host or not user:
            print("[SSH 狀態] 🔴 失敗：缺少主機或用戶名。")
            return

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if auth_method == "key":
            client.connect(hostname=host, port=port, username=user, key_filename=key_path, timeout=5)
        else:
            client.connect(hostname=host, port=port, username=user, password=password, timeout=5)

        stdin, stdout, stderr = client.exec_command("uname -a")
        output = stdout.read().decode().strip()
        client.close()

        if output:
            print(f"[SSH 狀態] 🟢 成功：連接到 {host}，伺服器信息：{output}")
        else:
            print(f"[SSH 狀態] 🟡 警告：連接成功，但無法獲取伺服器信息。")

    except Exception as e:
        print(f"[SSH 狀態] 🔴 失敗：{e}")

def check_odoo_connection(config):
    """Tests the Odoo connection."""
    try:
        odoo_config = config.get("odoo", {})
        url = odoo_config.get("url")
        db = odoo_config.get("db")
        login = odoo_config.get("login")
        password = odoo_config.get("password")

        if not all([url, db, login, password]):
            print("[Odoo 狀態] 🔴 失敗：缺少 URL、數據庫、登錄名或密碼。")
            return

        client = OdooClient(url)
        client.authenticate(db, login, password)
        user = client.search_read("res.users", [["login", "=", login]], ["name"], limit=1)

        if user:
            user_name = user[0].get("name", login)
            print(f"[Odoo 狀態] 🟢 成功：連接到 {url}，用戶 '{user_name}' 驗證成功。")
        else:
            print("[Odoo 狀態] 🟡 警告：連接成功，但無法獲取用戶信息。")

    except OdooRPCError as e:
        print(f"[Odoo 狀態] 🔴 失敗：RPC 錯誤 - {e}")
    except Exception as e:
        print(f"[Odoo 狀態] 🔴 失敗：{e}")

def main():
    """Main function to run the system checks."""
    print("===== 系統狀態檢查 =====")
    try:
        config = load_config()
        check_ssh_connection(config)
        check_odoo_connection(config)
    except FileNotFoundError:
        print("🔴 錯誤：找不到 `config.json` 或 `config.example.json` 配置文件。")
    except Exception as e:
        print(f"🔴 發生未知錯誤：{e}")
    finally:
        print("========================")

if __name__ == "__main__":
    main()
