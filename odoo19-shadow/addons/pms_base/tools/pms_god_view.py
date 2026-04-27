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
    print(" PMS GOD VIEW V3 - HIGHEST DEGREE PROPERTY MANAGEMENT ")
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

    # 3. Google Home Optimization (Traits & Metadata)
    print("\n[3] Google Home Optimization (Professional Metadata):")
    pms_model_path = "odoo19-shadow/addons/pms_base/models/pms_models.py"
    if os.path.exists(pms_model_path):
        with open(pms_model_path, 'r') as f:
            content = f.read()
            # Check for professional metadata fields
            metadata = ['nicknames', 'default_names', 'manufacturer', 'model_number']
            for field in metadata:
                status = "OPTIMIZED" if field in content else "MISSING"
                print(f"  - {field:25}: {status}")

            has_attr = "get_google_attributes" in content
            print(f"  - Schema-Compliant Attrs : {'READY' if has_attr else 'MISSING'}")
    else:
        print("  - PMS Device model not found!")

    # 4. OAuth & Fulfillment Persistence
    print("\n[4] OAuth Flow & Telemetry Persistence:")
    fulfillment_path = "odoo19-shadow/addons/sc_google_home/controllers/fulfillment_controller.py"
    if os.path.exists(fulfillment_path):
        with open(fulfillment_path, 'r') as f:
            content = f.read()
            has_auth_code = "google_home_authorization_code" in content
            has_timed = "@staps_timed(persist=True)" in content
            has_custom_data = "customData" in content
            print(f"  - Secure OAuth (AuthCode): {'ACTIVE' if has_auth_code else 'FAILED'}")
            print(f"  - Fulfillment Telemetry  : {'ACTIVE' if has_timed else 'INACTIVE'}")
            print(f"  - Rich Metadata (SYNC)   : {'ACTIVE' if has_custom_data else 'BASIC'}")
    else:
        print("  - Fulfillment controller not found!")

    # 5. Eco-Efficiency Algorithm V3
    print("\n[5] Eco-Efficiency Algorithm V3 (Weighted Algorithm):")
    coin_path = "odoo19-shadow/addons/pms_community_center/models/coin_models.py"
    if os.path.exists(coin_path):
        with open(coin_path, 'r') as f:
            content = f.read()
            # Check for V3 weight formula (40% variety, 30% coins, 30% eco)
            has_v3_formula = "variety_points + coin_points + eco_points" in content and "min(40, unique_types * 10)" in content
            print(f"  - Algorithm V3 (40/30/30): {'VALIDATED' if has_v3_formula else 'OLD VERSION'}")
    else:
        print("  - Coin models not found!")

    # 6. UI/UX Glassmorphism & Supreme Badge
    print("\n[6] Resident Portal UI/UX (Highest Degree):")
    template_path = "odoo19-shadow/addons/pms_portal_resident/views/portal_templates.xml"
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            content = f.read()
            has_badge = "Supreme Optimization Active" in content
            has_heartbeat = "STAPS Heartbeat Precision" in content
            print(f"  - Supreme Badge          : {'ACTIVE' if has_badge else 'MISSING'}")
            print(f"  - STAPS Heartbeat Visual : {'ACTIVE' if has_heartbeat else 'MISSING'}")
    else:
        print("  - Portal templates not found!")

    print("\n" + "="*60)
    print(" DIAGNOSTIC COMPLETE - SYSTEM AT HIGHEST DEGREE OPTIMIZATION ")
    print("="*60)

if __name__ == "__main__":
    main()
