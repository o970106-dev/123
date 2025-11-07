import argparse
from typing import Any, Dict, List

from odoo_jsonrpc import OdooClient, OdooRPCError


def list_floors(client: OdooClient) -> List[Dict[str, Any]]:
    try:
        floors = client.search_read(
            "pos.restaurant.floor",
            [],
            ["id", "name"],
            limit=100,
        )
        return floors or []
    except OdooRPCError as e:
        raise RuntimeError(
            f"無法讀取樓層資料，可能未安裝餐飲模組 (pos_restaurant)。錯誤：{e}"
        )


def count_tables(client: OdooClient, floor_id: int) -> int:
    try:
        tables = client.search_read(
            "pos.restaurant.table",
            [["floor_id", "=", floor_id]],
            ["id"],
            limit=1000,
        )
        return len(tables or [])
    except OdooRPCError:
        # 如果沒有桌位模型，視為 0
        return 0


def main():
    parser = argparse.ArgumentParser(description="列出 Odoo 的 POS 餐飲樓層與桌位數")
    parser.add_argument("--url", default="http://127.0.0.1:18069")
    parser.add_argument("--db", default="wuchang_preview_20251107")
    parser.add_argument("--login", default="admin")
    parser.add_argument("--password", default="odoo")
    args = parser.parse_args()

    client = OdooClient(args.url)
    # 嘗試認證，若拒絕嘗試使用第一個資料庫
    try:
        client.authenticate(args.db, args.login, args.password)
    except OdooRPCError:
        try:
            dbs = client.list_databases() or []
            if isinstance(dbs, dict) and dbs.get("databases"):
                dbs = dbs["databases"]
            if not dbs:
                raise RuntimeError("伺服器上沒有找到任何資料庫。")
            fallback_db = dbs[0]
            print(f"[warn] 無法使用指定資料庫 '{args.db}' 認證，改用 '{fallback_db}'。")
            client.authenticate(fallback_db, args.login, args.password)
        except Exception as e:
            raise RuntimeError(f"認證失敗：{e}")

    # 嘗試列出樓層
    try:
        floors = list_floors(client)
    except RuntimeError as e:
        print(str(e))
        print("提示：請在 POS 設定中啟用『餐飲』功能以使用樓層與桌位。")
        return

    if not floors:
        print("沒有找到任何樓層記錄。看起來目前尚未建立設計好的範例樓層。")
        print("可在後台：Point of Sale > Configuration > Restaurant > Floors 新增樓層與桌位。")
        return

    print("找到以下樓層：")
    for f in floors:
        table_count = count_tables(client, f["id"])
        print(f"- Floor: {f['name']} (ID={f['id']}), Tables={table_count}")


if __name__ == "__main__":
    main()
