import sys
import os

def check_file(path, search_terms):
    if not os.path.exists(path):
        print(f"FAILED: {path} not found")
        return False
    with open(path, 'r') as f:
        content = f.read()
        for term in search_terms:
            if term not in content:
                print(f"FAILED: {term} not found in {path}")
                return False
    print(f"PASSED: {path} contains all search terms")
    return True

def main():
    print("PMS HIGHEST DEGREE V2 FUNCTIONAL AUDIT")
    print("======================================")

    # Check Sensor in pms_models.py
    check_file("odoo19-shadow/addons/pms_base/models/pms_models.py",
               ["'action.devices.types.SENSOR'", "humidity", "occupancy", "'action.devices.traits.SensorState'"])

    # Check fulfillment for sensors
    check_file("odoo19-shadow/addons/sc_google_home/controllers/fulfillment_controller.py",
               ["currentSensorStateData", "currentDescriptiveState", "rawValue", "https://oauth-redirect.googleusercontent.com/"])

    # Check volunteering in coin_models.py
    check_file("odoo19-shadow/addons/pms_community_center/models/coin_models.py",
               ["class PmsSkill", "x_is_volunteer", "x_volunteer_skills", "required_skill_id"])

    # Check portal routes
    check_file("odoo19-shadow/addons/pms_portal_resident/controllers/portal_controller.py",
               ["toggle_volunteer", "add_skill"])

    # Check portal UI
    check_file("odoo19-shadow/addons/pms_portal_resident/views/portal_templates.xml",
               ["Volunteer Center", "Metric Tensor Telemetry", "device.humidity"])

if __name__ == '__main__':
    main()
