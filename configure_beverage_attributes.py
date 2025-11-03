import argparse
from typing import Dict, List, Tuple

from odoo_jsonrpc import OdooClient


def ensure_attribute(odoo: OdooClient, name: str, display_type: str = "select") -> int:
    existing = odoo.search_read("product.attribute", [["name", "=", name]], ["id"], limit=1)
    if existing:
        return existing[0]["id"]
    return odoo.create("product.attribute", {"name": name, "display_type": display_type})


def ensure_attribute_values(odoo: OdooClient, attribute_id: int, values: List[Tuple[str, float]]) -> List[int]:
    """僅確保屬性值存在，不在此層設定加價。"""
    value_ids: List[int] = []
    for name, _price_extra in values:
        existing = odoo.search_read(
            "product.attribute.value",
            [["name", "=", name], ["attribute_id", "=", attribute_id]],
            ["id"],
            limit=1,
        )
        if existing:
            vid = existing[0]["id"]
            value_ids.append(vid)
        else:
            vid = odoo.create(
                "product.attribute.value",
                {"name": name, "attribute_id": attribute_id},
            )
            value_ids.append(vid)
    return value_ids


def ensure_product_template(odoo: OdooClient, name: str) -> int:
    existing = odoo.search_read("product.template", [["name", "=", name]], ["id"], limit=1)
    if existing:
        return existing[0]["id"]
    # 若不存在則建立基本產品，基礎價由使用者後續調整
    return odoo.create("product.template", {"name": name, "list_price": 0.0, "type": "consu"})


def ensure_attribute_line(odoo: OdooClient, tmpl_id: int, attribute_id: int, value_ids: List[int]) -> int:
    # product.template.attribute.line: 關聯產品模板與屬性，並指定可選值
    existing = odoo.search_read(
        "product.template.attribute.line",
        [["product_tmpl_id", "=", tmpl_id], ["attribute_id", "=", attribute_id]],
        ["id"],
        limit=1,
    )
    if existing:
        line_id = existing[0]["id"]
        # 設定 value_ids 為提供的集合（覆蓋）
        odoo.write("product.template.attribute.line", [line_id], {"value_ids": [(6, 0, value_ids)]})
    else:
        line_id = odoo.create(
        "product.template.attribute.line",
        {"product_tmpl_id": tmpl_id, "attribute_id": attribute_id, "value_ids": [(6, 0, value_ids)]},
        )

    return line_id

def set_price_extras_on_line(odoo: OdooClient, line_id: int, values: List[Tuple[str, float]]):
    """在 product.template.attribute.value 層設定各值加價。"""
    # 取出此屬性行所有模板值，建立 mapping
    existing_ptav = odoo.search_read(
        "product.template.attribute.value",
        [["attribute_line_id", "=", line_id]],
        ["id", "name", "product_attribute_value_id"],
    )
    # 建立 product.attribute.value.id -> product.template.attribute.value.id 對應
    pav_to_ptav = {}
    for rec in existing_ptav:
        pav = rec.get("product_attribute_value_id")
        if isinstance(pav, list) and pav:
            pav_to_ptav[pav[0]] = rec["id"]

    # 取得屬性行允許的值清單（domain 可省略，依現有 ptav 查找）
    for name, extra in values:
        # 找到對應的 product.attribute.value
        pav_rec = odoo.search_read(
            "product.attribute.value",
            [["name", "=", name]],
            ["id"],
            limit=1,
        )
        if not pav_rec:
            continue
        pav_id = pav_rec[0]["id"]
        ptav_id = pav_to_ptav.get(pav_id)
        if ptav_id:
            odoo.write("product.template.attribute.value", [ptav_id], {"price_extra": extra})
        else:
            # 若不存在，建立新的模板值並設定加價
            odoo.create(
                "product.template.attribute.value",
                {
                    "attribute_line_id": line_id,
                    "product_attribute_value_id": pav_id,
                    "price_extra": extra,
                },
            )


def main():
    parser = argparse.ArgumentParser(description="配置飲料訂購系統屬性並套用到指定產品")
    parser.add_argument("--url", required=True, help="Odoo 服務基址，例如 http://34.80.194.190")
    parser.add_argument("--db", required=False, help="Odoo 資料庫名稱（可省略，將自動偵測唯一資料庫）")
    parser.add_argument("--login", required=True, help="管理員登入帳號，例如 admin@wuchang.life")
    parser.add_argument("--password", required=True, help="管理員登入密碼")
    parser.add_argument("--product", default="招牌咖啡", help="要套用的產品名稱（默認：招牌咖啡）")

    args = parser.parse_args()

    odoo = OdooClient(args.url)
    db = args.db
    if not db:
        dbs = odoo.list_databases() or []
        if not dbs:
            raise RuntimeError("未能取得資料庫清單，請手動提供 --db")
        if isinstance(dbs, dict) and dbs.get('databases'):
            # 某版本返回字典
            dbs = dbs['databases']
        if len(dbs) > 1:
            raise RuntimeError(f"偵測到多個資料庫：{dbs}，請用 --db 指定其中之一")
        db = dbs[0]
    odoo.authenticate(db, args.login, args.password)

    # 定義屬性與值（含價格調整）
    sweetness_values = [
        ("正常糖 (100%)", 0.0),
        ("少糖 (70%)", 0.0),
        ("半糖 (50%)", 0.0),
        ("微糖 (30%)", 0.0),
        ("更換蔗糖", 5.0),
    ]
    temperature_values = [
        ("熱飲", 0.0),
        ("溫飲", 0.0),
        ("去冰", 0.0),
        ("微冰", 0.0),
        ("正常冰", 0.0),
        ("冰沙", 10.0),
    ]
    size_values = [
        ("大杯 (600cc)", 30.0),
        ("中杯 (450cc)", 0.0),
        ("小杯 (350cc)", -15.0),
    ]

    # 建立/取得屬性
    sweetness_id = ensure_attribute(odoo, "甜度", display_type="select")
    temperature_id = ensure_attribute(odoo, "溫度", display_type="select")
    size_id = ensure_attribute(odoo, "尺寸", display_type="select")

    # 建立/更新屬性值（含價格）
    sweetness_value_ids = ensure_attribute_values(odoo, sweetness_id, sweetness_values)
    temperature_value_ids = ensure_attribute_values(odoo, temperature_id, temperature_values)
    size_value_ids = ensure_attribute_values(odoo, size_id, size_values)

    # 建立/取得產品模板
    tmpl_id = ensure_product_template(odoo, args.product)

    # 套用屬性到產品模板
    sweetness_line_id = ensure_attribute_line(odoo, tmpl_id, sweetness_id, sweetness_value_ids)
    temperature_line_id = ensure_attribute_line(odoo, tmpl_id, temperature_id, temperature_value_ids)
    size_line_id = ensure_attribute_line(odoo, tmpl_id, size_id, size_value_ids)

    # 在模板層設定加價
    set_price_extras_on_line(odoo, sweetness_line_id, sweetness_values)
    set_price_extras_on_line(odoo, temperature_line_id, temperature_values)
    set_price_extras_on_line(odoo, size_line_id, size_values)

    print(f"[完成] 已將屬性（甜度/溫度/尺寸）套用到產品：{args.product}")
    print("- 可在 銷售 → 產品 → 產品，開啟產品確認變體屬性行")
    print("- 銷售訂單新增該產品時會彈出配置器並按加價計算最終價格")


if __name__ == "__main__":
    main()
