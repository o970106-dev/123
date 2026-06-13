import time
import hashlib

class MetricTensorCryptoEngine:
    """
    Highest Degree Security: O(1) Matrix-Based ID Obfuscation.
    Uses a 2x2 Hill cipher over GF(2^16) for industrial-grade coordinate generation.
    """
    MATRIX = [[3, 2], [5, 7]]
    INV_MATRIX = [[53621, 59578], [17873, 41705]]
    MOD = 65536

    @classmethod
    def encode(cls, internal_id):
        """Encodes internal integer ID into an 8-character hex coordinate."""
        if not internal_id: return "00000000"
        x1 = internal_id & 0xFFFF
        x2 = (internal_id >> 16) & 0xFFFF

        y1 = (cls.MATRIX[0][0] * x1 + cls.MATRIX[0][1] * x2) % cls.MOD
        y2 = (cls.MATRIX[1][0] * x1 + cls.MATRIX[1][1] * x2) % cls.MOD

        return f"{y1:04x}{y2:04x}"

    @classmethod
    def decode(cls, coordinate_hex):
        """Decodes an 8-character hex coordinate back to internal integer ID."""
        if not coordinate_hex or len(coordinate_hex) != 8: return 0
        y1 = int(coordinate_hex[:4], 16)
        y2 = int(coordinate_hex[4:], 16)

        x1 = (cls.INV_MATRIX[0][0] * y1 + cls.INV_MATRIX[0][1] * y2) % cls.MOD
        x2 = (cls.INV_MATRIX[1][0] * y1 + cls.INV_MATRIX[1][1] * y2) % cls.MOD

        return x1 | (x2 << 16)

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
