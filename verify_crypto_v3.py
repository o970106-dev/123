
from odoo19_shadow.addons.pms_base.models.staps_core import MetricTensorCryptoEngine

def verify_crypto():
    print("Starting MetricTensorCryptoEngine Verification...")
    test_ids = [1, 42, 1337, 65535, 1000000, 4294967295]

    success = True
    for tid in test_ids:
        encoded = MetricTensorCryptoEngine.encode(tid)
        decoded = MetricTensorCryptoEngine.decode(encoded)

        # Note: Hill Cipher with 2x2 matrix and mod 65536 handles 32-bit IDs
        # by splitting into two 16-bit components.
        # Ensure the test ID is within 32-bit range for this implementation.
        tid_32 = tid & 0xFFFFFFFF

        if tid_32 == decoded:
            print(f"  [PASS] ID {tid:10} -> Enc: {encoded} -> Dec: {decoded}")
        else:
            print(f"  [FAIL] ID {tid:10} -> Enc: {encoded} -> Dec: {decoded} (Expected: {tid_32})")
            success = False

    if success:
        print("\nMetricTensorCryptoEngine Integrity: VALID")
    else:
        print("\nMetricTensorCryptoEngine Integrity: CORRUPTED")
    return success

if __name__ == "__main__":
    # Mocking odoo to allow standalone script execution
    import sys
    from unittest.mock import MagicMock
    mock_odoo = MagicMock()
    sys.modules['odoo'] = mock_odoo

    # Manually adding the path to ensure import works
    import os
    sys.path.append(os.getcwd())

    # Adjusting import path for the script
    from odoo19_shadow.addons.pms_base.models.staps_core import MetricTensorCryptoEngine
    verify_crypto()
