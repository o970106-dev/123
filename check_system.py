import os
import subprocess
import json
import socket
from pathlib import Path
from datetime import datetime

def check_dependencies():
    print("[1/6] 檢查依賴項 (requirements.txt)...")
    req_file = Path("requirements.txt")
    if not req_file.exists():
        return False, "缺少 requirements.txt"

    with open(req_file, "r") as f:
        content = f.read()

    missing = []
    if "requests" not in content:
        missing.append("requests")

    if missing:
        return False, f"缺少依賴: {', '.join(missing)}"
    return True, "所有必要依賴已列出"

def check_module_sync():
    print("[2/6] 檢查模組同步狀態 (pos_beverage_modifier)...")
    root_mod = Path("pos_beverage_modifier")
    shadow_mod = Path("odoo19-shadow/addons/pos_beverage_modifier")

    if not root_mod.exists() or not shadow_mod.exists():
        return False, "模組目錄不存在"

    result = subprocess.run(["diff", "-r", str(root_mod), str(shadow_mod)], capture_output=True, text=True)
    if result.returncode != 0:
        return False, "根模組與 shadow 模組不同步"
    return True, "模組已同步"

def check_local_odoo():
    print("[3/6] 檢查本地 Odoo 服務 (Port 18069)...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex(('127.0.0.1', 18069))
        if result == 0:
            return True, "本地 Odoo 服務正在運行"
        else:
            return False, "本地 Odoo 服務未啟動"
    finally:
        sock.close()

def check_remote_server():
    print("[4/6] 檢查遠端伺服器連線性 (manage_server.py)...")
    if not Path("manage_server.py").exists():
        return False, "缺少 manage_server.py"

    try:
        # Use a simple command to test connectivity
        result = subprocess.run(["python3", "manage_server.py", "run", "--cmd", "uptime"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True, "遠端伺服器連線正常"
        else:
            return False, f"遠端伺服器連線失敗: {result.stderr.strip() or 'Timeout/Error'}"
    except subprocess.TimeoutExpired:
        return False, "遠端伺服器連線超時 (沙盒限制)"
    except Exception as e:
        return False, f"連線檢查出錯: {str(e)}"

def check_backups():
    print("[5/6] 檢查備份檔案...")
    backup_dir = Path("backups")
    if not backup_dir.exists():
        return False, "缺少 backups 目錄"

    files = list(backup_dir.glob("*"))
    if not files:
        return False, "backups 目錄為空"

    return True, f"找到 {len(files)} 個備份檔案"

def check_hardcoded_logic():
    print("[6/6] 檢查前端硬編碼邏輯...")
    js_path = Path("pos_beverage_modifier/static/src/patch/product_item_patch.js")
    if not js_path.exists():
        return False, "缺少 JS 補丁檔案"

    with open(js_path, "r") as f:
        content = f.read()

    # Check for hardcoded prices or specific product names
    is_hardcoded = "computePriceExtras" in content and "extra +=" in content
    has_hardcoded_names = 'targetNames = ["' in content

    if is_hardcoded or has_hardcoded_names:
        return False, "發現硬編碼邏輯 (產品名稱或加價金額)"
    return True, "未發現明顯的硬編碼邏輯"

def main():
    report = []

    checks = [
        ("Dependencies", check_dependencies),
        ("Module Sync", check_module_sync),
        ("Local Odoo", check_local_odoo),
        ("Remote Server", check_remote_server),
        ("Backups", check_backups),
        ("JS Logic", check_hardcoded_logic)
    ]

    print("=== 系統查核開始 ===\n")
    all_ok = True
    for name, func in checks:
        ok, msg = func()
        status = "✅ PASS" if ok else "❌ FAIL"
        report.append(f"| {name} | {status} | {msg} |")
        # Only set all_ok to False for critical local issues
        if not ok and name in ["Dependencies", "Module Sync"]:
             all_ok = False
        print(f"{status}: {msg}")

    print("\n=== 查核報告生成中 (SYSTEM_AUDIT.md) ===")

    audit_md = "# System Audit Report\n\n"
    audit_md += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    audit_md += "| Component | Status | Details |\n"
    audit_md += "|-----------|--------|---------|\n"
    audit_md += "\n".join(report) + "\n\n"

    audit_md += "## Recommendations\n"
    if not all_ok:
        audit_md += "- [ ] Fix mismatched modules or dependencies.\n"
    audit_md += "- [ ] **Critical**: Refactor `product_item_patch.js` to fetch configuration and prices from the backend `pos.beverage.config` and `pos.beverage.config.line` models.\n"
    audit_md += "- [ ] Restore missing STAPS core modules (`pms_base`, etc.) from the primary repository.\n"

    with open("SYSTEM_AUDIT.md", "w") as f:
        f.write(audit_md)

    print(f"查核完成，總體狀態: {'良好' if all_ok else '有待改進'}")

if __name__ == "__main__":
    main()
