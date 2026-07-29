import time
import sys
import os
import logging
from unittest.mock import MagicMock

# Add addons path to sys.path to import modules
sys.path.append(os.path.abspath('odoo19-shadow/addons'))

# Mock Odoo environment
sys.modules['odoo'] = MagicMock()
sys.modules['odoo.http'] = MagicMock()
sys.modules['odoo.addons.pms_base.models.staps_core'] = MagicMock()

from pms_base.models.staps_core import staps_timed, timed_process, STAPSCore

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

@staps_timed
def test_operation():
    time.sleep(0.01)
    return "OK"

def run_verification():
    print("=== PMS Double J Architecture Fix Verification ===")

    # 1. Test STAPS Timing (Now actual ms)
    print("\n[Test 1] STAPS Timing Check (Actual ms):")
    test_operation()

    # 2. Test Block Timing
    print("\n[Test 2] STAPS Block Check:")
    with timed_process("Resident Portal Dashboard Load", node_id="PF-NODE"):
        time.sleep(0.005)

    # 3. Test O(1) Coordination uniqueness
    print("\n[Test 3] STAPS Coordinate Uniqueness:")
    c1 = STAPSCore.get_staps_coordinate("task1", "PM")
    c2 = STAPSCore.get_staps_coordinate("task1", "PM")
    print(f"  C1: {c1}")
    print(f"  C2: {c2}")
    if c1 != c2:
        print("  [PASS] Coordinates are unique.")
    else:
        print("  [FAIL] Coordinate collision.")

    # 4. Audit Fixes
    print("\n[Test 4] Fixes Audit:")

    # Check imports in portal controller
    from pms_portal_resident.controllers.main import PMSPortalController
    print("  [OK] PMSPortalController imported successfully (no NameError).")

    # Check Google Home routes
    from sc_google_home.controllers.main import GoogleHomeFulfillment
    print("  [OK] GoogleHomeFulfillment imported successfully.")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    run_verification()
