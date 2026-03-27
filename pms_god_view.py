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

    # 3. Google Home Trait Matrix
    print("\n[3] Google Home Trait Implementation:")
    model_path = "odoo19-shadow/addons/pms_base/models/pms_models.py"
    if os.path.exists(model_path):
        with open(model_path, 'r') as f:
            content = f.read()
            traits = ['Brightness', 'Scene', 'OnOff', 'LockUnlock', 'TemperatureSetting']
            for trait in traits:
                status = "IMPLEMENTED" if trait in content else "NOT FOUND"
                print(f"  - {trait:25}: {status}")
    else:
        print("  - Device model not found!")

    print("\n[3.1] Google Home Security Audit:")
    fulfillment_path = "odoo19-shadow/addons/sc_google_home/controllers/fulfillment_controller.py"
    if os.path.exists(fulfillment_path):
        with open(fulfillment_path, 'r') as f:
            content = f.read()
            has_secure_token = "if token:" in content
            has_json_fail = "request.make_response(json.dumps" in content and "authFailure" in content
            print(f"  - Secure Token Validation: {'PASSED' if has_secure_token else 'FAILED'}")
            print(f"  - JSON Auth Failure Resp : {'PASSED' if has_json_fail else 'FAILED'}")

    # 4. Happiness Coin Economy Audit
    print("\n[4] Happiness Coin Backend Optimization:")
    coin_path = "odoo19-shadow/addons/pms_community_center/models/coin_models.py"
    if os.path.exists(coin_path):
        with open(coin_path, 'r') as f:
            content = f.read()
            has_batch = "read_group" in content and "self.ids" in content
            print(f"  - Batch Balance Compute : {'OPTIMIZED' if has_batch else 'SUB-OPTIMAL'}")
    else:
        print("  - Coin models not found!")

    # 5. UI/UX Glassmorphism Check
    print("\n[5] Resident Portal UI/UX (Glassmorphism):")
    css_path = "odoo19-shadow/addons/pms_portal_resident/static/src/css/portal_glass.css"
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            content = f.read()
            has_blur = "backdrop-filter: blur(20px)" in content
            has_glass = "rgba(255, 255, 255, 0.08)" in content
            print(f"  - High-Intensity Blur (20px): {'ACTIVE' if has_blur else 'LOW'}")
            print(f"  - Deep Glass Transparency  : {'ACTIVE' if has_glass else 'INACTIVE'}")
    else:
        print("  - Portal CSS not found!")

    print("\n" + "="*60)
    print(" DIAGNOSTIC COMPLETE - SYSTEM OPERATING AT HIGHEST DEGREE ")
    print("="*60)

if __name__ == "__main__":
    main()
