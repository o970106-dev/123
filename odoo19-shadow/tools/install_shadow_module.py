import requests
import sys
import json
import os

def load_config():
    paths = ["config.json", "../config.json", "../../config.json"]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}

def main():
    cfg = load_config()
    odoo_cfg = cfg.get("odoo", {})

    BASE = odoo_cfg.get("url", "http://127.0.0.1:8069")
    DB = odoo_cfg.get("db", "odoo")
    LOGIN = odoo_cfg.get("login", "admin")
    PASSWORD = odoo_cfg.get("password", "admin")
    MODULE = "pos_beverage_modifier"

    s = requests.Session()
    # Authenticate
    p = {"jsonrpc": "2.0", "method": "call", "params": {"db": DB, "login": LOGIN, "password": PASSWORD}}
    r = s.post(BASE + "/web/session/authenticate", json=p, timeout=30)
    r.raise_for_status()
    print("auth:", r.json())

    # Update app list
    p = {"jsonrpc": "2.0", "method": "call", "params": {}}
    r = s.post(BASE + "/web/dataset/call_kw/ir.module.module/update_list", json=p, timeout=120)
    r.raise_for_status()
    print("update_list:", r.json())

    # Search module
    p = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "ir.module.module",
            "method": "search_read",
            "args": [],
            "kwargs": {
                "domain": [["name", "=", MODULE]],
                "fields": ["id", "name", "state"],
                "limit": 1,
            },
        },
    }
    r = s.post(BASE + "/web/dataset/call_kw/ir.module.module/search_read", json=p, timeout=60)
    r.raise_for_status()
    mods = r.json().get("result") or []
    print("mods:", mods)
    if not mods:
        print("module not found", file=sys.stderr)
        sys.exit(2)
    mid = mods[0]["id"]

    # Install
    p = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "ir.module.module",
            "method": "button_immediate_install",
            "args": [[mid]],
            "kwargs": {},
        },
    }
    r = s.post(BASE + "/web/dataset/call_kw/ir.module.module/button_immediate_install", json=p, timeout=180)
    r.raise_for_status()
    print("install:", r.json())

    # Verify state
    p = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "ir.module.module",
            "method": "search_read",
            "args": [],
            "kwargs": {
                "domain": [["id", "=", mid]],
                "fields": ["id", "name", "state"],
                "limit": 1,
            },
        },
    }
    r = s.post(BASE + "/web/dataset/call_kw/ir.module.module/search_read", json=p, timeout=60)
    r.raise_for_status()
    print("after:", r.json())

if __name__ == "__main__":
    main()
