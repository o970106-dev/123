# Odoo Fix Plan

## Phase 1: Structural Repair
### 1. Fix Missing Manifests
建立 `odoo18-shadow/addons/pm3_integrated_property/pm3_community/__manifest__.py`：
```python
{
    'name': 'PM3 Community',
    'version': '18.0.1.0.0',
    'depends': ['pm3_base', 'pm3_identity'],
    'data': [],
    'installable': True,
}
```

### 2. Restore Core Modules
需從原始碼倉庫還原 `wuchang_m1_property` 到 `odoo18-shadow/addons/` 目錄。

## Phase 2: POS Compatibility Fix
### 1. Update `pos_beverage_modifier/__manifest__.py`
將資產宣告從：
```python
"web.assets_qweb": [
    "pos_beverage_modifier/static/src/xml/modifier_templates.xml",
],
```
改為併入 `point_of_sale.assets`：
```python
"assets": {
    "point_of_sale.assets": [
        "pos_beverage_modifier/static/src/patch/product_item_patch.js",
        "pos_beverage_modifier/static/src/components/modifier_dialog.js",
        "pos_beverage_modifier/static/src/css/modifier.css",
        "pos_beverage_modifier/static/src/xml/modifier_templates.xml",
    ],
},
```

## Phase 3: Infrastructure Adjustment
### 1. Align Docker Config
修改 `odoo19-shadow/docker-compose.yml` (或建立對應的 Odoo 18 compose 檔案)：
- `image: odoo:18.0`
- 確保 `volumes` 正確指向 `./addons`。

## Rollback Plan
- **Files**: 所有修改皆可透過 `git checkout` 撤銷。
- **Database**: 本計畫不涉及資料庫寫入，若執行 `upgrade` 後出現問題，應使用 `docker exec` 停止服務並還原 DB 備份。
