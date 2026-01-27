import json
import os
import sys
import paramiko
from odoo_jsonrpc import OdooClient

def load_config(path="config.json"):
    if not os.path.exists(path):
        # 嘗試從範例配置讀取
        alt = "config.example.json"
        if os.path.exists(alt):
             with open(alt, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def check_ssh(cfg):
    print("--- 正在檢查 SSH 連線 ---")
    ssh_cfg = cfg.get("ssh", {})
    host = ssh_cfg.get("host")
    port = ssh_cfg.get("port", 22)
    user = ssh_cfg.get("user")
    auth_method = ssh_cfg.get("auth_method", "key")
    key_path = ssh_cfg.get("key_path")
    password = ssh_cfg.get("password")

    if not host or not user or host == "your.server.ip":
        print("[資訊] SSH 配置尚未完成，跳過檢查")
        return False

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if auth_method == "key":
            client.connect(hostname=host, port=port, username=user, key_filename=key_path, timeout=10)
        else:
            client.connect(hostname=host, port=port, username=user, password=password, timeout=10)
        print(f"[成功] 已連線至 {user}@{host}:{port}")
        client.close()
        return True
    except Exception as e:
        print(f"[失敗] SSH 連線出錯: {e}")
        return False

def check_odoo(cfg):
    print("\n--- 正在檢查 Odoo API 連線 ---")
    odoo_cfg = cfg.get("odoo", {})
    url = odoo_cfg.get("url")

    if url and url.startswith("http://"):
        print(f"[警告] 目前使用非加密連線: {url}")
        https_url = url.replace("http://", "https://")
        print(f"[資訊] 嘗試檢查 HTTPS 版本: {https_url}")
        try:
            import requests
            r = requests.get(https_url, timeout=5)
            print(f"[成功] HTTPS 可連通 (狀態碼: {r.status_code})")
        except Exception as e:
            print(f"[資訊] HTTPS 目前無法連通: {e}")
    db = odoo_cfg.get("db")
    login = odoo_cfg.get("login")
    password = odoo_cfg.get("password")

    if not url or url == "http://your.odoo.url":
        print("[資訊] Odoo 配置尚未完成，跳過檢查")
        return False

    try:
        client = OdooClient(url)
        uid = client.authenticate(db or "odoo", login, password)
        if uid:
            print(f"[成功] Odoo 認證成功 (UID: {uid})")
            return True
        else:
            print("[失敗] Odoo 認證失敗")
            return False
    except Exception as e:
        print(f"[失敗] Odoo 連線出錯: {e}")
        return False

def main():
    print("=== 五常系統診斷工具 ===")
    cfg = load_config()
    if not cfg:
        print("[錯誤] 找不到配置檔案")
        sys.exit(1)

    ssh_ok = check_ssh(cfg)
    odoo_ok = check_odoo(cfg)

    print("\n--- 診斷結果 ---")
    if ssh_ok and odoo_ok:
        print("✅ 所有系統運作正常！")
    else:
        print("💡 請確保 config.json 已正確配置。")

if __name__ == "__main__":
    main()
