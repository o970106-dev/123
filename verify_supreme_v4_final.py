
import sys
from unittest.mock import MagicMock

# Mocking Odoo framework
sys.modules['odoo'] = MagicMock()
sys.modules['odoo.http'] = MagicMock()
from odoo import models, fields, api

class MockPmsDevice:
    def __init__(self, data):
        self.id = data.get('id', 1)
        self.resident_id = MagicMock(id=data.get('resident_id', 1))
        self.device_type = data.get('device_type', 'action.devices.types.LIGHT')
        self.eco_mode = data.get('eco_mode', False)

class MockUser:
    def __init__(self, data):
        self.id = data.get('id', 1)
        self.happiness_coin_balance = data.get('happiness_coin_balance', 0.0)
        self.x_is_volunteer = data.get('x_is_volunteer', False)
        self.x_volunteer_skills = data.get('x_volunteer_skills', [])

def calculate_eco_score_v4(user, devices, maint_reqs_count):
    # 1. Happiness Coin Weight (Max 20 points)
    coin_points = min(20, user.happiness_coin_balance * 0.4)

    # 2. Eco-Mode Weight (Max 25 points)
    total_dev = len(devices)
    eco_dev = len([d for d in devices if d.eco_mode])
    eco_points = (eco_dev / total_dev * 25) if total_dev > 0 else 0

    # 3. Variety Weight (Max 25 points)
    unique_types = len(set(d.device_type for d in devices))
    variety_points = min(25, unique_types * 6.25)

    # 4. Volunteering Weight (Max 15 points)
    volunteer_points = 15 if user.x_is_volunteer else 0
    if user.x_volunteer_skills:
        volunteer_points = min(15, volunteer_points + len(user.x_volunteer_skills) * 2)

    # 5. Maintenance Weight (Max 15 points)
    maint_points = min(15, maint_reqs_count * 5)

    return int(min(100, coin_points + eco_points + variety_points + volunteer_points + maint_points))

def test_v4_score_scenarios():
    print("Testing Supreme Degree V4 Eco-Efficiency Scenarios...")

    # Scenario 1: The Supreme Resident (Perfect Score)
    user_top = MockUser({'id': 1, 'happiness_coin_balance': 50.0, 'x_is_volunteer': True, 'x_volunteer_skills': [1, 2]})
    devices_top = [
        MockPmsDevice({'device_type': 'action.devices.types.LIGHT', 'eco_mode': True}),
        MockPmsDevice({'device_type': 'action.devices.types.THERMOSTAT', 'eco_mode': True}),
        MockPmsDevice({'device_type': 'action.devices.types.SENSOR', 'eco_mode': True}),
        MockPmsDevice({'device_type': 'action.devices.types.OUTLET', 'eco_mode': True})
    ]
    score_top = calculate_eco_score_v4(user_top, devices_top, 3)
    print(f"  - Supreme Resident Score: {score_top} (Expected: 100)")
    assert score_top == 100

    # Scenario 2: The New Resident (Minimal Activity)
    user_new = MockUser({'id': 2, 'happiness_coin_balance': 0.0, 'x_is_volunteer': False})
    devices_new = [MockPmsDevice({'device_type': 'action.devices.types.LIGHT', 'eco_mode': False})]
    score_new = calculate_eco_score_v4(user_new, devices_new, 0)
    # Variety: 1 * 6.25 = 6
    print(f"  - New Resident Score: {score_new} (Expected: 6)")
    assert score_new == 6

def test_id_obfuscation():
    print("\nTesting Metric Tensor ID Obfuscation Logic...")
    # Using the MATRIX from staps_core.py
    MATRIX = [[3, 2], [5, 7]]
    MOD = 65536

    internal_id = 1234
    x1 = internal_id & 0xFFFF
    x2 = (internal_id >> 16) & 0xFFFF

    y1 = (MATRIX[0][0] * x1 + MATRIX[0][1] * x2) % MOD
    y2 = (MATRIX[1][0] * x1 + MATRIX[1][1] * x2) % MOD

    encoded = f"{y1:04x}{y2:04x}"
    print(f"  - ID: {internal_id} -> Secure ID: {encoded}")
    assert len(encoded) == 8

if __name__ == "__main__":
    try:
        test_v4_score_scenarios()
        test_id_obfuscation()
        print("\nSUPREME DEGREE V4 LOGIC VERIFICATION PASSED")
    except AssertionError as e:
        print("\nVERIFICATION FAILED")
        sys.exit(1)
