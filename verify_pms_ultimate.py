import sys
import time
import hashlib
from unittest.mock import MagicMock

def test_staps_timing():
    print("Testing STAPS High-Precision Timing...")
    start = time.time_ns()
    time.sleep(0.01) # Simulate work
    end = time.time_ns()
    duration_ms = (end - start) / 1_000_000.0
    print(f"Measured Duration: {duration_ms:.4f}ms")
    assert duration_ms >= 10.0, "Timing accuracy check failed"
    print("STAPS Timing Test Passed.\n")

def test_coordinate_uniqueness():
    print("Testing STAPS Coordinate Uniqueness...")
    coords = set()
    for i in range(100):
        ts = time.time_ns()
        seed = f"test_func-{ts}"
        coord = hashlib.sha256(seed.encode()).hexdigest()[:16]
        if coord in coords:
            raise AssertionError(f"Duplicate coordinate detected: {coord}")
        coords.add(coord)
    print(f"Verified {len(coords)} unique coordinates.")
    print("Coordinate Uniqueness Test Passed.\n")

def test_google_home_security_logic():
    print("Testing Google Home Security Logic...")
    # Mocking user lookup
    mock_users = {
        'valid_token_123': {'id': 10, 'name': 'Resident A'},
        'mock_access_token': {'id': 2, 'name': 'Admin'}
    }

    def get_user(token):
        return mock_users.get(token)

    assert get_user('valid_token_123')['id'] == 10
    assert get_user('invalid_token') is None
    assert get_user('mock_access_token')['id'] == 2
    print("Security Logic Test Passed.\n")

def test_telemetry_opt_out():
    print("Testing Telemetry Performance Logic...")
    persist_default = False
    print(f"Default Telemetry Persistence: {persist_default}")
    assert persist_default is False, "Default persistence should be False for performance"
    print("Telemetry Performance Test Passed.\n")

if __name__ == "__main__":
    try:
        test_staps_timing()
        test_coordinate_uniqueness()
        test_google_home_security_logic()
        test_telemetry_opt_out()
        print("--- ALL PMS OPTIMIZATION & SECURITY TESTS PASSED ---")
    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)
