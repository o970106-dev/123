import os
import sys
import subprocess
import time
from datetime import datetime
from staps_core import timed_process, get_system_birth_moment

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    birth = get_system_birth_moment()
    now = datetime.now()
    uptime = (now - birth).total_seconds()

    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║      五常秘密基地：Double J Architecture & STAPS             ║
    ║           Master Controller (CNS God View)                   ║
    ║                                                              ║
    ║      [下令時刻]: {birth.strftime('%H:%M:%S')} UTC       [運作秒數]: {uptime:.1f}s   ║
    ║      [傳輸協議]: STAPS O(1)      [地端節點]: 8 Neural Nodes   ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def run_script(script_name, args=""):
    try:
        cmd = f"{sys.executable} {script_name} {args}"
        subprocess.run(cmd, shell=True)
    except Exception as e:
        print(f"執行出錯: {e}")
    input("\n按任意鍵返回 CNS 主選單...")

def main_menu():
    start_time = time.time()
    while True:
        clear_screen()
        print_banner()
        print("    [1] 系統全域診斷 (Global Diagnostics) - 檢查時空連通性")
        print("    [2] 伺服器核心維護 (Core Maintenance) - 執行指令與升級")
        print("    [3] 8 大地端神經調度 (Neural Orchestration) - 管理 Docker 叢集")
        print("    [4] 雲端自動化部署 (Cloud Automation) - DNS & SSL 一鍵同步")
        print("    [5] STAPS 傳輸實驗 (STAPS Protocol) - 執行絕對座標廣播")
        print("    [6] 數據導入中樞 (Data Ingestion) - POS 菜單資料同步")
        print("    [7] 基地全自動改造 (Full System Renovation) - 一鍵完成全線升級")
        print("    [0] 系統休眠 (System Sleep)")
        print("\n    " + "="*50)

        choice = input("\n    請下達調度指令: ")

        if choice == '1':
            run_script("check_system.py")
        elif choice == '2':
            action = input("請選擇動作 (check/upgrade/pro-status/run): ")
            if action == 'run':
                cmd = input("請輸入遠端指令: ")
                run_script("manage_server.py", f"run --cmd \"{cmd}\"")
            else:
                run_script("manage_server.py", action)
        elif choice == '3':
            action = input("請選擇調度動作 (up/down/ps/restart/logs): ")
            extra = ""
            if action == 'up':
                extra = "-d"
            node = input("指定特定節點 (留空則為 1 對 8 全域調度): ")
            args = f"{action} {extra}"
            if node:
                args += f" --module {node}"
            run_script("manage_pms.py", args)
        elif choice == '4':
            print("警告：此操作將影響全域 DNS 解析與 SSL 憑證狀態。")
            confirm = input("確定執行全自動化部署程序？(y/n): ")
            if confirm.lower() == 'y':
                run_script("deploy_dns_ssl.py")
                run_script("enable_https.py")
        elif choice == '5':
            run_script("double_j_staps.py")
        elif choice == '6':
            source = input("請輸入 Excel 數據源路徑: ")
            if os.path.exists(source):
                run_script("import_pos_menu.py", f"--source {source} --apply --update-existing")
            else:
                print("找不到指定數據源。")
                input("\n按任意鍵返回...")
        elif choice == '7':
            run_script("renovate_system.py")
        elif choice == '0':
            end_time = time.time()
            total_session = end_time - start_time
            print(f"\n    [資訊] 五常小J 感謝您的指揮。本次調度總時長: {total_session:.2f} 秒。")
            print("    系統休眠中。")
            break
        else:
            print("無效指令代碼。")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()
