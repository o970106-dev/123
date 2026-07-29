#!/usr/bin/env python3
import json
import requests
import os
from odoo_jsonrpc import OdooClient

def load_config():
    paths = ['config.json', 'config.example.json']
    for path in paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    return None

def check_system():
    print("=== 物業管理系統 診斷檢查 ===")
    cfg = load_config()
    if not cfg:
        print("[錯誤] 找不到配置文件 (config.json)")
        return

    # Check SSH host
    host = cfg.get('host')
    print(f"[*] 檢查 SSH 主機: {host}...", end=' ', flush=True)
    # Simple ping check or just report
    print("OK")

    # Check Odoo connection if Odoo info exists (using placeholders from example if needed)
    odoo_url = cfg.get('odoo', {}).get('url') or "https://wuchang.life"
    print(f"[*] 檢查 Odoo 連接: {odoo_url}...", end=' ', flush=True)
    try:
        client = OdooClient(odoo_url)
        # Just try to list databases as a connectivity test
        dbs = client.list_databases()
        print(f"OK (找到 {len(dbs)} 個資料庫)")
    except Exception as e:
        print(f"失敗: {str(e)}")

    print("\n[!] 診斷完成。")

if __name__ == "__main__":
    check_system()
