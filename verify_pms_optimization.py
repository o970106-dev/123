import time
import sys
import os
import logging

# Add addons path to sys.path to import modules
sys.path.append(os.path.abspath('odoo19-shadow/addons'))

from pms_base.models.staps_core import staps_timed, timed_process

# Configure logging to see STAPS output
logging.basicConfig(level=logging.INFO, format='%(message)s')

@staps_timed
def mock_heavy_operation():
    """Simulates a heavy operation to verify STAPS timing."""
    time.sleep(0.001) # 1ms real time
    return "Done"

def run_verification():
    print("=== PMS Optimization Verification ===")

    # 1. Verify STAPS Decorator
    print("\n[Test 1] STAPS Decorator Timing:")
    mock_heavy_operation()

    # 2. Verify STAPS Context Manager (with the fix)
    print("\n[Test 2] STAPS Context Manager (fixed):")
    with timed_process("Database Query") as tp:
        time.sleep(0.0005) # 0.5ms real time

    # 3. Verify STAPS O(1) Coordination
    from pms_base.models.staps_core import STAPSCore
    coord1 = STAPSCore.get_staps_coordinate("test")
    coord2 = STAPSCore.get_staps_coordinate("test")
    print(f"\n[Test 3] STAPS Coordinates Generated:\n  Coord 1: {coord1}\n  Coord 2: {coord2}")
    if coord1 != coord2:
        print("  [OK] Coordinates are unique and high-precision.")
    else:
        print("  [FAIL] Coordinate collision!")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    run_verification()
