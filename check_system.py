import os
import subprocess
import socket
import re

def check_dependencies():
    print("--- Checking Dependencies ---")
    with open('requirements.txt', 'r') as f:
        reqs = f.read()

    missing = []
    if 'requests' not in reqs:
        missing.append('requests')

    if missing:
        print(f"❌ Missing in requirements.txt: {', '.join(missing)}")
    else:
        print("✅ requirements.txt looks good")

def check_sync():
    print("\n--- Checking Module Synchronization ---")
    root_mod = "pos_beverage_modifier"
    shadow_mod = "odoo19-shadow/addons/pos_beverage_modifier"

    if not os.path.exists(root_mod) or not os.path.exists(shadow_mod):
        print("❌ One of the module paths is missing")
        return

    result = subprocess.run(["diff", "-r", root_mod, shadow_mod], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Modules are out of sync!")
        print(result.stdout)
    else:
        print("✅ Modules are synchronized")

def check_odoo_models():
    print("\n--- Checking Odoo Model Fields Integrity ---")
    model_path = "pos_beverage_modifier/models/beverage_config.py"
    if os.path.exists(model_path):
        with open(model_path, 'r') as f:
            content = f.read()

        required_fields = ["product_tmpl_id", "pos_category_id", "show_popup"]
        for field in required_fields:
            if re.search(fr"\b{field}\b\s*=", content):
                print(f"✅ Found field '{field}' in PosBeverageConfig")
            else:
                print(f"❌ Missing field '{field}' in PosBeverageConfig")

        if "class ProductTemplate(models.Model):" in content:
            print("✅ Found ProductTemplate inheritance")
        else:
            print("❌ Missing ProductTemplate inheritance")
    else:
        print("❌ Model file not found")

def check_hardcoded_js():
    print("\n--- Checking Hardcoded Logic in JS ---")
    js_path = "pos_beverage_modifier/static/src/patch/product_item_patch.js"
    if os.path.exists(js_path):
        with open(js_path, 'r') as f:
            content = f.read()
        if "computePriceExtras" in content and "extra +=" in content:
            print("⚠️ Found hardcoded price mapping in product_item_patch.js")
        else:
            print("✅ No obvious hardcoded price mapping in JS")
    else:
        print("❌ JS patch file not found")

def check_core_components():
    print("\n--- Checking Core Architectural Components ---")
    components = {
        "wuchang_master.py": "Unified CLI 'God View' dashboard",
        "renovate_system.py": "System upgrade orchestration",
        "verify_community_system.py": "Community system verification",
        "pms_base/models/staps_core.py": "STAPS high-precision timing & CNS core"
    }

    for path, desc in components.items():
        if os.path.exists(path):
            print(f"✅ Found {path} ({desc})")
        else:
            print(f"❌ Missing {path} ({desc}) (Expected finding in current repo state)")

def main():
    print("=== Rigorous System Audit Report ===")
    check_dependencies()
    check_sync()
    check_odoo_models()
    check_hardcoded_js()
    check_core_components()
    print("\n=== Audit Complete ===")

if __name__ == "__main__":
    main()
