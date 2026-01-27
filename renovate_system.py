import os
import sys
import subprocess
import time
from staps_core import timed_process, staps_timed

@staps_timed
def run_renovation():
    print("""
    ============================================================
    🚀 啟動「五常秘密基地」全自動系統改造程序 (Full Renovation)
    ============================================================
    """)

    scripts = [
        ("初始化 8 節點 STAPS 座標", "generate_pms_composes.py", ""),
        ("雲端 DNS 與 SSL 通道配置", "deploy_dns_ssl.py", ""),
        ("Nginx HTTPS 加密適配", "enable_https.py", ""),
        ("全域神經節點啟動 (1 對 8 廣播)", "manage_pms.py", "up -d")
    ]

    for desc, script, args in scripts:
        print(f"\n>> 正在執行: {desc}")
        try:
            cmd = f"{sys.executable} {script} {args}"
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError:
            print(f"!! 錯誤: {desc} 執行中斷。")
            return False

    return True

def main():
    start_time = time.time()
    success = run_renovation()
    end_time = time.time()

    total_elapsed = end_time - start_time

    print("\n" + "="*60)
    if success:
        print("✅ 系統改造全線完成！這座基地現在已具備世界第一的調度能力。")
    else:
        print("❌ 系統改造未完全達成，請檢查上述錯誤日誌。")

    print(f"⏱️ 改造總耗時: {total_elapsed:.2f} 秒")
    print("="*60)

if __name__ == "__main__":
    main()
