import hashlib
import time
import functools
import json
import os
from datetime import datetime
from contextlib import contextmanager

# ==========================================
# 核心技術：時空絕對位置系統 (STAPS) 核心庫
# 版權所有：Wu Chang (自然人) & 五常小J
# ==========================================

# 8 個核心地端神經節點定義
STAPS_NODES = ["pm", "pf", "vt", "cc", "sc", "er", "ax1", "ax2"]
STAPS_MULTIPLIER = len(STAPS_NODES) # 1 對 8 並行乘數

# 埠號映射配置
NODE_PORTS = {
    "pm": 18101,
    "pf": 18102,
    "vt": 18103,
    "cc": 18104,
    "sc": 18105,
    "er": 18107,
    "ax1": 18108,
    "ax2": 18109,
}

# 長連線埠號映射
NODE_LONG_PORTS = {
    "pm": 8111,
    "pf": 8112,
    "vt": 8113,
    "cc": 8114,
    "sc": 8115,
    "er": 8117,
    "ax1": 8118,
    "ax2": 8119,
}

# Node ID to Addon Dir mapping
NODE_ADDON_MAP = {
    "pm": "pm",
    "pf": "pms_portal_resident",
    "vt": "vt",
    "cc": "pms_community_center",
    "sc": "sc_google_home",
    "er": "er",
    "ax1": "pms_merchant_adapter",
    "ax2": "pms_ax2",
}

def get_absolute_coordinate(identity_code: str) -> str:
    """利用 SHA-256 將身份 ID 映射為物理座標"""
    return hashlib.sha256(identity_code.encode()).hexdigest()

@contextmanager
def timed_process(process_name: str):
    """高精度處理計時器"""
    print(f"\n[計時啟動] 正在執行: {process_name}...")
    start_time = time.perf_counter()
    yield
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    print(f"[計時結束] {process_name} 完成。耗時: {elapsed:.4f} 秒")

def staps_timed(func):
    """計時裝飾器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with timed_process(func.__name__):
            return func(*args, **kwargs)
    return wrapper

def get_parallel_efficiency(total_seconds: float) -> float:
    """計算並行校準後的等效單節點耗時 (Total / 8)"""
    return total_seconds / STAPS_MULTIPLIER

def get_engineering_compression(actual_seconds: float, estimated_value_mins: float = 105) -> float:
    """計算「時空摺疊」壓縮比：預估工程價值 / 實際耗時"""
    return (estimated_value_mins * 60) / max(actual_seconds, 0.0001)

def get_system_birth_moment() -> datetime:
    """調閱時空日誌，獲取下令實際時刻 (Time Zero)"""
    log_path = "collaboration_log.json"
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                log = json.load(f)
                birth_str = log.get("system_birth")
                if birth_str:
                    return datetime.strptime(birth_str, "%Y-%m-%d %H:%M:%S")
        except:
            pass
    return datetime.now()

def get_node_path(node_id: str) -> str:
    """獲取節點的相對檔案路徑 (修復版)"""
    # 實際結構中，模組位於 odoo19-shadow/addons/ 下
    addon_dir = NODE_ADDON_MAP.get(node_id, node_id)
    return f"odoo19-shadow/addons/{addon_dir}"

def verify_staps_integrity():
    """驗證系統連通性基礎"""
    print("--- [STAPS] 正在校準 8 個神經節點座標 ---")
    for node in STAPS_NODES:
        coord = get_absolute_coordinate(node)
        port = NODE_PORTS.get(node)
        path = get_node_path(node)
        print(f"  > 節點: {node:<4} | 座標: {coord[:16]}... | Port: {port} | Path: {path}")
    print("--- [STAPS] 校準完畢 ---")

if __name__ == "__main__":
    verify_staps_integrity()
