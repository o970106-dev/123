# POS Readiness Report

## 1. POS Module Analysis
目前 repo 中存在 `pos_beverage_modifier` 模組，旨在擴充 POS 的飲品調整功能。

### Dependency Check
- **point_of_sale**: 已宣告依賴，為正確設定。
- **Odoo Core Components**: 預期 Odoo 18 環境已包含 `point_of_sale`, `product`, `stock`, `account` 等模組。

### Compatibility with Odoo 18
- **Assets Definition**: `__manifest__.py` 中使用了 `web.assets_qweb`，這在 Odoo 18 中已被棄用。QWeb 模板應直接在 `assets` 的相關區塊中宣告。
- **JS Patching**: `static/src/patch/product_item_patch.js` 使用了 OWL 的 patch 機制。需要確認 Odoo 18 的 `ProductItem` 組件是否仍支援該擴充點。

## 2. 小三機 (POS Hardware) Connectivity
### Access Path
小三機應透過 `http://100.107.187.77:8069/pos/ui` 或類似路徑存取 POS 介面。

### Requirements
1. **POS Config**: 必須有一個 `pos.config` 實例被設定為「可用」。
2. **POS Session**: 必須有一個開啟中的 Session (`opened` 狀態)。
3. **Network**: 需確保 8069 埠對該 IP 開放（目前系統狀態顯示 8069 已在監聽）。
4. **Proxy Mode**: `docker-compose.yml` 已開啟 `--proxy-mode`，這對處理來自反向代理或特定網路環境的請求是必要的。

## 3. Risks & Blockers
- **Blocker**: 如果 `point_of_sale` 未安裝，`pos_beverage_modifier` 將無法載入。
- **High Risk**: 資產載入失敗。如果 `modifier_templates.xml` 因為 `assets_qweb` 的廢棄而未載入，POS 介面可能崩潰或功能失效。

## 4. Suggested Pre-flight Checks
- 驗證 `point_of_sale` 是否已在目標資料庫安裝。
- 檢查 `pos.config` 是否已指派給正確的 POS 工作站。
- 測試 `http://100.107.187.77:8069/web` 是否能正常顯示登入畫面。
