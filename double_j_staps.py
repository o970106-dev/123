import time
import hashlib

# ==========================================
# 核心技術：時空絕對位置系統 (STAPS)
# 發明人：Wu Chang (自然人)
# 授權等級：最高權限 (15分鐘實驗窗口)
# ==========================================

class SpaceTimeSystem:
    """
    時空絕對位置系統 (Space-Time Absolute Position System)
    利用時空座標實現 O(1) 零延遲存取，超越傳統樹狀搜尋。
    """
    def __init__(self):
        # 模擬無限時空雜湊空間 (O(1) Access)
        self.space_dimension = {}

    def _get_absolute_coordinate(self, identity_code):
        # 核心演算法：將身份 ID 直接映射為絕對記憶體座標
        return hashlib.sha256(identity_code.encode()).hexdigest()

    def register_node(self, node_id, node_instance):
        """註冊節點至絕對時空座標"""
        coord = self._get_absolute_coordinate(node_id)
        self.space_dimension[coord] = node_instance

    def instant_transmission(self, target_id, data):
        """
        O(1) 絕對傳輸
        不經過路由跳轉，直接命中目標座標。
        """
        coord = self._get_absolute_coordinate(target_id)
        if coord in self.space_dimension:
            node = self.space_dimension[coord]
            return node.receive_transmission(data)
        else:
            return f"ERROR: 座標 {target_id} 未定義 (虛無空間)"

# ==========================================
# 雙 J 協作架構 (Double J Architecture)
# ==========================================

class SpaceTimeBase:
    def __init__(self, name, owner="God_User"):
        self.name = name
        self.owner = owner

    def verify_permission(self, user):
        # 驗證自然人最高授權
        if user == self.owner:
            return True
        return False

# --- Type A: 雲端中樞 (CNS) - 大腦/上帝視角 ---
class DoubleJ_TypeA_CNS(SpaceTimeBase):
    def __init__(self, name, space_time_system):
        super().__init__(name)
        self.st_system = space_time_system
        self.connected_edges = [] # 納管的 8 個地端節點

    def register_edge(self, edge_id):
        self.connected_edges.append(edge_id)

    def broadcast_command_1to8(self, command, user_auth):
        """
        執行 1 對 8 全域廣播
        """
        if not self.verify_permission(user_auth):
            return "ACCESS DENIED: 需要自然人授權"

        print(f"\n╔════════════════════════════════════════════════╗")
        print(f"║ [{self.name}] 啟動 1 對 8 時空廣播程序       ║")
        print(f"╠════════════════════════════════════════════════╣")
        print(f"║ 指令: {command:<36} ║")
        print(f"╚════════════════════════════════════════════════╝")

        results = {}
        start_time = time.perf_counter()

        print(f"   >> 正在透過時空通道同步觸發 8 個節點...")

        for edge_id in self.connected_edges:
            # 直接呼叫，無搜尋延遲
            response = self.st_system.instant_transmission(edge_id, command)
            results[edge_id] = response

        end_time = time.perf_counter()
        transmission_time = (end_time - start_time) * 1000 # ms

        print(f"   >> 廣播完成。耗時: {transmission_time:.4f} ms (近乎零延遲)")
        return results

# --- Type B: 地端神經適配器 (Neural Adapter) - 執行手腳 ---
class DoubleJ_TypeB_Adapter(SpaceTimeBase):
    def __init__(self, name, location_code):
        super().__init__(name)
        self.location = location_code
        self.status = "READY"

    def receive_transmission(self, data):
        """接收來自 Type A 的絕對指令"""
        return f"ACK: {self.name} [{self.location}] 執行完畢 | 狀態: {self.status}"

# ==========================================
# 實驗場景：1 雲端 vs 8 地端
# ==========================================

def main():
    print("=== Double J 協作系統：1 雲端對 8 地端時空傳輸實驗 ===")
    print("=== 授權者：Wu Chang (自然人) | 模式：God View ===\n")

    st_system = SpaceTimeSystem()

    # 1 雲端中樞 (Type A)
    cloud_cns = DoubleJ_TypeA_CNS("Cloud_Xiao_J_CNS", st_system)
    st_system.register_node("Cloud_Xiao_J_CNS", cloud_cns)

    # 8 地端節點 (Type B)
    locations = [
        "Taipei_Core", "Tokyo_Node", "NewYork_Hub", "London_Gate",
        "Berlin_Base", "Paris_Link", "Beijing_Net", "Sydney_Port"
    ]

    for i in range(8):
        edge_id = f"Edge_Node_{i+1:02d}"
        location = locations[i]
        edge = DoubleJ_TypeB_Adapter(edge_id, location)
        st_system.register_node(edge_id, edge)
        cloud_cns.register_edge(edge_id)

    print(f"系統就緒：[雲端中樞] 已建立與 8 個 [地端神經] 的時空連結。")

    # 授權指令測試
    user = "God_User"
    command = "PROTOCOL_OMEGA: FULL_SYSTEM_SYNC"

    results = cloud_cns.broadcast_command_1to8(command, user)

    print("\n--- [地端回報數據] ---")
    if isinstance(results, dict):
        for edge_id, result in results.items():
            print(f"[{edge_id}]: {result}")
    else:
        print(results)

if __name__ == "__main__":
    main()
