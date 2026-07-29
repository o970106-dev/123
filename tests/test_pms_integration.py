import unittest
import json
import time
from pms_coordination import engine, STAPS_MULTIPLIER

class TestPMSIntegration(unittest.TestCase):

    def test_staps_multiplier(self):
        """Verify the STAPS engineering multiplier is correctly set to 8."""
        self.assertEqual(STAPS_MULTIPLIER, 8)

    def test_coordinate_mapping(self):
        """Verify SHA-256 coordinate mapping for O(1) indexing."""
        coord1 = engine.get_absolute_coordinate("node_a")
        coord2 = engine.get_absolute_coordinate("node_a")
        coord3 = engine.get_absolute_coordinate("node_b")

        self.assertEqual(coord1, coord2)
        self.assertNotEqual(coord1, coord3)
        self.assertEqual(len(coord1), 64)

    def test_latency_threshold(self):
        """Ensure CNS signal transmission is near-instant."""
        start = time.perf_counter()
        engine.get_absolute_coordinate("test_signal")
        latency = (time.perf_counter() - start) * 1000

        # Target is < 0.1ms for local coordinate mapping
        self.assertLess(latency, 0.5)
        print(f"Verified CNS Latency: {latency:.4f}ms")

    def test_broadcast_structure(self):
        """Verify the broadcast signal structure."""
        msg = engine.broadcast_signal("power_alert", {"status": "critical"})
        self.assertEqual(msg['channel'], "power_alert")
        self.assertIn("coordinate", msg)
        self.assertEqual(msg['payload']['status'], "critical")

if __name__ == "__main__":
    unittest.main()
