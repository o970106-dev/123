import argparse
import os
import subprocess
import sys
import hashlib

# ==========================================
# 核心技術：時空絕對位置系統 (STAPS) 整合版
# ==========================================

class STAPSOrchestrator:
    """
    利用 STAPS 邏輯進行 O(1) 節點調度
    """
    def __init__(self):
        self.nodes = {}
        # 初始化 8 個關鍵神經節點
        module_list = ["pm", "pf", "vt", "cc", "sc", "er", "ax1", "ax2"]
        for mod in module_list:
            self.register_node(mod)

    def _get_absolute_coordinate(self, identity_code):
        return hashlib.sha256(identity_code.encode()).hexdigest()

    def register_node(self, node_id):
        coord = self._get_absolute_coordinate(node_id)
        target_dir = f"pms_modules/{node_id}/core/odoo19-shadow"
        self.nodes[coord] = {
            "id": node_id,
            "path": target_dir
        }

    def dispatch(self, node_id, action, extra_args=None):
        coord = self._get_absolute_coordinate(node_id)
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

    if args.module:
        # 單點傳輸
        orchestrator.dispatch(args.module, args.action, extra_args)
    else:
        # 1 對 8 全域廣播
        print(f"╔════════════════════════════════════════════════╗")
        print(f"║ [CNS] 啟動 1 對 8 STAPS 全域廣播程序         ║")
        print(f"╚════════════════════════════════════════════════╝")
        module_list = ["pm", "pf", "vt", "cc", "sc", "er", "ax1", "ax2"]
        for mod in module_list:
            orchestrator.dispatch(mod, args.action, extra_args)

if __name__ == "__main__":
    main()
