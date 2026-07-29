import argparse
import os
import subprocess
import sys
from staps_core import STAPS_NODES, get_absolute_coordinate, get_node_path, timed_process

class STAPSOrchestrator:
    """
    利用 STAPS 邏輯進行 O(1) 節點調度
    """
    def __init__(self):
        self.nodes = {}
        for mod in STAPS_NODES:
            self.register_node(mod)

    def register_node(self, node_id):
        coord = get_absolute_coordinate(node_id)
        target_dir = get_node_path(node_id)
        self.nodes[coord] = {
            "id": node_id,
            "path": target_dir
        }

    def dispatch(self, node_id, action, extra_args=None):
        coord = get_absolute_coordinate(node_id)
        node = self.nodes.get(coord)

        if not node:
            print(f"[警告] 座標 {node_id} 未定義 (虛無空間)")
            return

        target_dir = node["path"]
        if not os.path.exists(target_dir):
            print(f"[跳過] 節點 {node_id} 目錄不存在: {target_dir}")
            return

        cmd = ["docker-compose", "-f", "docker-compose.yml", action]
        if extra_args:
            cmd.extend(extra_args)

        print(f"--- [STAPS傳輸] 命中座標: {node_id} | 執行: {action} ---")
        try:
            subprocess.run(cmd, cwd=target_dir, check=True)
        except Exception as e:
            print(f"[錯誤] 節點 {node_id} 調度失敗: {e}")

def main():
    orchestrator = STAPSOrchestrator()

    parser = argparse.ArgumentParser(description="Double J 神經節點調度工具 (STAPS)")
    parser.add_argument("action", choices=["up", "down", "restart", "logs", "ps"], help="Docker Compose 操作")
    parser.add_argument("--module", help="指定單一節點 (預設為全域廣播)")
    parser.add_argument("-d", "--detach", action="store_true", help="後台執行 (用於 up)")
    args = parser.parse_args()

    extra_args = []
    if args.action == "up" and args.detach:
        extra_args.append("-d")

    with timed_process(f"神經調度程序 ({args.action})"):
        if args.module:
            orchestrator.dispatch(args.module, args.action, extra_args)
        else:
            print(f"╔════════════════════════════════════════════════╗")
            print(f"║ [CNS] 啟動 1 對 8 STAPS 全域廣播程序         ║")
            print(f"╚════════════════════════════════════════════════╝")
            for mod in STAPS_NODES:
                orchestrator.dispatch(mod, args.action, extra_args)

if __name__ == "__main__":
    main()
