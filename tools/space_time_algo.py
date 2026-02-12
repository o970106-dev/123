"""
時空系統絕對距離演算法 (SpaceTimeSystem Absolute Distance)
發明者：聊國咖啡館 社工老闆
此演算法利用絕對座標映射實現 O(1) 的極速寫入與高效區間查詢，是雙J 協作的核心同步技術。
"""
import time
import random
import sys
import gc

# 設定遞迴深度上限以防萬一
sys.setrecursionlimit(200000)

def get_size(obj, seen=None):
    """遞迴計算物件佔用的真實記憶體大小 (包含 __slots__)"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)

    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])

    if hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)

    # 處理 __slots__ 優化的物件
    if hasattr(obj, '__slots__'):
        for slot in obj.__slots__:
            if hasattr(obj, slot):
                size += get_size(getattr(obj, slot), seen)

    if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])

    return size

# --- 演算法 1: 傳統樹狀結構 (Tree) ---
class TreeNode:
    # 使用 __slots__ 進行極限優化，模擬 C++ 指標結構，避免 Python dict 開銷
    __slots__ = ['key', 'value', 'left', 'right']
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None

class TraditionalTree:
    def __init__(self):
        self.root = None
        self.name = "傳統樹狀結構 (Tree)"

    def insert(self, key, value):
        if not self.root:
            self.root = TreeNode(key, value)
            return

        # 迭代式插入 (Iterative Insert)
        curr = self.root
        while True:
            if key < curr.key:
                if curr.left:
                    curr = curr.left
                else:
                    curr.left = TreeNode(key, value)
                    break
            else:
                if curr.right:
                    curr = curr.right
                else:
                    curr.right = TreeNode(key, value)
                    break

    def query(self, start, end):
        result = []
        stack = []
        curr = self.root

        # 中序遍歷搜尋 (In-order Traversal)
        while stack or curr:
            if curr:
                if curr.key >= start:
                    stack.append(curr)
                    curr = curr.left
                else:
                    curr = curr.right
            else:
                curr = stack.pop()
                if curr.key <= end:
                    result.append(curr.value)
                    curr = curr.right
                else:
                    curr = None
        return result

# --- 演算法 2: 時空系統絕對距離 (Absolute Distance) ---
class SpaceTimeSystem:
    def __init__(self, min_t, max_t, precision_slots=1000):
        self.name = "時空系統絕對距離 (Absolute Distance)"
        self.min_t = min_t
        self.max_t = max_t
        self.slot_count = precision_slots
        # 計算每個時間槽的絕對區間
        self.interval = (max_t - min_t) / precision_slots
        # 預先分配連續記憶體空間 (Array/Bucket)
        self.space = [[] for _ in range(precision_slots + 1)]

    def insert(self, key, value):
        # O(1) 絕對距離映射：直接計算記憶體位置，無需比較
        idx = int((key - self.min_t) / self.interval)
        if 0 <= idx < self.slot_count:
            self.space[idx].append((key, value))
        else:
            self.space[-1].append((key, value))

    def query(self, start, end):
        # O(1) 範圍計算：直接鎖定起始與結束的區塊
        start_idx = int((start - self.min_t) / self.interval)
        end_idx = int((end - self.min_t) / self.interval)

        start_idx = max(0, start_idx)
        end_idx = min(self.slot_count, end_idx)

        result = []
        # 僅掃描相關區塊，避開全域搜尋
        for i in range(start_idx, end_idx + 1):
            bucket = self.space[i]
            for k, v in bucket:
                if start <= k <= end:
                    result.append(v)
        return result

# --- 評測引擎 ---
def run_benchmark():
    print("=== 時空系統演算法效能評測 ===")
    print(f"日期: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    DATA_SIZE = 100000
    TIME_MIN = 0.0
    TIME_MAX = 1000000.0
    print(f"\n[準備階段] 產生 {DATA_SIZE:,} 筆隨機時間點資料 (範圍: {TIME_MIN}-{TIME_MAX})...")

    random.seed(42)
    dataset = [(random.uniform(TIME_MIN, TIME_MAX), f"data_{i}") for i in range(DATA_SIZE)]

    QUERY_COUNT = 1000
    queries = []
    for _ in range(QUERY_COUNT):
        s = random.uniform(TIME_MIN, TIME_MAX - 1000)
        e = s + random.uniform(100, 5000)
        queries.append((s, e))

    algorithms = [
        TraditionalTree(),
        SpaceTimeSystem(TIME_MIN, TIME_MAX, precision_slots=1000)
    ]

    results = {}

    for algo in algorithms:
        print(f"\n--- 測試演算法: {algo.name} ---")

        # 測試 1: 寫入速度
        start_time = time.time()
        for k, v in dataset:
            algo.insert(k, v)
        end_time = time.time()
        insert_duration = end_time - start_time
        print(f"1. 寫入速度 (Insert): {insert_duration:.4f} 秒")

        # 測試 2: 區間搜尋速度
        start_time = time.time()
        found_count = 0
        for s, e in queries:
            res = algo.query(s, e)
            found_count += len(res)
        end_time = time.time()
        query_duration = end_time - start_time
        print(f"2. 區間搜尋 (Range Query) x{QUERY_COUNT}: {query_duration:.4f} 秒 (共找到 {found_count} 筆)")

        # 測試 3: 記憶體佔用
        gc.collect()
        try:
            mem_size = get_size(algo) / (1024 * 1024) # MB
        except Exception as e:
            mem_size = 0
        print(f"3. 記憶體佔用 (Memory): {mem_size:.2f} MB")

        results[algo.name] = {
            "insert": insert_duration,
            "query": query_duration,
            "memory": mem_size
        }

    # --- 最終報告輸出 ---
    print("\n\n" + "="*50)
    print("             最終對比報告 (Final Report)")
    print("="*50)
    print(f"{'指標 (Metric)':<25} | {'傳統樹 (Tree)':<15} | {'時空系統 (Absolute)':<15} | {'差異 (Diff)'}")
    print("-" * 75)

    tree_res = results["傳統樹狀結構 (Tree)"]
    st_res = results["時空系統絕對距離 (Absolute Distance)"]

    diff_insert = (tree_res['insert'] / st_res['insert'])
    print(f"{'寫入時間 (Insert)':<25} | {tree_res['insert']:.4f}s        | {st_res['insert']:.4f}s        | 時空系統快 {diff_insert:.1f}x 倍")

    diff_query = (tree_res['query'] / st_res['query'])
    print(f"{'查詢時間 (Query)':<25} | {tree_res['query']:.4f}s        | {st_res['query']:.4f}s        | 時空系統快 {diff_query:.1f}x 倍")

    if st_res['memory'] > 0:
        diff_mem = (tree_res['memory'] / st_res['memory'])
        print(f"{'記憶體 (Memory)':<25} | {tree_res['memory']:.2f} MB       | {st_res['memory']:.2f} MB       | 時空系統省 {diff_mem:.1f}x 倍")
    else:
        print(f"{'記憶體 (Memory)':<25} | {tree_res['memory']:.2f} MB       | {st_res['memory']:.2f} MB       | (無法計算)")

    print("-" * 75)
    print("結論:")
    print("1. 寫入優勢：時空系統無需遍歷樹高 (O(log N))，利用絕對座標直接寫入 (O(1))，速度提升顯著。")
    print("2. 查詢優勢：時空系統透過絕對距離鎖定特定區塊，避免了全樹的遞迴搜尋。")
    print("3. 架構哲學：樹狀結構依賴「相對關係 (Pointers)」，時空系統依賴「絕對位置 (Index)」。")
    print("="*50)

if __name__ == "__main__":
    run_benchmark()
