import sys
import paramiko
from odoo_jsonrpc import OdooClient, OdooRPCError
import requests
from shared_config import load_config

def print_status(status, message):
    """以不同顏色印出狀態訊息。"""
    if status == "ok":
        # 綠色代表成功
        print(f"\033[92m[✓] {message}\033[0m")
    elif status == "error":
        # 紅色代表錯誤
        print(f"\033[91m[✗] {message}\033[0m")
    elif status == "warn":
        # 黃色代表警告
        print(f"\033[93m[!] {message}\033[0m")
    else:
        # 預設顏色代表資訊
        print(f"[*] {message}")

def check_ssh_connection(config: dict):
    """檢查 SSH 連線狀態。"""
    print_status("info", "--- 開始檢查 SSH 連線 ---")
    ssh_config = config.get("ssh")
    if not ssh_config:
        print_status("error", "設定檔中缺少 `ssh` 區段。")
        print_status("info", "--- SSH 連線檢查結束 ---\n")
        return

    host = ssh_config.get("host")
    port = int(ssh_config.get("port", 22))
    user = ssh_config.get("user")
    auth_method = ssh_config.get("auth_method", "key")
    key_path = ssh_config.get("key_path")
    password = ssh_config.get("password")

    if not host or not user:
        print_status("error", "SSH 設定不完整，`host` 和 `user` 為必填項。")
        print_status("info", "--- SSH 連線檢查結束 ---\\n")
        return

    client = None
    try:
        print_status("info", f"嘗試連線至 {user}@{host}:{port}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if auth_method == "key":
            client.connect(
                hostname=host, port=port, username=user,
                key_filename=key_path, password=password, timeout=10,
                allow_agent=True, look_for_keys=True
            )
        else:
            client.connect(
                hostname=host, port=port, username=user,
                password=password, timeout=10,
                allow_agent=False, look_for_keys=False
            )

        print_status("ok", "SSH 連線成功！")

        stdin, stdout, stderr = client.exec_command("uname -a")
        output = stdout.read().decode().strip()
        print_status("info", f"遠端伺服器回應: {output}")

    except paramiko.AuthenticationException:
        print_status("error", "SSH 認證失敗。請檢查您的使用者名稱、密碼或金鑰路徑。")
    except paramiko.SSHException as e:
        print_status("error", f"SSH 連線時發生錯誤: {e}")
    except FileNotFoundError:
        print_status("error", f"找不到 SSH 金鑰檔案：{key_path}。")
    except Exception as e:
        print_status("error", f"發生未預期的錯誤: {e}")
    finally:
        if client:
            client.close()
        print_status("info", "--- SSH 連線檢查結束 ---\n")

def check_odoo_connection(config: dict):
    """檢查 Odoo 連線狀態。"""
    print_status("info", "--- 開始檢查 Odoo 連線 ---")
    odoo_config = config.get("odoo")
    if not odoo_config:
        print_status("error", "設定檔中缺少 `odoo` 區段。")
        print_status("info", "--- Odoo 連線檢查結束 ---\\n")
        return

    url = odoo_config.get("url")
    db = odoo_config.get("db")
    login = odoo_config.get("login")
    password = odoo_config.get("password")

    if not all([url, db, login, password]):
        print_status("error", "Odoo 設定不完整，`url`, `db`, `login`, `password` 都是必填項。")
        print_status("info", "--- Odoo 連線檢查結束 ---\\n")
        return

    try:
        print_status("info", f"嘗試連線至 Odoo 伺服器: {url}")
        client = OdooClient(url)

        dbs = client.list_databases() or []
        if isinstance(dbs, dict) and dbs.get("databases"):
             dbs = dbs["databases"]

        if not dbs:
            print_status("warn", "無法從伺服器獲取資料庫列表，但將繼續嘗試...")
        else:
            print_status("ok", f"成功獲取資料庫列表: {dbs}")
            if db not in dbs:
                print_status("error", f"指定的資料庫 '{db}' 不在伺服器列表上。")
                print_status("info", "--- Odoo 連線檢查結束 ---\\n")
                return

        print_status("info", f"嘗試使用帳號 '{login}' 登入資料庫 '{db}'...")
        client.authenticate(db, login, password)
        print_status("ok", "Odoo 認證成功！")

        user_info = client.search_read("res.users", [["login", "=", login]], ["name"], limit=1)
        user_name = user_info[0]['name'] if user_info else '未知'
        print_status("ok", f"成功以使用者 '{user_name}' 的身分執行操作。")

    except OdooRPCError as e:
        print_status("error", f"Odoo RPC 錯誤: {e}")
    except requests.exceptions.ConnectionError:
        print_status("error", f"無法連線至 Odoo URL: {url}。請檢查 URL 是否正確或 Odoo 伺服器是否正在執行。")
    except Exception as e:
        print_status("error", f"發生未預期的錯誤: {e}")
    finally:
        print_status("info", "--- Odoo 連線檢查結束 ---")

def main():
    """主執行函式，執行所有系統檢查。"""
    print("=========================")
    print("=   系統組態與連線檢查   =")
    print("=========================\n")

    config_path = "config.json"
    config = load_config(config_path)

    check_ssh_connection(config)
    check_odoo_connection(config)

    print("所有檢查已完成。")

if __name__ == "__main__":
    main()
