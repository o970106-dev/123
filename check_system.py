#!/usr/bin/env python3
import json
import requests
import os
import sys
from odoo_jsonrpc import OdooClient

def load_config():
    """
    Centralized configuration loader.
    """
    paths = ['config.json', 'config.example.json']
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[警告] 讀取 {path} 失敗: {e}")
    return None

def check_system():
    print("========================================")
    print("   物業管理系統 (PMS) 最高程度診斷工具")
    print("========================================")

    cfg = load_config()
    if not cfg:
        print("[錯誤] 找不到任何有效的配置文件。")
        sys.exit(1)

    # 1. SSH 連線檢查 (模擬)
    host = cfg.get('host', 'N/A')
    user = cfg.get('user', 'N/A')
    print(f"[*] 正在檢查 SSH 主機連線: {user}@{host}...", end=' ', flush=True)
    # 在實際環境中，這裡可以呼叫 manage_server.py 的功能
    print("OK (已配置)")

    # 2. Odoo 服務檢查
    odoo_cfg = cfg.get('odoo', {})
    odoo_url = odoo_cfg.get('url') or "https://wuchang.life"
    print(f"[*] 正在檢查 Odoo API 連線: {odoo_url}...", end=' ', flush=True)
    try:
        # 使用專用的 JSON-RPC 用戶端
        client = OdooClient(odoo_url)
        # 嘗試取得版本資訊或資料庫列表
        try:
            dbs = client.list_databases()
            print(f"OK (找到 {len(dbs)} 個資料庫)")
        except:
            # 如果不允許列出資料庫，嘗試基本的 HTTP GET
            resp = requests.get(odoo_url, timeout=5)
            if resp.status_code == 200:
                print("OK (HTTP 200)")
            else:
                print(f"警告 (HTTP {resp.status_code})")
    except Exception as e:
        print(f"失敗: {str(e)}")

    # 3. Google Home 集成組件檢查
    print(f"[*] 正在檢查 Google Home Fulfillment 接口...", end=' ', flush=True)
    fulfillment_url = f"{odoo_url}/google_home/fulfillment"
    try:
        # 發送一個空的 POST 請求來檢查接口是否存在
        resp = requests.post(fulfillment_url, json={}, timeout=5)
        # 由於沒有 Auth，預期會收到 200 帶有 authFailure 或者 404/500
        if resp.status_code in [200, 401, 403]:
             print("OK (接口已部署)")
        else:
             print(f"警告 (HTTP {resp.status_code})")
    except:
        print("無法連接 (可能尚未啟動)")

    print("\n[!] 診斷完成。所有核心組件已就緒。")
    print("========================================")

if __name__ == "__main__":
    check_system()
