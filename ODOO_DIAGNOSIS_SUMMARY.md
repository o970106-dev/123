# Odoo 18 Diagnosis Report

## 1. Executive Summary
目前系統處於「部分模組缺失」且「結構分散」的狀態。雖然 `pm3_base` 與 `pm3_identity` 的基本結構正確且語法通過檢查，但核心業務模組 `wuchang_m1_property` 以及關鍵的 `pm3_community` 缺少 `__manifest__.py` 或完全不存在於檔案系統中。POS 擴充模組 `pos_beverage_modifier` 雖然存在，但其 `assets` 定義仍使用舊版 QWeb 格式，可能在 Odoo 18 中造成載入問題。主要的 BLOCKER 是 `wuchang_m1_property` 的缺失，這將直接導致依賴該模組的功能失效。

## 2. Repository / Addons Map
偵測到的 Odoo Addons：
- `odoo18-shadow/addons/pm3_integrated_property/pm3_base`: 基礎治理模組。
- `odoo18-shadow/addons/pm3_integrated_property/pm3_identity`: 五維身份治理。
- `odoo18-shadow/addons/pm3_integrated_property/pm3_community`: 缺失 manifest，僅有 `__init__.py`。
- `odoo18-shadow/addons/wuchang_property_governance_18`: 僅有 `__init__.py`，為空殼。
- `odoo19-shadow/addons/pos_beverage_modifier`: POS 飲品調整模組。
- `pos_beverage_modifier/`: 重複的 POS 飲品調整模組（結構略有不同）。

## 3. Critical Findings
| Risk | File | Problem | Evidence | Suggested Fix |
| :--- | :--- | :--- | :--- | :--- |
| **BLOCKER** | `wuchang_m1_property` | 模組完全缺失 | 在 repo 中找不到 `wuchang_m1_property` 資料夾 | 從備份或原始分支還原該模組 |
| **BLOCKER** | `pm3_community/__manifest__.py` | 缺失 manifest | 目錄存在但找不到 manifest 檔案 | 建立 `__manifest__.py` 並定義依賴關係 |
| **HIGH** | `pos_beverage_modifier/__manifest__.py` | Odoo 18 資產格式不相容 | 使用了 `web.assets_qweb` | 將 `web.assets_qweb` 遷移至 `assets` 下的 `web.assets_backend` 或適當位置 |
| **MEDIUM** | `pos_beverage_modifier` | 模組冗餘 | 根目錄與 `odoo19-shadow` 下皆有該模組 | 統一保留一份，建議以 `odoo18-shadow` 為主進行適配 |
| **MEDIUM** | `odoo19-shadow/docker-compose.yml` | 映象本版與目標不符 | 使用 `image: odoo:19` 但目標是 Odoo 18 | 將 image 修改為 `odoo:18.0` |

## 4. POS / 小三機 Readiness
- **point_of_sale 依賴**：`pos_beverage_modifier` 已正確宣告依賴 `point_of_sale`。
- **啟用條件**：
  - Odoo 端需安裝 `point_of_sale` 模組。
  - 需建立至少一個 `pos.config` 及其關聯的 `pos.session`（可參考 `fix_pos_setup.py`）。
  - 小三機透過 `http://100.107.187.77:8069/web` 連入時，需確保網路通訊正常且 `db_filter` 未阻擋該 IP。
- **阻礙因素**：`pos_beverage_modifier` 的 JS Patch 語法需確認是否符合 Odoo 18 的 OWL 組件規範，且 QWeb 範本路徑可能需要調整。

## 5. Module Dependency Graph
```text
pm3_identity
└── pm3_base
    ├── base
    └── mail
contacts (via pm3_identity)

pos_beverage_modifier
└── point_of_sale
    ├── product
    ├── stock
    ├── account
    └── ... (Odoo core)

wuchang_m1_property (MISSING)
└── pm3_base (EXPECTED)
```

## 6. Files That Need Fix
- `odoo18-shadow/addons/pm3_integrated_property/pm3_community/__manifest__.py`: 需新增。
- `odoo19-shadow/addons/pos_beverage_modifier/__manifest__.py`: 需更新 `assets` 定義。
- `odoo19-shadow/docker-compose.yml`: 需檢查 version 與 addons 路徑對齊。

## 7. Minimal Safe Patch Plan
1. **補齊缺失 Manifest**：建立 `pm3_community/__manifest__.py`，確保其依賴 `pm3_base`。
   - *為什麼*：防止 Odoo 因找不到模組定義而無法載入。
   - *風險*：極低。
2. **修正 POS 資產定義**：將 `pos_beverage_modifier` 的 `web.assets_qweb` 併入 `point_of_sale.assets` 或適當區塊。
   - *為什麼*：Odoo 18 已棄用獨立的 `assets_qweb`。
   - *風險*：中（需驗證 OWL 元件載入）。
3. **建立 wuchang_m1_property 骨架**：若無法還原原始檔案，應先建立骨架避免其他模組依賴失敗。

## 8. Commands For User To Run Locally
```bash
# 檢查 Python 語法錯誤
python3 -m py_compile odoo18-shadow/addons/pm3_integrated_property/pm3_base/models/*.py

# 搜尋所有模組的依賴關係
grep -r "depends" odoo18-shadow/addons/ --include="__manifest__.py"

# 查看 Docker 日誌（僅限只讀觀察）
docker logs wuchang_os_odoo_18 --tail 100

# 執行 Odoo 啟動檢查（不寫入 DB）
# docker exec -it wuchang_os_odoo_18 odoo -d <your_db> -u pm3_base --stop-after-init --dry-run
```
