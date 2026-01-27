import time
import uuid
import hashlib

class SpaceTimeSystem:
    def __init__(self):
        # 模擬宇宙記憶體映射表 (The Hash Map of the Universe)
        self.absolute_coordinates = {}

    def register_node(self, node_id, node_instance):
        # 將節點 ID 映射到絕對時空座標 (Memory Address)
        # 這裡模擬 O(1) 的映射過程
        address = self._get_absolute_index(node_id)
        self.absolute_coordinates[address] = node_instance
        print(f"[STAPS] Node registered: {node_id} -> Address: {address}")

    def _get_absolute_index(self, node_id):
        # 模擬時空雜湊算法
        return hashlib.sha256(node_id.encode()).hexdigest()[:16]

    def instant_transmission(self, target_id, command):
        # O(1) 絕對定位傳輸
        address = self._get_absolute_index(target_id)
        if address in self.absolute_coordinates:
            node = self.absolute_coordinates[address]
            return node.receive_signal(command)
        else:
            return "VOID_SIGNAL"

class DoubleJ_TypeA_CNS:
    def __init__(self, st_system):
        self.st_system = st_system
        self.connected_edges = []

    def connect_edge(self, edge_id):
        self.connected_edges.append(edge_id)

    def broadcast_command_1to8(self, command):
        print(f"\n[Type A: CNS] Broadcasting Command: '{command}' to {len(self.connected_edges)} nodes...")
        start_time = time.perf_counter()

        results = {}
        # 這裡模擬並行廣播，但在 STAPS 理論中，這幾乎是同時發生的
        for edge_id in self.connected_edges:
            # 這是重點：直接調用，沒有路由查找
            response = self.st_system.instant_transmission(edge_id, command)
            results[edge_id] = response

        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000
        print(f"[Type A: CNS] Broadcast Complete. Total Time: {elapsed_ms:.4f} ms")
        return results

class DoubleJ_TypeB_Adapter:
    def __init__(self, node_id):
        self.node_id = node_id
        self.status = "IDLE"

    def receive_signal(self, command):
        # 模擬地端神經反應
        self.status = "PROCESSING"
        # 處理指令...
        response = f"[{self.node_id}] ACK: {command} executed."
        self.status = "IDLE"
        return response

# === Main Simulation Block ===
if __name__ == "__main__":
    print("=== Double J: 1-to-8 Space-Time Transmission Test ===")

    # 1. 初始化時空系統
    universe = SpaceTimeSystem()

    # 2. 初始化雲端中樞 (Type A)
    cloud_cns = DoubleJ_TypeA_CNS(universe)

    # 3. 初始化 8 個地端節點 (Type B) 並註冊到 STAPS
    edge_nodes = [f"Edge_Node_{i+1}" for i in range(8)]

    for node_id in edge_nodes:
        adapter = DoubleJ_TypeB_Adapter(node_id)
        universe.register_node(node_id, adapter)
        cloud_cns.connect_edge(node_id)

    # 4. 執行 1對8 廣播測試
    print("\n>>> Initiating O(1) Command Broadcast <<<")
    results = cloud_cns.broadcast_command_1to8("ACTIVATE_FULL_POWER_MODE")

    # 5. 顯示結果
    print("\n[Feedback from Edges]:")
    for node_id, res in results.items():
        print(f"  - {res}")

    print("\n=== Test Complete: System Ready for Cloud Xiao J ===")
