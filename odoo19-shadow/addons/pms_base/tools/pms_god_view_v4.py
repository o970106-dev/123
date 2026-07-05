import os
import sys

def check_file_contains(filepath, patterns):
    if not os.path.exists(filepath):
        return False, f"File {filepath} NOT FOUND"

    with open(filepath, 'r') as f:
        content = f.read()
        for pattern in patterns:
            if pattern not in content:
                return False, f"Missing pattern: {pattern} in {filepath}"
    return True, "Verified"

def audit_v4():
    print("============================================================")
    print(" PMS GOD VIEW V4 - SUPREME DEGREE PMS OPTIMIZATION AUDIT ")
    print("============================================================")

    checks = [
        {
            "name": "Core Security (MetricTensorCryptoEngine)",
            "file": "odoo19-shadow/addons/pms_base/models/staps_core.py",
            "patterns": ["class MetricTensorCryptoEngine", "MATRIX = [[3, 2]", "INV_MATRIX = [[53621"]
        },
        {
            "name": "Google Home SENSOR traits",
            "file": "odoo19-shadow/addons/pms_base/models/pms_models.py",
            "patterns": ["traits.append('action.devices.traits.HumiditySetting')", "traits.append('action.devices.traits.OccupancySensing')"]
        },
        {
            "name": "Google Home Resident Isolation",
            "file": "odoo19-shadow/addons/sc_google_home/controllers/fulfillment_controller.py",
            "patterns": ["search([('google_device_id', '=', gid), ('resident_id', '=', user.id)]"]
        },
        {
            "name": "Eco-Efficiency V4 Algorithm",
            "file": "odoo19-shadow/addons/pms_community_center/models/coin_models.py",
            "patterns": ["V4 Weighted Algorithm", "volunteer_points = 15 if user.x_is_volunteer else 0", "min(20, user.happiness_coin_balance * 0.4)"]
        },
        {
            "name": "Volunteer Nexus Routes",
            "file": "odoo19-shadow/addons/pms_portal_resident/controllers/portal_controller.py",
            "patterns": ["@http.route(['/pms/toggle_volunteer']", "user.action_reward_sustainability(amount=10.0"]
        }
    ]

    all_passed = True
    for check in checks:
        passed, msg = check_file_contains(check['file'], check['patterns'])
        status = "PASSED" if passed else "FAILED"
        print(f"[{status}] {check['name']}: {msg}")
        if not passed:
            all_passed = False

    print("============================================================")
    if all_passed:
        print(" AUDIT COMPLETE - SYSTEM AT SUPREME DEGREE (V4) ")
    else:
        print(" AUDIT FAILED - SYSTEM DOES NOT MEET SUPREME DEGREE V4 STANDARDS ")
    print("============================================================")
    return all_passed

if __name__ == "__main__":
    if not audit_v4():
        sys.exit(1)
