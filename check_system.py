# -*- coding: utf-8 -*-
import json
import os
import sys
import paramiko
from odoo_jsonrpc import OdooClient

def load_config(path: str = "config.json") -> dict:
    """從 JSON 檔案載入設定，若檔案不存在則嘗試使用範例檔。"""
    if not os.path.exists(path):
        alt_path = "config.example.json"
        if not os.path.exists(alt_path):
            print("[錯誤] 找不到設定檔 (config.json 或 config.example.json)。")
            sys.exit(1)
        path = alt_path
        print(f"[提示] 未找到 config.json，使用範例設定檔：{path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"[錯誤] 設定檔 {path} 格式無效。")
        sys.exit(1)
    except Exception as e:
        print(f"[錯誤] 讀取設定檔時發生錯誤: {e}")
        sys.exit(1)

def check_ssh(ssh_config: dict):
    """測試 SSH 連線並執行一條簡單的指令。"""
    print("="*30)
    print("1. 正在檢查 SSH 連線...")
    client = None  # 先將 client 初始化為 None
    try:
        host = ssh_config.get("host")
        user = ssh_config.get("user")

        if not host or not user:
            print("[失敗] SSH 設定不完整 (需要 host 和 user)。")
            return

        print(f"   - 主機: {host}")
        print(f"   - 使用者: {user}")

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_params = {
            "hostname": host,
            "port": int(ssh_config.get("port", 22)),
            "username": user,
            "timeout": 30,
        }

        auth_method = ssh_config.get("auth_method", "key")
        if auth_method == "key":
            connect_params.update({
                "key_filename": ssh_config.get("key_path"),
                "allow_agent": True,
                "look_for_keys": True,
            })
        else:
            password = ssh_config.get("password")
            if not password:
                print("[失敗] 使用密碼驗證，但未在設定中提供密碼。")
                return
            connect_params.update({
                "password": password,
                "allow_agent": False,
                "look_for_keys": False,
            })

        client.connect(**connect_params)
        print("   - SSH 連線成功。")

        # 執行 'uname -a' 來確認遠端狀態
        stdin, stdout, stderr = client.exec_command("uname -a", timeout=10)
        kernel_info = stdout.read().decode().strip()
        if kernel_info:
            print(f"   - 遠端系統核心: {kernel_info}")
            print("[成功] SSH 伺服器運作正常。")
        else:
            err = stderr.read().decode().strip()
            print(f"[警告] SSH 指令執行失敗: {err}")

    except FileNotFoundError:
        print("[失敗] 找不到 SSH 私鑰檔案，請檢查 key_path 設定。")
    except paramiko.AuthenticationException:
        print("[失敗] SSH 驗證失敗，請檢查您的使用者名稱、密碼或金鑰。")
    except paramiko.SSHException as e:
        print(f"[失敗] SSH 連線時發生錯誤: {e}")
    except Exception as e:
        print(f"[失敗] 發生未預期的錯誤: {e}")
    finally:
        if client:
            client.close()

def check_odoo(odoo_config: dict):
    """測試 Odoo 連線並獲取基本資訊。"""
    print("\n" + "="*30)
    print("2. 正在檢查 Odoo 連線...")
    try:
        url = odoo_config.get("url")
        db = odoo_config.get("db")
        login = odoo_config.get("login")
        password = odoo_config.get("password")

        if not all([url, db, login, password]):
            print("[失敗] Odoo 設定不完整 (需要 url, db, login, password)。")
            return

        print(f"   - Odoo 伺服器 URL: {url}")
        print(f"   - 資料庫: {db}")

        client = OdooClient(url)

        # 1. 檢查伺服器是否可達
        print("   - 正在嘗試列出資料庫...")
        dbs = client.list_databases()
        if dbs is None: # None can indicate an error
            print("[失敗] 無法從 Odoo 伺服器獲取資料庫列表。請檢查 URL 和網路連線。")
            return

        print(f"   - 找到的資料庫: {dbs}")
        if db not in dbs:
            print(f"[失敗] 指定的資料庫 '{db}' 不在伺服器上。")
            return

        # 2. 嘗試驗證
        print("   - 正在驗證身份...")
        client.authenticate(db, login, password)
        print("   - Odoo 驗證成功。")

        # 3. 讀取公司資訊以確認 API 可用
        company_info = client.search_read("res.company", [], ["id", "name"], limit=1)
        if company_info:
            print(f"   - 成功讀取公司資料: {company_info[0]['name']}")
            print("[成功] Odoo 伺服器運作正常。")
        else:
            print("[警告] Odoo API 看似正常，但無法讀取公司資料。")

    except ConnectionRefusedError:
        print(f"[失敗] 連線被拒絕。請確認 Odoo 伺服器正在 {url} 上運行。")
    except Exception as e:
        # OdooClient might raise a generic Exception with a message
        print(f"[失敗] 連線 Odoo 時發生錯誤: {e}")

def main():
    """主函式，執行所有系統檢查。"""
    config = load_config()

    ssh_config = config.get("ssh")
    if ssh_config:
        check_ssh(ssh_config)
    else:
        print("[提示] 設定檔中未找到 'ssh' 區塊，跳過 SSH 檢查。")

    odoo_config = config.get("odoo")
    if odoo_config:
        check_odoo(odoo_config)
    else:
        print("\n[提示] 設定檔中未找到 'odoo' 區塊，跳過 Odoo 檢查。")

if __name__ == "__main__":
    main()
