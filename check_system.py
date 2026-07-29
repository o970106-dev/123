import json
import sys
import requests
from typing import Any, Dict, List, Optional
from manage_server import load_config, connect as connect_ssh, run_command

class OdooRPCError(Exception):
    pass

class OdooClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.uid: Optional[int] = None

    def list_databases(self) -> Any:
        url = f"{self.base_url}/web/database/list"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {},
        }
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if 'error' in data:
            raise OdooRPCError(str(data['error']))
        return data.get('result')

    def authenticate(self, db: str, login: str, password: str) -> int:
        url = f"{self.base_url}/web/session/authenticate"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": db,
                "login": login,
                "password": password,
            },
        }
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if 'error' in data:
            raise OdooRPCError(str(data['error']))
        result = data.get('result') or {}
        uid = result.get('uid')
        if not uid:
            raise OdooRPCError("Authentication failed: no uid returned")
        self.uid = uid
        return uid

    def call_kw(self, model: str, method: str, args: List[Any], kwargs: Dict[str, Any]) -> Any:
        url = f"{self.base_url}/web/dataset/call_kw/{model}/{method}"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": model,
                "method": method,
                "args": args,
                "kwargs": kwargs,
            },
        }
        resp = self.session.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if 'error' in data:
            raise OdooRPCError(str(data['error']))
        return data.get('result')

    def search_read(self, model: str, domain: List[Any], fields: List[str], limit: int = 0) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {"domain": domain, "fields": fields}
        if limit:
            kwargs["limit"] = limit
        return self.call_kw(model, "search_read", [], kwargs)

    def create(self, model: str, vals: Dict[str, Any]) -> int:
        return self.call_kw(model, "create", [vals], {})

    def write(self, model: str, ids: List[int], vals: Dict[str, Any]) -> bool:
        return self.call_kw(model, "write", [ids, vals], {})

def check_ssh_connection(ssh_cfg):
    """檢查 SSH 連線並執行一條簡單的遠端指令"""
    print("--- 正在檢查 SSH 連線 ---")
    try:
        password = ssh_cfg.get("password")
        client = connect_ssh(ssh_cfg)
        print(f"✅ 成功連線到伺服器: {ssh_cfg.get('host')}")

        print("\n[測試] 執行 'uname -a'...")
        out, err, rc = run_command(client, "uname -a", sudo=False, password=password)
        if rc == 0:
            print(f"✅ 遠端指令執行成功:\n{out.strip()}")
        else:
            print(f"❌ 遠端指令執行失敗:\n{err.strip()}")
        client.close()
    except Exception as e:
        print(f"❌ SSH 連線失敗: {e}")
        print("[提示] 請檢查 'config.json' 中的 'ssh' 設定是否正確。")

def check_odoo_connection(odoo_cfg):
    """檢查 Odoo 連線並獲取基本資訊"""
    print("\n--- 正在檢查 Odoo 連線 ---")
    url = odoo_cfg.get("url")
    db = odoo_cfg.get("db")
    login = odoo_cfg.get("login")
    pw = odoo_cfg.get("pw")

    if not all([url, db, login, pw]):
        print("❌ Odoo 設定不完整，請檢查 config.json")
        return

    try:
        print(f"正在連線到 Odoo: {url}")
        client = OdooClient(url)

        print("列出資料庫...")
        dbs = client.list_databases()
        if not dbs:
            print("❌ 未能從 Odoo 獲取資料庫列表")
            return
        print(f"✅ 成功獲取資料庫列表: {dbs}")

        if db not in dbs:
            print(f"⚠️  指定的資料庫 '{db}' 不在列表中，請確認")

        print(f"使用資料庫 '{db}' 進行身分驗證...")
        client.authenticate(db, login, pw)
        print(f"✅ 成功以使用者 '{login}' 登入")

        print("\n[測試] 讀取 POS 設定...")
        pos_configs = client.search_read("pos.config", [], ["id", "name"], limit=5)
        print(f"✅ 成功讀取 POS 設定，找到 {len(pos_configs)} 個項目。")

    except Exception as e:
        print(f"❌ Odoo 連線或操作失敗: {e}")
        print("[提示] 請檢查 'config.json' 中的 'odoo' 設定是否正確，以及 Odoo 服務是否正在執行。")

def main():
    try:
        cfg = load_config("config.json")
        ssh_cfg = cfg.get("ssh")
        odoo_cfg = cfg.get("odoo")

        if not ssh_cfg:
            print("[警告] 配置文件中缺少 'ssh' 部分，跳過 SSH 檢查。")
        else:
            check_ssh_connection(ssh_cfg)

        if not odoo_cfg:
            print("[警告] 配置文件中缺少 'odoo' 部分，跳過 Odoo 檢查。")
        else:
            check_odoo_connection(odoo_cfg)

    except FileNotFoundError:
        print("[錯誤] 找不到 config.json 或 config.example.json。請先設定您的連線資訊。")
        sys.exit(1)
    except Exception as e:
        print(f"[嚴重錯誤] 發生未預期的問題: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
