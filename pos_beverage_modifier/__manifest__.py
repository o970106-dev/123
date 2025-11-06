{
    "name": "POS Beverage Modifier",
    "summary": "Single-button beverage options dialog (sweetness/size/temperature)",
    "version": "19.0.1.0",
    "category": "Point of Sale",
    "depends": ["point_of_sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/beverage_config_views.xml",
        "data/beverage_demo.xml",
    ],
    "assets": {
        "point_of_sale.assets": [
            "pos_beverage_modifier/static/src/patch/product_item_patch.js",
            "pos_beverage_modifier/static/src/components/modifier_dialog.js",
            "pos_beverage_modifier/static/src/css/modifier.css",
        ],
        "web.assets_qweb": [
            "pos_beverage_modifier/static/src/xml/modifier_templates.xml",
        ],
    },
    "author": "Wuchang Life",
    "license": "OEEL-1",
}

