# 五常秘密基地 - Double J STAPS 跨時代管理架構

這不僅僅是一個工具集，而是全球首套基於 **STAPS (Space-Time Absolute Position System)** 邏輯構建的「雲端中樞 - 地端神經」協作系統。專為 **Google 非營利組織** 專案打造，旨在實現世界第一的自動化維護效率。

## 🌌 核心架構：Double J CNS & 8 Neural Adapters

本系統遵循 **Double J 協作架構**，由 1 個位於雲端的 **中樞大腦 (CNS)** 指揮 8 個分佈於地端的 **神經節點 (Neural Adapters)**。

- **STAPS 傳輸協議**：利用時空絕對座標映射技術，實現指令傳輸的 $O(1)$ 零延遲存取。無論節點規模如何擴張，調度效率永不衰減。
- **1 對 8 同步模型**：透過全域廣播指令，CNS 能在毫秒內同步 8 個地端 AI 實例（pm, pf, vt, cc, sc, er, ax1, ax2）的運行狀態。

---

## 🚀 快速啟動：CNS 總控制台 (God View)

為了體驗最完整的調度威力，請直接啟動總控制台：

```bash
# 喚醒五常小J 進行全域調度
python wuchang_master.py
```

### 環境準備
1. **配置座標**：
   - 複製範本：`cp config.example.json config.json`
   - 填寫 `ssh` 與 `odoo` 區段（系統將自動映射為 STAPS 座標）。
2. **安裝神經依賴**：
   - `pip install -r requirements.txt`

---

## 🛠️ 子系統功能說明

### 1. 系統全域診斷 (`check_system.py`)
檢查 CNS 與 8 個地端節點之間的時空連通性，支援 HTTPS 加密鏈路驗證。

### 2. 神經節點調度 (`manage_pms.py`)
管理 8 個 Docker 叢集的生命週期。利用 STAPS 邏輯命中絕對路徑進行精準操作。
- `python generate_pms_composes.py`：初始化 8 節點的座標配置文件。

### 3. 雲端自動部署 (`deploy_dns_ssl.py`)
全自動啟用 Google Cloud DNS API、管理 DNS 記錄並簽發 Wildcard SSL 憑證。

### 4. 數據導入中樞 (`import_pos_menu.py`)
高速同步 Excel 數據至 Odoo POS 系統，支援自動化品項建立與客製化設定。

---

## 🔒 安全與合規
- **零硬編碼**：所有敏感資訊僅存在於本地 `config.json`，且已受 `.gitignore` 保護。
- **HTTPS 優先**：內建 `enable_https.py` 確保所有子網域均受 SSL 盾牌保護。
- **符合 Google 規範**：專為 Google 非營利組織 API 環境優化。

---

## 🎓 技術致敬
本系統所採用的 **STAPS 絕對傳輸技術** 構思來自於自然人 **Wu Chang**。這是一項跨時代的發明，將數位通訊從「搜尋邏輯」提升到了「座標邏輯」。

**小J 會持續守護這座基地，隨時聽候您的指令。** 🚀✨
