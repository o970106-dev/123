# 五常溫馨小家 - 開發與維護指南 (AGENTS.md)

歡迎來到五常小J 的開發世界！本指南旨在幫助您了解如何維護這個「家」，並保持其整潔與優雅。

## 核心理念
- **簡約而不簡單**：優先使用容器化 (Docker) 而非虛擬化 (VM)，以保持系統輕量與高效。
- **使用者中心**：所有功能的設計應以「住戶」與「管理員」的體驗為首位。
- **結構清晰**：腳本與代碼應分類存放，避免根目錄過於混亂。

## 目錄結構
- `/odoo19-shadow/`：主服務部署目錄，包含 Docker Compose 與主要插件。
- `/pos_beverage_modifier/`：POS 飲品優化插件，負責美化點單體驗。
- `/odoo19-shadow/addons/pf_resident_portal/`：住戶門戶中心，提供統一的「家」的管理入口。
- `*.py` (根目錄)：管理工具腳本，應定期整理或整合至管理類別中。

## 開發規範
1. **美化與設計**：
   - 使用 `fa` 圖標 (FontAwesome) 增加可視化指引。
   - 保持 Traditional Chinese (繁體中文) 輸出，以符合當地使用習慣。
2. **安全性**：
   - 不得將 `config.json` 提交至版本控制，應始終維護 `config.example.json`。
3. **自動化**：
   - 優先開發自動化腳本來處理重複性任務（如 `import_pos_menu.py`）。

## 維護清單
- 定期執行 `python manage_server.py check` 檢查系統狀態。
- 更新 POS 菜單後，使用 `python import_pos_menu.py --apply` 同步數據。

---
*「家，是心之所在。代碼，是築家的基石。」—— 五常小J*
