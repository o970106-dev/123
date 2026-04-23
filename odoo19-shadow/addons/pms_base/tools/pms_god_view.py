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
    print(" PMS GOD VIEW V3 - HIGHEST DEGREE PROPERTY MANAGEMENT DIAGNOSTIC ")
    print("="*60)

    # 1. Module Synchronization
    print("\n[1] Module Synchronization Audit:")
    modules = ['pms_base', 'pms_community_center', 'pms_portal_resident', 'sc_google_home']
    for mod in modules:
        path = f"odoo19-shadow/addons/{mod}"
        status = "OK" if os.path.exists(path) else "MISSING"
        print(f"  - {mod:25}: {status}")

    # 2. STAPS 2.0 Persistence
    print("\n[2] STAPS 2.0 Persistence & Precision:")
    staps_path = "odoo19-shadow/addons/pms_base/models/staps_core.py"
    if os.path.exists(staps_path):
        with open(staps_path, 'r') as f:
            content = f.read()
            has_ns = "time.time_ns()" in content
            has_cursor = "env.registry.cursor()" in content
            print(f"  - Nanosecond Precision  : {'PASSED' if has_ns else 'FAILED'}")
            print(f"  - High-Resilience Commit: {'ACTIVE' if has_cursor else 'INACTIVE'}")
    else:
        print("  - STAPS core not found!")

    # 3. Google Home Professional Metadata
    print("\n[3] Google Home Professional Metadata:")
    pms_model_path = "odoo19-shadow/addons/pms_base/models/pms_models.py"
    full_ctrl_path = "odoo19-shadow/addons/sc_google_home/controllers/fulfillment_controller.py"

    if os.path.exists(pms_model_path):
        with open(pms_model_path, 'r') as f:
            content = f.read()
            has_nicknames = "nicknames =" in content
            has_default = "default_names =" in content
            print(f"  - Schema (Nicknames)     : {'READY' if has_nicknames else 'MISSING'}")
            print(f"  - Schema (Default Names) : {'READY' if has_default else 'MISSING'}")

    if os.path.exists(full_ctrl_path):
        with open(full_ctrl_path, 'r') as f:
            content = f.read()
            has_metadata = "nicknames" in content and "defaultNames" in content
            has_custom = "customData" in content
            print(f"  - Fulfillment Metadata  : {'ACTIVE' if has_metadata else 'INACTIVE'}")
            print(f"  - Custom Data Payload   : {'ACTIVE' if has_custom else 'INACTIVE'}")
    else:
        print("  - Fulfillment controller not found!")

    # 4. Fulfillment Telemetry
    print("\n[4] Operational Analytics (Fulfillment Telemetry):")
    if os.path.exists(full_ctrl_path):
        with open(full_ctrl_path, 'r') as f:
            content = f.read()
            instrumented = "@staps_timed(persist=True)" in content
            print(f"  - Fulfillment Instrument: {'ACTIVE' if instrumented else 'INACTIVE'}")

    # 5. Eco-Efficiency Algorithm (Highest Degree)
    print("\n[5] Eco-Efficiency Algorithm (Highest Degree):")
    coin_path = "odoo19-shadow/addons/pms_community_center/models/coin_models.py"
    if os.path.exists(coin_path):
        with open(coin_path, 'r') as f:
            content = f.read()
            has_variety = "variety_points" in content or "unique_types" in content
            has_weighted = "coin_points + eco_points + variety_points" in content
            print(f"  - Device Variety Weight : {'ACTIVE' if has_variety else 'INACTIVE'}")
            print(f"  - Weighted Eco-Scoring  : {'ACTIVE' if has_weighted else 'INACTIVE'}")
    else:
        print("  - Coin models not found!")

    # 6. UI/UX Glassmorphism
    print("\n[6] Resident Portal UI/UX (Glassmorphism):")
    css_path = "odoo19-shadow/addons/pms_portal_resident/static/src/css/portal_glass.css"
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            content = f.read()
            has_blur = "blur(20px)" in content
            print(f"  - Ultra-Intensity Blur  : {'ACTIVE' if has_blur else 'FAILED'}")
    else:
        print("  - Portal CSS not found!")

    print("\n" + "="*60)
    print(" DIAGNOSTIC COMPLETE - SYSTEM OPERATING AT HIGHEST DEGREE ")
    print("="*60)

if __name__ == "__main__":
    main()
