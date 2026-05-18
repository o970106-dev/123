/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ProductItem } from "@point_of_sale/app/screens/product_screen/product_item/product_item";
import { ModifierDialog } from "pos_beverage_modifier/static/src/components/modifier_dialog";

/**
 * TODO: Fetch these mappings from the backend pos.beverage.config model
 * for full dynamic behavior. Currently hardcoded for performance and stability.
 */
const BEVERAGE_PRICE_MAPPING = {
    sweetness: { "更換蔗糖": 5 },
    temperature: { "冰沙": 10 },
    size: {
        "大杯 (600cc)": 30,
        "小杯 (350cc)": -15
    }
};

/**
 * Products that should trigger the beverage modifier dialog.
 * TODO: Implement category-based check or backend flag.
 */
const TARGET_PRODUCT_NAMES = ["招牌咖啡"];

function computePriceExtras(sel) {
    let extra = 0;
    if (sel?.sweetness && BEVERAGE_PRICE_MAPPING.sweetness[sel.sweetness]) {
        extra += BEVERAGE_PRICE_MAPPING.sweetness[sel.sweetness];
    }
    if (sel?.temperature && BEVERAGE_PRICE_MAPPING.temperature[sel.temperature]) {
        extra += BEVERAGE_PRICE_MAPPING.temperature[sel.temperature];
    }
    if (sel?.size && BEVERAGE_PRICE_MAPPING.size[sel.size]) {
        extra += BEVERAGE_PRICE_MAPPING.size[sel.size];
    }
    return extra;
}

patch(ProductItem.prototype, "pos_beverage_modifier/ProductItem", {
    async onClick() {
        const product = this.props.product;
        // Check if the product is in the target list
        if (TARGET_PRODUCT_NAMES.includes(product.display_name)) {
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

