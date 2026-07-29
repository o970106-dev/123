import subprocess
import requests
import json
import os
import sys

def check_odoo_local():
    url = "http://127.0.0.1:18069"
    print(f"[Check] Local Odoo Service ({url})...")
    try:
        resp = requests.get(url, timeout=5)
        print(f"  Status: {resp.status_code} OK")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  Status: Connection Failed ({e})")
        return False

def check_remote_server():
    print("[Check] Remote Server Status (via manage_server.py)...")
    try:
        # Run manage_server.py check
        result = subprocess.run(
            [sys.executable, "manage_server.py", "check"],
            capture_output=True,
            text=True,
            timeout=60
        )
        print(result.stdout)
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("  Status: Timeout after 60 seconds")
        return False
    except Exception as e:
        print(f"  Status: Failed to run check ({e})")
        return False

def main():
    print("=" * 40)
    print(" SYSTEM DIAGNOSTIC REPORT (God View)")
    print("=" * 40)

    odoo_ok = check_odoo_local()
    print("-" * 20)
    remote_ok = check_remote_server()

    print("=" * 40)
    if odoo_ok and remote_ok:
        print(" SYSTEM STATUS: HEALTHY")
    elif not odoo_ok and not remote_ok:
        print(" SYSTEM STATUS: CRITICAL (Both Local & Remote unreachable)")
    else:
        print(" SYSTEM STATUS: DEGRADED")
    print("=" * 40)

if __name__ == "__main__":
    main()
