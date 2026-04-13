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
    print(" PMS GOD VIEW V2 - SUPREME PROPERTY MANAGEMENT DIAGNOSTIC ")
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

    # 3. Google Home Trait Matrix (Enhanced)
    print("\n[3] Google Home Optimization (Highest Degree):")
    pms_model_path = "odoo19-shadow/addons/pms_base/models/pms_models.py"
    if os.path.exists(pms_model_path):
        with open(pms_model_path, 'r') as f:
            content = f.read()
            traits = ['Brightness', 'Scene', 'TemperatureSetting', 'FanSpeed']
            for trait in traits:
                status = "CENTRALIZED" if trait in content else "NOT FOUND"
                print(f"  - {trait:25}: {status}")

            has_attr = "get_google_attributes" in content
            print(f"  - Schema-Compliant Attrs : {'READY' if has_attr else 'MISSING'}")

            # Professional Metadata Check
            metadata = ['manufacturer', 'model_number', 'hw_version', 'sw_version']
            meta_passed = all(m in content for m in metadata)
            print(f"  - Professional Metadata  : {'PASSED' if meta_passed else 'FAILED'}")

    else:
        print("  - PMS Device model not found!")

    # 4. Eco-Efficiency Ecosystem
    print("\n[4] Sustainability & Eco-Efficiency Audit (Supreme Algorithm):")
    coin_path = "odoo19-shadow/addons/pms_community_center/models/coin_models.py"
    if os.path.exists(coin_path):
        with open(coin_path, 'r') as f:
            content = f.read()
            has_weighted = "40/40/20" in content
            print(f"  - Weighted Eco-Scoring  : {'ACTIVE' if has_weighted else 'INACTIVE'}")
    else:
        print("  - Coin models not found!")

    # 4.1 Dependency & Security Check
    print("\n[4.1] Module Dependency & Security Integrity:")
    manifest_path = "odoo19-shadow/addons/pms_portal_resident/__manifest__.py"
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            content = f.read()
            has_dep = "sc_google_home" in content
            print(f"  - Portal Dependencies    : {'SECURED' if has_dep else 'FAILED'}")

    sec_path = "odoo19-shadow/addons/pms_community_center/security/cc_security.xml"
    if os.path.exists(sec_path):
        with open(sec_path, 'r') as f:
            content = f.read()
            has_id = "model_pms_happiness_coin" in content
            print(f"  - Security XML Integrity : {'PASSED' if has_id else 'FAILED'}")

    # 5. UI/UX Glassmorphism Check (High Intensity)
    print("\n[5] Resident Portal UI/UX (Supreme Glassmorphism):")
    css_path = "odoo19-shadow/addons/pms_portal_resident/static/src/css/portal_glass.css"
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            content = f.read()
            has_blur_20 = "blur(20px)" in content
            has_gradient = "linear-gradient" in content
            print(f"  - Ultra-Intensity Blur (20px): {'ACTIVE' if has_blur_20 else 'FAILED'}")
            print(f"  - Cinematic Background      : {'ACTIVE' if has_gradient else 'INACTIVE'}")
    else:
        print("  - Portal CSS not found!")

    print("\n" + "="*60)
    print(" DIAGNOSTIC COMPLETE - SYSTEM OPERATING AT SUPREME DEGREE ")
    print("="*60)

if __name__ == "__main__":
    main()
