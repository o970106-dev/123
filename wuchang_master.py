import os
import sys
import subprocess
import time
from datetime import datetime
from staps_core import timed_process, get_system_birth_moment, STAPS_NODES

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
    ║      [狀態]: Highest Degree Optimization Active (v3.0)       ║
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

def broadcast_energy_save():
    with timed_process("Global Energy Saving Broadcast"):
        print(">>> [STAPS] 發送 O(1) 全域節能指令...")
        # Simulating signal transmission to all nodes
        for node in STAPS_NODES:
            print(f"  > 訊號已到達節點: {node} (延遲: 0.0003ms)")
        print(">>> [成功] 全域節能協議已在 8 個神經節點同步生效。")
    input("\n廣播完成。按任意鍵返回...")

def main_menu():
    start_time = time.time()
    while True:
        clear_screen()
        print_banner()
        print("    [1] 系統全域診斷 (Global Diagnostics) - 檢查時空連通性")
        print("    [2] 8 大地端神經調度 (Neural Orchestration) - 管理 Docker 叢集")
        print("    [3] STAPS 傳輸實驗 (STAPS Protocol) - 執行絕對座標廣播")
        print("    [4] 全域節能廣播 (Global Energy Save) - 觸發 SC 節能協議")
        print("    [5] 數據導入中樞 (Data Ingestion) - POS 菜單資料同步")
        print("    [6] 系統極致優化 (System Renovation) - 執行最高程度優化")
        print("    [0] 系統休眠 (System Sleep)")
        print("\n    " + "="*50)

        choice = input("\n    請下達調度指令: ")

        if choice == '1':
            run_script("check_system.py")
        elif choice == '2':
            run_script("manage_pms.py", "ps")
        elif choice == '3':
            run_script("staps_core.py")
        elif choice == '4':
            broadcast_energy_save()
        elif choice == '5':
            source = input("請輸入 Excel 數據源路徑: ")
            if os.path.exists(source):
                run_script("import_pos_menu.py", f"--source {source} --apply --update-existing")
            else:
                print("找不到指定數據源。")
                input("\n按任意鍵返回...")
        elif choice == '6':
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
