class MetricTensorCryptoEngine:
    MATRIX = [[3, 2], [5, 7]]
    INV_MATRIX = [[53621, 59578], [17873, 41705]]
    MOD = 65536

    @classmethod
    def encode(cls, internal_id):
        if not internal_id: return "00000000"
        x1 = internal_id & 0xFFFF
        x2 = (internal_id >> 16) & 0xFFFF
        y1 = (cls.MATRIX[0][0] * x1 + cls.MATRIX[0][1] * x2) % cls.MOD
        y2 = (cls.MATRIX[1][0] * x1 + cls.MATRIX[1][1] * x2) % cls.MOD
        return f"{y1:04x}{y2:04x}"

    @classmethod
    def decode(cls, coordinate_hex):
        if not coordinate_hex or len(coordinate_hex) != 8: return 0
        y1 = int(coordinate_hex[:4], 16)
        y2 = int(coordinate_hex[4:], 16)
        x1 = (cls.INV_MATRIX[0][0] * y1 + cls.INV_MATRIX[0][1] * y2) % cls.MOD
        x2 = (cls.INV_MATRIX[1][0] * y1 + cls.INV_MATRIX[1][1] * y2) % cls.MOD
        return x1 | (x2 << 16)

test_ids = [1, 42, 1337, 65535, 1000000, 4294967295]
for tid in test_ids:
    encoded = MetricTensorCryptoEngine.encode(tid)
    decoded = MetricTensorCryptoEngine.decode(encoded)
    tid_32 = tid & 0xFFFFFFFF
    status = "PASS" if tid_32 == decoded else "FAIL"
    print(f"[{status}] {tid} -> {encoded} -> {decoded}")
