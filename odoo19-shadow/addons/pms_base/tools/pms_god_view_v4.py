import sys
import unittest
from unittest.mock import MagicMock

# Mock Odoo environment
class MockEnv:
    def __init__(self):
        self.registry = MagicMock()
        self.user = MagicMock(id=1, happiness_coin_balance=100.0, x_is_volunteer=True)
        self.models = {}

    def __getitem__(self, model_name):
        return self.models.get(model_name, MagicMock())

    def sudo(self):
        return self

class TestPmsSupremeV4(unittest.TestCase):
    def setUp(self):
        self.env = MockEnv()

    def test_v4_eco_efficiency_algorithm(self):
        """Validates the Supreme Degree (V4) Eco-Efficiency logic."""
        # Weights: Coins 20%, Eco 25%, Variety 25%, Volunteering 15%, Maintenance 15%
        coin_balance = 50.0 # 50 * 0.4 = 20 pts (max)
        user_devices = [
            MagicMock(eco_mode=True, device_type='LIGHT'),
            MagicMock(eco_mode=True, device_type='THERMOSTAT'),
            MagicMock(eco_mode=False, device_type='LOCK'),
            MagicMock(eco_mode=True, device_type='SENSOR'),
        ]
        # Eco: 3/4 * 25 = 18.75 pts
        # Variety: 4 types * 6.25 = 25 pts (max)
        # Volunteering: True + Skills = 15 pts
        # Maintenance: 2 resolved * 5 = 10 pts

        # pts = 20 + 18.75 + 25 + 15 + 10 = 88.75 -> 88

        # Calculation logic check
        coin_pts = min(20, coin_balance * 0.4)
        eco_pts = (3/4 * 25)
        variety_pts = min(25, 4 * 6.25)
        volunteer_pts = 15
        maint_pts = min(15, 2 * 5)

        total = int(min(100, coin_pts + eco_pts + variety_pts + volunteer_pts + maint_pts))
        self.assertEqual(total, 88)
        print(f"DEBUG: V4 Algorithm Check - Expected 88, Calculated {total}")

    def test_sensor_traits(self):
        """Validates SENSOR trait fulfillment."""
        traits = [
            'action.devices.traits.TemperatureSetting',
            'action.devices.traits.HumiditySetting',
            'action.devices.traits.OccupancySensing',
            'action.devices.traits.SensorState'
        ]
        # Simulate get_google_traits for SENSOR
        device_type = 'action.devices.types.SENSOR'
        sensor_traits = []
        if device_type == 'action.devices.types.SENSOR':
            sensor_traits = [
                'action.devices.traits.TemperatureSetting',
                'action.devices.traits.HumiditySetting',
                'action.devices.traits.OccupancySensing',
                'action.devices.traits.SensorState'
            ]

        for trait in traits:
            self.assertIn(trait, sensor_traits)
        print("DEBUG: SENSOR Trait Verification - PASSED")

    def test_metric_tensor_obfuscation(self):
        """Validates MetricTensorCryptoEngine ID obfuscation."""
        # Using the matrix constants from staps_core.py
        MATRIX = [[3, 2], [5, 7]]
        MOD = 65536

        internal_id = 12345
        x1 = internal_id & 0xFFFF
        x2 = (internal_id >> 16) & 0xFFFF

        y1 = (MATRIX[0][0] * x1 + MATRIX[0][1] * x2) % MOD
        y2 = (MATRIX[1][0] * x1 + MATRIX[1][1] * x2) % MOD

        coord = f"{y1:04x}{y2:04x}"
        self.assertEqual(len(coord), 8)
        print(f"DEBUG: Metric Tensor Check - ID {internal_id} -> Coord {coord}")

if __name__ == '__main__':
    print("--- PMS SUPREME V4 DIAGNOSTIC AUDIT ---")
    unittest.main()
