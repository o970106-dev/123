import json
import os
import sys

def load_config():
    paths = ['config.json', 'config.example.json']
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r') as f:
                return json.load(f)
    return None

def check_modules():
    mods = ['pm', 'pf', 'vt', 'cc', 'sc', 'er']
    results = {}
    for m in mods:
        path = os.path.join('pms_modules', m, 'core', 'odoo19-shadow', 'docker-compose.yml')
        results[m] = os.path.exists(path)
    return results

def main():
    print("=== PMS System Diagnostic ===")

    cfg = load_config()
    if cfg:
        print(f"[OK] Configuration loaded (host: {cfg.get('host')})")
    else:
        print("[FAIL] Configuration not found")

    print("\n--- Module Check ---")
    mod_results = check_modules()
    all_ok = True
    for mod, exists in mod_results.items():
        status = "[OK]" if exists else "[MISSING]"
        print(f"{mod.upper():<4}: {status}")
        if not exists: all_ok = False

    print("\n--- Addon Check ---")
    sc_addon = 'pms_modules/sc/core/odoo19-shadow/addons/sc_google_home/__manifest__.py'
    pf_addon = 'pms_modules/pf/core/odoo19-shadow/addons/pf_resident_portal/__manifest__.py'

    if os.path.exists(sc_addon):
        print("[OK] sc_google_home addon found")
    else:
        print("[FAIL] sc_google_home addon missing")
        all_ok = False

    if os.path.exists(pf_addon):
        print("[OK] pf_resident_portal addon found")
    else:
        print("[FAIL] pf_resident_portal addon missing")
        all_ok = False

    if all_ok:
        print("\n[SUCCESS] System integrity verified.")
    else:
        print("\n[ERROR] System integrity check failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
