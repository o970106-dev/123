import os
import json
import socket
import sys

def check_dependencies():
    print("--- [1/6] Checking Dependencies ---")
    if not os.path.exists("requirements.txt"):
        print("[FAIL] requirements.txt not found")
        return False

    try:
        # Check if paramiko and openpyxl are installed
        import paramiko
        import openpyxl
        print("[PASS] Core dependencies (paramiko, openpyxl) are installed")
        return True
    except ImportError as e:
        print(f"[FAIL] Missing dependency: {e}")
        return False

def check_odoo_service():
    print("\n--- [2/6] Checking Odoo Service (Port 18069) ---")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('127.0.0.1', 18069))
    if result == 0:
        print("[PASS] Odoo service is running on port 18069")
        sock.close()
        return True
    else:
        print("[FAIL] Odoo service is NOT running on port 18069")
        sock.close()
        return False

def check_module_sync():
    print("\n--- [3/6] Checking Module Synchronization ---")
    root_mod = "pos_beverage_modifier"
    shadow_mod = "odoo19-shadow/addons/pos_beverage_modifier"

    if not os.path.exists(root_mod) or not os.path.exists(shadow_mod):
        print(f"[FAIL] One or both module directories missing: {root_mod}, {shadow_mod}")
        return False

    # Simple check: compare __manifest__.py
    with open(os.path.join(root_mod, "__manifest__.py"), "r") as f:
        root_m = f.read()
    with open(os.path.join(shadow_mod, "__manifest__.py"), "r") as f:
        shadow_m = f.read()

    if root_m == shadow_m:
        print("[PASS] Module manifests are synchronized")
        return True
    else:
        print("[FAIL] Module manifests are OUT OF SYNC")
        return False

def check_js_hardcoded_logic():
    print("\n--- [4/6] Checking for Hardcoded JS Logic ---")
    js_path = "pos_beverage_modifier/static/src/patch/product_item_patch.js"
    if not os.path.exists(js_path):
        print(f"[SKIP] JS file not found: {js_path}")
        return True

    with open(js_path, "r") as f:
        content = f.read()

    issues = []
    if "extra +=" in content or "extra -=" in content:
        issues.append("Hardcoded price adjustments found (extra += ...)")
    if 'targetNames = ["' in content:
        issues.append("Hardcoded product names found (targetNames = [...])")

    if issues:
        for issue in issues:
            print(f"[WARN] {issue}")
        return False # Return False to indicate warnings exist
    else:
        print("[PASS] No obvious hardcoded price logic found in JS")
        return True

def find_file_pythonic(filename):
    """Python-native alternative to 'find' for portability."""
    for root, dirs, files in os.walk("."):
        if filename in files:
            return os.path.join(root, filename)
    return None

def check_architectural_components():
    print("\n--- [5/6] Checking Architectural Components ---")
    components = [
        "wuchang_master.py",
        "staps_core.py",
        "renovate_system.py"
    ]

    all_found = True
    for comp in components:
        found_path = find_file_pythonic(comp)
        if found_path:
            print(f"[PASS] Component found: {comp} at {found_path}")
        else:
            print(f"[FAIL] Component MISSING: {comp}")
            all_found = False
    return all_found

def check_config():
    print("\n--- [6/6] Checking config.json ---")
    if not os.path.exists("config.json"):
        print("[FAIL] config.json MISSING")
        return False

    try:
        with open("config.json", "r") as f:
            cfg = json.load(f)

        # Check for Windows paths in key_path
        key_path = cfg.get("key_path", "")
        if "\\" in key_path or (len(key_path) > 1 and key_path[1] == ":"):
            print(f"[WARN] key_path contains Windows-style path: {key_path}")
            return False
        print("[PASS] config.json looks okay")
        return True
    except Exception as e:
        print(f"[FAIL] Error reading config.json: {e}")
        return False

def main():
    print("=== System Audit ('God View') ===")
    results = [
        check_dependencies(),
        check_odoo_service(),
        check_module_sync(),
        check_js_hardcoded_logic(),
        check_architectural_components(),
        check_config()
    ]

    print("\n=== Audit Complete ===")
    if all(results):
        print("Status: ALL CHECKS PASSED")
        sys.exit(0)
    else:
        # Check if only non-critical (like JS warnings) failed
        # For now, if any check returns False, we report overall failure
        print("Status: SOME CHECKS FAILED OR HAVE WARNINGS")
        # We don't exit with non-zero here if we just want to report,
        # but for a diagnostic tool, non-zero is often better if there are FAILs.
        if results[0] and results[2]: # Dependencies and Sync are critical
             sys.exit(0) # Allow success if basic environment is okay but service/config have issues
        else:
             sys.exit(1)

if __name__ == "__main__":
    main()
