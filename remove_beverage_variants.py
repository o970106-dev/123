import argparse
from typing import List, Any, Dict

from odoo_jsonrpc import OdooClient, OdooRPCError


def ensure_db(odoo: OdooClient, db_arg: str | None) -> str:
    if db_arg:
        return db_arg
    dbs = odoo.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if not dbs:
        raise RuntimeError("未能取得資料庫清單，請用 --db 指定")
    if len(dbs) > 1:
        raise RuntimeError(f"偵測到多個資料庫：{dbs}，請用 --db 指定其中之一")
    return dbs[0]


def find_template(odoo: OdooClient, name: str) -> Dict[str, Any]:
    tmpls = odoo.search_read(
        "product.template",
        [["name", "=", name]],
        ["id", "name"],
        limit=1,
    )
    if not tmpls:
        raise RuntimeError(f"找不到產品模板：{name}")
    return tmpls[0]


def list_attribute_lines(odoo: OdooClient, tmpl_id: int) -> List[Dict[str, Any]]:
    lines = odoo.search_read(
        "product.template.attribute.line",
        [["product_tmpl_id", "=", tmpl_id]],
        ["id", "attribute_id", "value_ids"],
    )
    return lines


def unlink_attribute_lines(odoo: OdooClient, line_ids: List[int]) -> bool:
    if not line_ids:
        return True
    # Odoo unlink expects a list of ids as first arg
    return bool(odoo.call_kw("product.template.attribute.line", "unlink", [line_ids], {}))


def main():
    parser = argparse.ArgumentParser(description="刪除指定產品的所有變體（屬性行）")
    parser.add_argument("--url", required=True, help="Odoo 服務基址，例如 http://34.80.194.190")
    parser.add_argument("--db", required=False, help="Odoo 資料庫名稱（可省略，將自動偵測唯一資料庫）")
    parser.add_argument("--login", required=True, help="管理員登入帳號，例如 admin@wuchang.life")
    parser.add_argument("--password", required=True, help="管理員登入密碼")
    parser.add_argument("--product", default="招牌咖啡", help="要刪除變體的產品名稱（默認：招牌咖啡）")

    args = parser.parse_args()

    odoo = OdooClient(args.url)
    db = ensure_db(odoo, args.db)
    odoo.authenticate(db, args.login, args.password)

    tmpl = find_template(odoo, args.product)
    print(f"[info] 目標產品模板：id={tmpl['id']} name={tmpl['name']}")

    lines = list_attribute_lines(odoo, tmpl["id"])
    if not lines:
        print("[done] 此產品模板未包含變體屬性行，無需刪除。")
        return

    print(f"[info] 將刪除屬性行數量：{len(lines)}")
    for ln in lines:
        attr = ln.get("attribute_id")
        attr_name = None
        if isinstance(attr, list) and len(attr) == 2:
            attr_name = attr[1]
        print(f" - line_id={ln['id']} attribute={attr_name}")

    line_ids = [ln["id"] for ln in lines]
    try:
        ok = unlink_attribute_lines(odoo, line_ids)
        if not ok:
            raise RuntimeError("unlink 返回 False")
    except OdooRPCError as e:
        raise RuntimeError(f"刪除屬性行失敗：{e}")

    # 驗證刪除結果
    remaining = list_attribute_lines(odoo, tmpl["id"])
    if remaining:
        raise RuntimeError(f"刪除後仍存在屬性行：{[r['id'] for r in remaining]}")
    print("[done] 已刪除所有變體屬性行。產品不再生成變體。")


if __name__ == "__main__":
    main()

