# -*- coding: utf-8 -*-
import json
import socket
from urllib.parse import urlparse

# 這是 odoo_jsonrpc 的本地副本，所以我們直接引用
from odoo_jsonrpc import OdooClient
from shared_config import load_config


def check_odoo_connection(cfg: dict):
    """檢查 Odoo 連線與基本狀態"""
    print("\n--- 正在檢查 Odoo 連線 ---")
    odoo_cfg = cfg.get("odoo", {})
    url = odoo_cfg.get("url")
    db = odoo_cfg.get("db")
    login = odoo_cfg.get("login")
    password = odoo_cfg.get("password")

    if not all([url, db, login, password]):
        print(" [錯誤] Odoo 設定不完整，請檢查 config.json")
        return

    try:
        parsed_url = urlparse(url)
        print(f"[*] 目標: {url}")

        # 檢查 DNS 和網路層
        ip = socket.gethostbyname(parsed_url.hostname)
        print(f"[*] 主機 {parsed_url.hostname} 解析 IP 成功: {ip}")

        # 建立客戶端並驗證
        client = OdooClient(url)
        print(f"[*] 正在列出資料庫...")
        dbs = client.list_databases()
        if not dbs:
            print(" [警告] 無法從 Odoo 實例獲取資料庫列表")
        else:
            print(f"[*] 成功獲取資料庫列表 (共 {len(dbs)} 個)")

        if db not in dbs:
            print(f" [錯誤] 指定的資料庫 '{db}' 不在列表中!")
            return

        print(f"[*] 正在以使用者 '{login}' 登入資料庫 '{db}'...")
        client.authenticate(db, login, password)
        print("[*] Odoo 驗證成功！")

        # 檢查 POS 設定
        configs = client.search_read("pos.config", [], ["id", "name"], limit=5)
        print(f"[*] 找到 {len(configs)} 個 POS 設定檔")

        print("\n[成功] Odoo 連線檢查完成，系統看來已準備就緒。")

    except socket.gaierror:
        print(f" [錯誤] DNS 解析失敗: 無法解析主機 '{parsed_url.hostname}'")
    except ConnectionRefusedError:
        print(f" [錯誤] 連線被拒絕。請檢查 Odoo 伺服器是否正在運行，以及防火牆設定。")
    except Exception as e:
        print(f" [錯誤] 發生未預期的 Odoo 連線錯誤: {e}")

# 從 manage_server 引入我們需要的功能
from manage_server import connect as ssh_connect, run_command as ssh_run_command

def check_ssh_connection(cfg: dict):
    """檢查 SSH 連線與伺服器基本狀態"""
    print("\n--- 正在檢查 SSH 連線與伺服器狀態 ---")
    ssh_cfg = cfg.get("ssh", {})
    host = ssh_cfg.get("host")

    if not host:
        print(" [錯誤] SSH 設定不完整，請檢查 config.json")
        return

    client = None
    try:
        print(f"[*] 目標伺服器: {host}")
        client = ssh_connect(ssh_cfg)
        print("[*] SSH 連線成功！")

        print("[*] 正在檢查系統資訊 (uname -a)...")
        out, err, rc = ssh_run_command(client, "uname -a")
        if rc == 0:
            print(f"  [資訊] {out.strip()}")
        else:
            print(f"  [警告] 無法獲取系統資訊: {err}")

        print("[*] 正在檢查可更新的套件...")
        out, err, rc = ssh_run_command(client, "apt list --upgradable | wc -l")
        # 輸出包含 "Listing... Done"，所以行數 > 1 表示有可更新的套件
        num_upgradable = int(out.strip()) - 1 if out.strip().isdigit() else 0
        if num_upgradable > 0:
            print(f"  [注意] 有 {num_upgradable} 個套件可以更新。建議執行 `python manage_server.py upgrade`")
        else:
            print("  [資訊] 系統是最新狀態。")

        print("\n[成功] SSH 連線與伺服器檢查完成。")

    except Exception as e:
        print(f" [錯誤] 發生未預期的 SSH 連線錯誤: {e}")
    finally:
        if client:
            client.close()


def main():
    """主執行函數"""
    print("--- 系統健康狀況檢查 ---")
    cfg = load_config()

    check_ssh_connection(cfg)
    check_odoo_connection(cfg)

if __name__ == "__main__":
    main()
