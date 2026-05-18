/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ProductItem } from "@point_of_sale/app/screens/product_screen/product_item/product_item";
import { ModifierDialog } from "pos_beverage_modifier/static/src/components/modifier_dialog";

function getId(field) {
    if (Array.isArray(field)) return field[0];
    return field;
}

patch(ProductItem.prototype, "pos_beverage_modifier/ProductItem", {
    async onClick() {
        const product = this.props.product;
        const pos = this.env.services.pos;

        const productTmplId = getId(product.product_tmpl_id);
        const posCategId = getId(product.pos_categ_id);

        // Find configuration for this product
        const config = pos.models['pos.beverage.config'].find(c => {
            const configTmplId = getId(c.product_tmpl_id);
            const configCategId = getId(c.pos_category_id);
            return (configTmplId && configTmplId === productTmplId) ||
                   (configCategId && configCategId === posCategId);
        });

        if (config && config.show_popup) {
            // Fetch lines for this config
            const configLines = pos.models['pos.beverage.config.line'].filter(l => getId(l.config_id) === config.id);

            this.env.services.dialog.add(ModifierDialog, {
                product,
                config,
                configLines,
                onConfirm: (selection) => this._applySelection(product, selection),
            });
            return;
        }
        return this._super(...arguments);
    },
    _applySelection(product, sel) {
        const pos = this.env.services.pos;
        const basePrice = product.lst_price || product.price || 0;

        let extra = 0;
        const descriptions = [];

        if (sel.sweetness) {
            extra += sel.sweetness.price;
            descriptions.push(sel.sweetness.name);
        }
        if (sel.temperature) {
            extra += sel.temperature.price;
            descriptions.push(sel.temperature.name);
        }
        if (sel.size) {
            extra += sel.size.price;
            descriptions.push(sel.size.name);
        }

        const line = pos.addProduct(product);
        if (line?.set_unit_price) {
            line.set_unit_price(basePrice + extra);
        }

        const summary = descriptions.join(' • ');
        if (line?.set_custom_description) {
            line.set_custom_description(summary);
        } else if (line?.set_note) {
            line.set_note(summary);
        }

        // Memory for next time
        localStorage.setItem("beverage_last_selection_ids", JSON.stringify({
            sweetness: sel.sweetness?.id,
            temperature: sel.temperature?.id,
            size: sel.size?.id
        }));
    },
});
