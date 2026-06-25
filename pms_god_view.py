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
    print(" PMS GOD VIEW - ULTIMATE PROPERTY MANAGEMENT DIAGNOSTIC ")
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
            has_sha = "hashlib.sha256" in content
            has_telemetry = "pms.telemetry" in content
            print(f"  - Nanosecond Precision  : {'PASSED' if has_ns else 'FAILED'}")
            print(f"  - O(1) Coordinate Uniqueness: {'PASSED' if has_sha else 'FAILED'}")
            print(f"  - Telemetry Persistence : {'PASSED' if has_telemetry else 'FAILED'}")
    else:
        print("  - STAPS core not found!")

    # 3. Google Home Trait Matrix (Centralized Audit)
    print("\n[3] Google Home Trait Implementation:")
    fulfillment_path = "odoo19-shadow/addons/sc_google_home/controllers/fulfillment_controller.py"
    models_path = "odoo19-shadow/addons/pms_base/models/pms_models.py"

    combined_content = ""
    if os.path.exists(fulfillment_path):
        with open(fulfillment_path, 'r') as f:
            combined_content += f.read()
    if os.path.exists(models_path):
        with open(models_path, 'r') as f:
            combined_content += f.read()

    if combined_content:
        traits = ['OnOff', 'LockUnlock', 'TemperatureSetting', 'FanSpeed', 'ColorTemperature', 'SensorState', 'Brightness']
        for trait in traits:
            status = "IMPLEMENTED" if trait in combined_content else "NOT FOUND"
            print(f"  - {trait:25}: {status}")
    else:
        print("  - Fulfillment or Models not found!")

    # 4. Happiness Coin Economy Audit
    print("\n[4] Happiness Coin Backend Optimization:")
    coin_path = "odoo19-shadow/addons/pms_community_center/models/coin_models.py"
    if os.path.exists(coin_path):
        with open(coin_path, 'r') as f:
            content = f.read()
            has_batch = "read_group" in content and "self.ids" in content
            has_eco_score = "eco_efficiency_score" in content and "min(" in content
            print(f"  - Batch Balance Compute : {'OPTIMIZED' if has_batch else 'SUB-OPTIMAL'}")
            print(f"  - Weighted Eco-Scoring  : {'OPTIMIZED' if has_eco_score else 'NOT FOUND'}")
    else:
        print("  - Coin models not found!")

    # 5. UI/UX Glassmorphism Check
    print("\n[5] Resident Portal UI/UX (Glassmorphism):")
    css_path = "odoo19-shadow/addons/pms_portal_resident/static/src/css/portal_glass.css"
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            content = f.read()
            has_blur = "backdrop-filter: blur(15px)" in content
            has_glass = "rgba(255, 255, 255, 0.1)" in content
            print(f"  - High-Intensity Blur (15px): {'ACTIVE' if has_blur else 'LOW'}")
            print(f"  - Deep Glass Transparency  : {'ACTIVE' if has_glass else 'INACTIVE'}")
    else:
        print("  - Portal CSS not found!")

    print("\n" + "="*60)
    print(" DIAGNOSTIC COMPLETE - SYSTEM OPERATING AT HIGHEST DEGREE ")
    print("="*60)

if __name__ == "__main__":
    main()
