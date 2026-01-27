import argparse
import os
import subprocess
import sys

MODULES = ["pm", "pf", "vt", "cc", "sc", "er"]

def run_docker_compose(module, action, extra_args=None):
    target_dir = f"pms_modules/{module}/core/odoo19-shadow"
    if not os.path.exists(target_dir):
        print(f"[跳過] 模組 {module} 目錄不存在: {target_dir}")
        return

    cmd = ["docker-compose", "-f", "docker-compose.yml", action]
    if extra_args:
        cmd.extend(extra_args)

    print(f"--- 執行模組 {module} 的 {action} 操作 ---")
    try:
        subprocess.run(cmd, cwd=target_dir, check=True)
    except Exception as e:
        print(f"[錯誤] 模組 {module} 執行失敗: {e}")

def main():
    parser = argparse.ArgumentParser(description="PMS 模組管理工具")
    parser.add_argument("action", choices=["up", "down", "restart", "logs", "ps"], help="Docker Compose 操作")
    parser.add_argument("--module", help="指定單一模組 (預設為全部)")
    parser.add_argument("-d", "--detach", action="store_true", help="後台執行 (用於 up)")
    args = parser.parse_args()

    modules_to_process = [args.module] if args.module else MODULES

    extra_args = []
    if args.action == "up" and args.detach:
        extra_args.append("-d")

    for mod in modules_to_process:
        run_docker_compose(mod, args.action, extra_args)

if __name__ == "__main__":
    main()
