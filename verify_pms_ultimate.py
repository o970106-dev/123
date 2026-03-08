import time
import hashlib

def get_staps_coordinate(action_name):
    ts = time.time_ns()
    raw = f"{action_name}-{ts}"
    return hashlib.sha256(raw.encode()).hexdigest()

def test_staps_performance():
    print("Testing STAPS 2.0 O(1) Performance...")
    iterations = 1000
    start = time.perf_counter()
    coords = set()
    for i in range(iterations):
        coord = get_staps_coordinate("test_action")
        coords.add(coord)
    duration = (time.perf_counter() - start) * 1000 / iterations

    print(f"Average STAPS Latency: {duration:.6f}ms")
    print(f"Coordinate Uniqueness: {len(coords)}/{iterations}")

    if duration < 0.05:
        print("✅ Performance Target Met (< 0.05ms)")
    else:
        print("❌ Performance Target Failed")

if __name__ == "__main__":
    test_staps_performance()
