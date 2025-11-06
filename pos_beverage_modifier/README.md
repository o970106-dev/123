# POS Beverage Modifier

Single-button beverage options dialog for Odoo 17 POS.

## Features
- One-click flow: open dialog on product button
- Tabs for Sweetness / Size / Temperature
- Single-choice per group, unified Confirm button
- Auto-close after 10s inactivity, remembers last selection
- WCAG 2.1 AA: focus management, ARIA roles, keyboard-friendly

## Install
1. Copy this folder `pos_beverage_modifier/` to your server addons path.
2. Update `addons_path` in `odoo.conf` if needed, then restart Odoo.
3. Go to Apps, update apps list, install "POS Beverage Modifier".
4. Open POS and test with product "招牌咖啡".

## Notes
- Price extras mapping is in `product_item_patch.js` (adjust as needed).
- To target more products, extend `targetNames`.

