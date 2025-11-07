from typing import List, Dict

from odoo_jsonrpc import OdooClient


ATTRS: Dict[str, List[str]] = {
    "甜度": ["無糖", "微糖", "半糖", "全糖"],
    "冰量": ["去冰", "微冰", "正常冰"],
    "加料": ["不加", "珍珠", "椰果"],
}

# 可選價差，只有有價差的項目填入 (屬於 PTAV 上的 price_extra)
PRICE_EXTRA: Dict[str, Dict[str, float]] = {
    "加料": {"珍珠": 10.0, "椰果": 10.0},
}


def ensure_attribute(client: OdooClient, name: str) -> int:
    rec = client.search_read(
        "product.attribute", [["name", "=", name]], ["id", "name"], limit=1
    )
    if rec:
        return rec[0]["id"]
    # 為了在 POS 顯示屬性選擇，使用 create_variant = 'always'
    return client.create(
        "product.attribute",
        {"name": name, "create_variant": "always", "display_type": "radio"},
    )


def ensure_attribute_values(client: OdooClient, attr_id: int, values: List[str]) -> List[int]:
    ids: List[int] = []
    for v in values:
        found = client.search_read(
            "product.attribute.value",
            [["name", "=", v], ["attribute_id", "=", attr_id]],
            ["id"],
            limit=1,
        )
        if found:
            ids.append(found[0]["id"])
        else:
            ids.append(client.create("product.attribute.value", {"name": v, "attribute_id": attr_id}))
    return ids


def ensure_attribute_line(client: OdooClient, tmpl_id: int, attr_id: int, value_ids: List[int]) -> int:
    # 查找是否已有屬性行
    existing = client.search_read(
        "product.template.attribute.line",
        [["product_tmpl_id", "=", tmpl_id], ["attribute_id", "=", attr_id]],
        ["id"],
        limit=1,
    )
    if existing:
        line_id = existing[0]["id"]
        # 覆蓋 value_ids（6 替換）
        client.write("product.template.attribute.line", [line_id], {"value_ids": [(6, 0, value_ids)]})
        return line_id
    return client.create(
        "product.template.attribute.line",
        {
            "product_tmpl_id": tmpl_id,
            "attribute_id": attr_id,
            "value_ids": [(6, 0, value_ids)],
        },
    )


def set_ptav_price_extras(client: OdooClient, line_id: int, attr_name: str):
    mapping = PRICE_EXTRA.get(attr_name) or {}
    if not mapping:
        return
    ptavs = client.search_read(
        "product.template.attribute.value",
        [["attribute_line_id", "=", line_id]],
        ["id", "name", "price_extra"],
    )
    for v in ptavs:
        name = v.get("name")
        extra = mapping.get(name)
        if extra is None:
            continue
        client.write("product.template.attribute.value", [v["id"]], {"price_extra": extra})


def ensure_variants_available_in_pos(client: OdooClient, tmpl_id: int):
    # 生成變體（保險起見觸發一次）
    try:
        client.call_kw("product.template", "create_variant_ids", [[tmpl_id]], {})
    except Exception:
        pass
    variants = client.search_read(
        "product.product",
        [["product_tmpl_id", "=", tmpl_id]],
        ["id", "available_in_pos"],
        limit=200,
    )
    ids = [v["id"] for v in variants]
    if ids:
        client.write("product.product", ids, {"available_in_pos": True})


def main():
    client = OdooClient("http://127.0.0.1:18069")
    client.authenticate("wuchang_preview_20251107", "admin", "odoo")
    tmpl = client.search_read(
        "product.template",
        [["name", "=", "招牌咖啡"]],
        ["id", "name"],
        limit=1,
    )
    if not tmpl:
        raise RuntimeError("找不到產品模板：招牌咖啡")
    tmpl_id = tmpl[0]["id"]

    for attr_name, values in ATTRS.items():
        attr_id = ensure_attribute(client, attr_name)
        value_ids = ensure_attribute_values(client, attr_id, values)
        line_id = ensure_attribute_line(client, tmpl_id, attr_id, value_ids)
        set_ptav_price_extras(client, line_id, attr_name)

    ensure_variants_available_in_pos(client, tmpl_id)
    print("[done] 屬性與變體已建立，並開啟 POS 可售")


if __name__ == "__main__":
    main()

