import argparse
from typing import Dict, List, Tuple

from odoo_jsonrpc import OdooClient


def ensure_db(odoo: OdooClient, db: str | None) -> str:
    if db:
        return db
    dbs = odoo.list_databases() or []
    if isinstance(dbs, dict) and dbs.get("databases"):
        dbs = dbs["databases"]
    if not dbs:
        raise RuntimeError("未能取得資料庫清單")
    if len(dbs) > 1:
        raise RuntimeError(f"偵測到多個資料庫：{dbs}，請用 --db 指定其中之一")
    return dbs[0]


def ensure_attribute(odoo: OdooClient, name: str, display_type: str = "select") -> int:
    existing = odoo.search_read("product.attribute", [["name", "=", name]], ["id"], limit=1)
    if existing:
        return existing[0]["id"]
    return odoo.create("product.attribute", {"name": name, "display_type": display_type})


def ensure_attribute_values(
    odoo: OdooClient, attribute_id: int, values: List[Tuple[str, float]]
) -> List[int]:
    value_ids: List[int] = []
    for name, _extra in values:
        existing = odoo.search_read(
            "product.attribute.value",
            [["name", "=", name], ["attribute_id", "=", attribute_id]],
            ["id"],
            limit=1,
        )
        if existing:
            value_ids.append(existing[0]["id"])
        else:
            vid = odoo.create("product.attribute.value", {"name": name, "attribute_id": attribute_id})
            value_ids.append(vid)
    return value_ids


def ensure_attribute_line(odoo: OdooClient, tmpl_id: int, attribute_id: int, value_ids: List[int]) -> int:
    existing = odoo.search_read(
        "product.template.attribute.line",
        [["product_tmpl_id", "=", tmpl_id], ["attribute_id", "=", attribute_id]],
        ["id"],
        limit=1,
    )
    if existing:
        line_id = existing[0]["id"]
        odoo.write("product.template.attribute.line", [line_id], {"value_ids": [(6, 0, value_ids)]})
    else:
        line_id = odoo.create(
            "product.template.attribute.line",
            {"product_tmpl_id": tmpl_id, "attribute_id": attribute_id, "value_ids": [(6, 0, value_ids)]},
        )
    return line_id


def zero_price_extras_on_line(odoo: OdooClient, line_id: int):
    ptavs = odoo.search_read(
        "product.template.attribute.value",
        [["attribute_line_id", "=", line_id]],
        ["id", "price_extra"],
    )
    for rec in ptavs:
        if rec.get("price_extra"):
            odoo.write("product.template.attribute.value", [rec["id"]], {"price_extra": 0.0})


def ensure_uom_and_pos_flag(odoo: OdooClient, tmpl_id: int):
    tmpl = odoo.search_read("product.template", [["id", "=", tmpl_id]], ["id", "uom_id", "available_in_pos"], limit=1)[0]
    updates = {}
    if not tmpl.get("available_in_pos"):
        updates["available_in_pos"] = True
    if not tmpl.get("uom_id"):
        # pick a reasonable UoM
        candidates = ["Units", "Unit", "個", "件", "pcs"]
        uom = None
        for nm in candidates:
            res = odoo.search_read("uom.uom", [["name", "ilike", nm]], ["id", "name"], limit=1)
            if res:
                uom = res[0]
                break
        if not uom:
            res = odoo.search_read("uom.uom", [["uom_type", "=", "reference"]], ["id", "name"], limit=1)
            if res:
                uom = res[0]
        if uom:
            updates["uom_id"] = uom["id"]
    if updates:
        odoo.write("product.template", [tmpl_id], updates)


def main():
    parser = argparse.ArgumentParser(description="將後端屬性保留但加價全部設為 0")
    parser.add_argument("--url", required=True)
    parser.add_argument("--db")
    parser.add_argument("--login", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--product", default="招牌咖啡")
    args = parser.parse_args()

    odoo = OdooClient(args.url)
    db = ensure_db(odoo, args.db)
    odoo.authenticate(db, args.login, args.password)

    # 目標產品（可能存在重複名稱，全部處理）
    tmpls = odoo.search_read(
        "product.template",
        [["name", "=", args.product]],
        ["id", "name"],
    )
    if not tmpls:
        raise RuntimeError(f"找不到產品模板：{args.product}")

    # 屬性與值（全部零加價）
    sweetness_values = [
        ("正常糖 (100%)", 0.0),
        ("少糖 (70%)", 0.0),
        ("半糖 (50%)", 0.0),
        ("微糖 (30%)", 0.0),
        ("更換蔗糖", 0.0),
    ]
    temperature_values = [
        ("熱飲", 0.0),
        ("溫飲", 0.0),
        ("去冰", 0.0),
        ("微冰", 0.0),
        ("正常冰", 0.0),
        ("冰沙", 0.0),
    ]
    size_values = [
        ("大杯 (600cc)", 0.0),
        ("中杯 (450cc)", 0.0),
        ("小杯 (350cc)", 0.0),
    ]

    # 建立或取得屬性與值
    sweetness_id = ensure_attribute(odoo, "甜度")
    temperature_id = ensure_attribute(odoo, "溫度")
    size_id = ensure_attribute(odoo, "尺寸")
    sweetness_value_ids = ensure_attribute_values(odoo, sweetness_id, sweetness_values)
    temperature_value_ids = ensure_attribute_values(odoo, temperature_id, temperature_values)
    size_value_ids = ensure_attribute_values(odoo, size_id, size_values)

    for tmpl in tmpls:
        tid = tmpl["id"]
        # 確保屬性行存在
        sweet_line = ensure_attribute_line(odoo, tid, sweetness_id, sweetness_value_ids)
        temp_line = ensure_attribute_line(odoo, tid, temperature_id, temperature_value_ids)
        size_line = ensure_attribute_line(odoo, tid, size_id, size_value_ids)
        # 將所有模板屬性值加價設為 0
        zero_price_extras_on_line(odoo, sweet_line)
        zero_price_extras_on_line(odoo, temp_line)
        zero_price_extras_on_line(odoo, size_line)
        # 確保 POS 可用與 UoM
        ensure_uom_and_pos_flag(odoo, tid)
        print(f"[ok] 已零加價並啟用 POS：product_tmpl_id={tid}")


if __name__ == "__main__":
    main()

