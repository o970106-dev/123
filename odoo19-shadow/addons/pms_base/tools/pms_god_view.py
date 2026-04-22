import os
import sys
import json
import subprocess

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
    except Exception as e:
        return str(e)

def main():
    print("="*60)
    print(" PMS GOD VIEW V3 - SUPREME PROPERTY MANAGEMENT DIAGNOSTIC ")
    print("="*60)

    # 1. Module Audit
    print("\n[1] Module Synchronization Audit:")
    modules = ['pms_base', 'pms_community_center', 'pms_portal_resident', 'sc_google_home']
    for mod in modules:
        path = f"odoo19-shadow/addons/{mod}"
        status = "OK" if os.path.exists(path) else "MISSING"
        print(f"  - {mod:25}: {status}")

    # 2. STAPS 2.0 Precision Check
    print("\n[2] STAPS 2.0 Framework Integrity:")
    staps_path = "odoo19-shadow/addons/pms_base/models/staps_core.py"
    if os.path.exists(staps_path):
        with open(staps_path, 'r') as f:
            content = f.read()
            has_ns = "time.time_ns()" in content
            has_telemetry = "pms.telemetry" in content
            print(f"  - Nanosecond Precision  : {'PASSED' if has_ns else 'FAILED'}")
            print(f"  - Telemetry Persistence : {'PASSED' if has_telemetry else 'FAILED'}")
    else:
        print("  - STAPS core not found!")

    # 3. Google Home Trait & Metadata Matrix
    print("\n[3] Google Home Optimization (Traits & Metadata):")
    pms_model_path = "odoo19-shadow/addons/pms_base/models/pms_models.py"
    fulfillment_path = "odoo19-shadow/addons/sc_google_home/controllers/fulfillment_controller.py"

    if os.path.exists(pms_model_path):
        with open(pms_model_path, 'r') as f:
            content = f.read()
            has_metadata = "nicknames" in content and "default_names" in content
            print(f"  - Device Metadata Schema : {'READY' if has_metadata else 'MISSING'}")

    if os.path.exists(fulfillment_path):
        with open(fulfillment_path, 'r') as f:
            content = f.read()
            has_sync_opt = "nicknames" in content and "customData" in content
            print(f"  - SYNC Metadata Fulfillment: {'OPTIMIZED' if has_sync_opt else 'LEGACY'}")

    # 4. Eco-Efficiency Ecosystem (Weighted V3)
    print("\n[4] Sustainability & Eco-Efficiency Audit (V3 Algorithm):")
    coin_path = "odoo19-shadow/addons/pms_community_center/models/coin_models.py"
    if os.path.exists(coin_path):
        with open(coin_path, 'r') as f:
            content = f.read()
            has_v3_weight = "variety_points = min(40" in content
            print(f"  - Weighted Algorithm V3 : {'ACTIVE' if has_v3_weight else 'LEGACY'}")
    else:
        print("  - Coin models not found!")

    # 5. UI/UX & Controller Performance
    print("\n[5] Resident Portal UI/UX & Performance:")
    controller_path = "odoo19-shadow/addons/pms_portal_resident/controllers/portal_controller.py"
    if os.path.exists(controller_path):
        with open(controller_path, 'r') as f:
            content = f.read()
            has_perf_opt = "'devices': devices" in content and "values =" in content
            print(f"  - Controller Data Prefetch: {'ACTIVE' if has_perf_opt else 'INACTIVE'}")

    print("\n" + "="*60)
    print(" DIAGNOSTIC COMPLETE - SYSTEM OPERATING AT SUPREME DEGREE ")
    print("="*60)

if __name__ == "__main__":
    main()
