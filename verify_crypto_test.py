import sys
import os

# Add odoo paths to sys.path
sys.path.append('odoo19-shadow/addons')

try:
    from pms_base.models.staps_core import MetricTensorCryptoEngine

    def test_crypto():
        test_ids = [1, 42, 1337, 65535, 1000000]
        print(f"{'Internal ID':<15} | {'Obfuscated Coordinate':<25} | {'Decoded ID':<15} | {'Status'}")
        print("-" * 75)
        for original_id in test_ids:
            encoded = MetricTensorCryptoEngine.encode(original_id)
            decoded = MetricTensorCryptoEngine.decode(encoded)
            status = "PASSED" if original_id == decoded else "FAILED"
            print(f"{original_id:<15} | {encoded:<25} | {decoded:<15} | {status}")

    if __name__ == "__main__":
        test_crypto()
except ImportError as e:
    print(f"Error importing MetricTensorCryptoEngine: {e}")
    print("Ensure the script is run from the repository root.")
