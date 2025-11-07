/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ProductItem } from "@point_of_sale/app/screens/product_screen/product_item/product_item";
import { ModifierDialog } from "pos_beverage_modifier/static/src/components/modifier_dialog";

function computePriceExtras(sel) {
    let extra = 0;
    if (sel?.sweetness === "更換蔗糖") extra += 5;
    if (sel?.temperature === "冰沙") extra += 10;
    if (sel?.size === "大杯 (600cc)") extra += 30;
    if (sel?.size === "小杯 (350cc)") extra -= 15;
    return extra;
}

patch(ProductItem.prototype, "pos_beverage_modifier/ProductItem", {
    async onClick() {
        const product = this.props.product;
        // 僅針對飲品或特定產品名稱，可改為類目判斷
        const targetNames = ["招牌咖啡"]; // 可擴充
        if (targetNames.includes(product.display_name)) {
            this.env.services.dialog.add(ModifierDialog, {
                product,
                onConfirm: (selection) => this._applySelection(product, selection),
            });
            return;
        }
        return this._super(...arguments);
    },
    _applySelection(product, sel) {
        const pos = this.env.services.pos;
        const basePrice = product.lst_price || product.price || 0;
        const extra = computePriceExtras(sel);
        const line = pos.addProduct(product);
        if (line?.set_unit_price) {
            line.set_unit_price(basePrice + extra);
        }
        const summary = `${sel.size} • ${sel.temperature} • ${sel.sweetness}`;
        if (line?.set_custom_description) {
            line.set_custom_description(summary);
        } else if (line?.set_note) {
            line.set_note(summary);
        }
        // 記憶選擇
        localStorage.setItem("beverage_last_selection", JSON.stringify(sel));
    },
});

