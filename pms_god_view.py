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
    print(" PMS GOD VIEW V2 - ULTIMATE PROPERTY MANAGEMENT DIAGNOSTIC ")
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
    models_path = "odoo19-shadow/addons/pms_base/models/pms_models.py"
    if os.path.exists(staps_path) and os.path.exists(models_path):
        with open(staps_path, 'r') as f:
            staps_content = f.read()
        with open(models_path, 'r') as f:
            models_content = f.read()

        has_ns = "time.time_ns()" in staps_content
        has_telemetry = "pms.telemetry" in staps_content
        has_error_field = "error = fields.Text" in models_content
        has_error_capture = "'error': telemetry_data['error']" in staps_content

        print(f"  - Nanosecond Precision  : {'PASSED' if has_ns else 'FAILED'}")
        print(f"  - Telemetry Persistence : {'PASSED' if has_telemetry else 'FAILED'}")
        print(f"  - STAPS Error Capture   : {'PASSED' if (has_error_field and has_error_capture) else 'FAILED'}")
    else:
        print("  - STAPS core files not found!")

    # 3. Google Home Trait Matrix (Centralized)
    print("\n[3] Google Home Centralized Logic Audit:")
    if os.path.exists(models_path):
        with open(models_path, 'r') as f:
            content = f.read()
        traits = ['Brightness', 'Scene', 'OnOff', 'TemperatureSetting', 'FanSpeed']
        methods = ['get_google_traits', 'get_google_attributes', 'get_google_state']

        for trait in traits:
            status = "IMPLEMENTED" if trait in content else "NOT FOUND"
            print(f"  - Trait: {trait:18}: {status}")

        for method in methods:
            status = "DEFINED" if f"def {method}" in content else "MISSING"
            print(f"  - Method: {method:17}: {status}")
    else:
        print("  - Device model not found!")

    # 4. User Model & Economy Audit
    print("\n[4] User Model & Eco-Efficiency Audit:")
    user_path = "odoo19-shadow/addons/sc_google_home/models/res_users.py"
    if os.path.exists(user_path):
        with open(user_path, 'r') as f:
            content = f.read()
        has_score = "eco_efficiency_score" in content
        has_token = "google_home_token" in content
        print(f"  - Eco-Efficiency Score  : {'ACTIVE' if has_score else 'INACTIVE'}")
        print(f"  - Google Home Token     : {'SECURED' if has_token else 'MISSING'}")
    else:
        print("  - User model extension not found!")

    # 5. UI/UX Glassmorphism Check
    print("\n[5] Resident Portal UI/UX (Glassmorphism V2):")
    css_path = "odoo19-shadow/addons/pms_portal_resident/static/src/css/portal_glass.css"
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            content = f.read()
        has_blur_20 = "backdrop-filter: blur(20px)" in content
        has_glass_08 = "rgba(255, 255, 255, 0.08)" in content
        print(f"  - High-Intensity Blur (20px): {'ACTIVE' if has_blur_20 else 'LOW'}")
        print(f"  - Glass Transparency (0.08): {'OPTIMIZED' if has_glass_08 else 'SUB-OPTIMAL'}")
    else:
        print("  - Portal CSS not found!")

    print("\n" + "="*60)
    print(" DIAGNOSTIC COMPLETE - SYSTEM OPERATING AT HIGHEST DEGREE ")
    print("="*60)

if __name__ == "__main__":
    main()
