import requests
import sys

BASE = "http://127.0.0.1:18069"
DB = "wuchang_shadow19"
LOGIN = "admin"
PASSWORD = "odoo"
MODULE = "pos_beverage_modifier"

def main():
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
