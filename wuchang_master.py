import os
import sys
import subprocess
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║      五常秘密基地：Double J Architecture & STAPS             ║
    ║           Master Controller (God View 模式)                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def run_script(script_name, args=""):
    try:
        cmd = f"{sys.executable} {script_name} {args}"
        subprocess.run(cmd, shell=True)
    except Exception as e:
        print(f"執行出錯: {e}")
    input("\n按任意鍵返回主選單...")

def main_menu():
    while True:
        clear_screen()
        print_banner()
        print("    [1] 系統診斷 (Check System) - 檢查 SSH 與 Odoo API")
        print("    [2] 伺服器維護 (Manage Server) - 更新、升級、指令執行")
        print("    [3] PMS 模組管理 (Manage PMS) - 啟動/停止 8 個地端節點")
        print("    [4] 雲端自動化 (DNS & SSL) - 自動配置 GCP DNS 與 簽發憑證")
        print("    [5] STAPS 廣播實驗 (STAPS Broadcast) - 執行 O(1) 絕對指令傳輸")
        print("    [6] POS 菜單導入 (Import POS Menu) - Excel 資料同步")
        print("    [0] 退出系統")
        print("\n    " + "="*50)

        choice = input("\n    請輸入操作編號: ")

        if choice == '1':
            run_script("check_system.py")
        elif choice == '2':
            action = input("請選擇動作 (check/upgrade/pro-status/run): ")
            if action == 'run':
                cmd = input("請輸入指令: ")
                run_script("manage_server.py", f"run --cmd \"{cmd}\"")
            else:
                run_script("manage_server.py", action)
        elif choice == '3':
            action = input("請選擇動作 (up/down/ps/restart/logs): ")
            extra = ""
            if action == 'up':
                extra = "-d"
            run_script("manage_pms.py", f"{action} {extra}")
        elif choice == '4':
            print("注意：此操作將啟動 Google Cloud DNS API 與 Certbot 流程。")
            confirm = input("確定執行？(y/n): ")
            if confirm.lower() == 'y':
                run_script("deploy_dns_ssl.py")
                run_script("enable_https.py")
        elif choice == '5':
            run_script("double_j_staps.py")
        elif choice == '6':
            source = input("請輸入 Excel 檔案路徑 (例如: data/menu.xlsx): ")
            if os.path.exists(source):
                run_script("import_pos_menu.py", f"--source {source} --apply --update-existing")
            else:
                print("找不到檔案。")
                input("\n按任意鍵返回...")
        elif choice == '0':
            print("\n    [資訊] 五常小J 感謝您的調度，系統休眠中。")
            break
        else:
            print("無效編號。")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()
