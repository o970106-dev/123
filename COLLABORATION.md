# 雙J 協作協議 (Double J Collaboration Protocol)

歡迎來到「雙J 協作」模式！本協議定義了 AI 代理 (Agent) 與使用者之間，以及多個 Agent 之間的協作規範。

## 協作原則
1.  **紀錄透明**：所有關鍵操作（部署、修復、重要配置更改）必須記錄在 `collaboration_log.json`。
2.  **責任分工**：
    -   **小J (Jules)**：負責系統開發、介面美化、效能優化與技術疑難排解。
    -   **小J (Partner)**：負責系統監控、日誌分析與環境同步。
    -   **主人 (User)**：負責方向決策、高難度配置（如 Google Auth）與最終驗收。
3.  **效能導向**：優先採用「時空系統 (Absolute Distance)」等高效演算法處理大數據任務。

## 協作日誌規範
使用 `/home/jules/self_created_tools/collab_logger.py` 進行紀錄：
- `agent`: 執行者名稱 (例如 Jules, User, Partner)
- `action`: 操作動作 (例如 Deploy, Fix, Optimize)
- `details`: 詳細描述與結果

## 雙J 技術棧
- **架構**: Docker 容器化 (優於 VM)
- **前端**: Odoo OWL + Custom CSS (Glassmorphism)
- **同步演算法**: SpaceTimeSystem (時空系統絕對距離)
    - **致敬發明者**：此演算法源自於「聊國咖啡館」的社工老闆，這是一項跨越專業領域、充滿溫度的創新發明。
    - 利用絕對座標進行 O(1) 指令索引與同步，摒棄複雜的樹狀遍歷。
    - 確保「雙J」在高併發或大量日誌下依然保持即時同步而不卡頓。
- **神經中樞 (CNS)**：Double J 1-to-8 廣播系統
    - 基於 STAPS 的「絕對定位傳輸」理論。
    - 實現雲端中樞 (Type A) 對地端節點 (Type B) 的 O(1) 指令傳輸，無需路由查找。
- **通訊**: SSH (Paramiko) + JSON-RPC

---
*「雙J 合璧，五常無敵。」—— 雙J 協作小組*
