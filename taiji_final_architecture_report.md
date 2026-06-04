# 🚀 封包網關系統架構稽核與根因報告

## 📌 執行摘要
系統經歷了從「邊緣節點」到「主網關」的演化過程（如同 Git 紀錄中的 `M014 finalize remaining canonical baseline` 版本更新）。然而，在系統服務（systemd）的層面，舊版的邊緣節點並沒有被徹底關閉。這導致新舊兩代網關在同一個通道（Port `9002`）發生了實體座標碰撞。舊網關（`taiji_unified_gateway_edge.py`）因為搶不到通道而崩潰，每次系統服務（`wuchang-gateway-9002.service`）將其重啟時又會觸發它內建的「顯示卡記憶體預熱機制 (GPU Enforcer)」，最終引發了 Ollama 運算資源滿載與 WSL 記憶體暴增到 14GB 的災難。

## A. 當前系統運行拓撲
目前的日誌顯示系統正處於「雙網關精神分裂 (Split-Brain Gateway)」的破缺狀態：
1. **[運作中/已佔用] 新主網關** (`services.gateway.main:app`) 成功佔用了 `127.0.0.1:9002` 這個通道。
2. **[運作中/無限崩潰] 舊邊緣網關** (`taiji_unified_gateway_edge.py`) 被系統服務喚醒，不斷嘗試去搶同一個 9002 通道，搶輸了就崩潰。
3. **[背景受害者] 算力引擎**：Ollama 運行在 `127.0.0.1:11434`，只能被動地承受舊邊緣網關每次崩潰重啟時發送的「模型載入」預熱攻擊。

## B. 重複的服務
從系統進程列表 (`ps aux`) 與 Git 歷史紀錄中，找到了「表面單一，實際多根」的鐵證：

*   **真正的單根 (The New Root)**: `/usr/bin/python3 -m uvicorn services.gateway.main:app --host 127.0.0.1 --port 9002` (PID: 311)
*   **幽靈多根 (The Ghost Root)**: `python taiji_unified_gateway_edge.py` (PID: 32882，由 `wuchang-gateway-9002.service` 這個 systemd 服務啟動)。
*   *(附帶發現)*: 甚至還有另一個新主網關的程式運行在 `8081` 通道：`python3 -m uvicorn services.gateway.main:app --host 127.0.0.1 --port 8081` (PID: 569)。

## C. 通道（埠號）衝突
*   **衝突的通道**: `127.0.0.1:9002`
*   **證據**:
    *   系統網路狀態 `ss -lntp | grep 9002` 顯示進程 PID 311 已經在監聽 (LISTEN) 9002 通道。
    *   `systemctl --user status wuchang-gateway-9002` 的日誌顯示，它啟動的 PID 32882 必然會遇到「位址已被使用 (Address already in use)」的錯誤而崩潰。

## D. Ollama 被無限喚醒的來源與 WSL 記憶體暴增原因
日誌精準地抓出了這 100 多次 Ollama 被喚醒，以及 WSL 記憶體被 5GB 模型塞滿的「元凶程式碼」：
*   **觸發點所在檔案**: `taiji_unified_gateway_edge.py`
*   **觸發點程式碼特徵 (Line Evidence)**:
    ```python
    @app.on_event("startup")
    ```
*   **觸發邏輯日誌**:
    ```text
    Jun 04 13:07:01 MSI bash[32882]: 2026-06-04 13:07:01,779 [VoiceEngine-Realtime] 🔧 [GPU Enforcer] Initiating strict VRAM...
    Jun 04 13:07:01 MSI bash[32882]: 2026-06-04 13:07:01,813 [VoiceEngine-Realtime] HTTP Request: POST http://127.0.0.1:11434
    ```
*   **病理分析**: 每次 `wuchang-gateway-9002.service` 因為搶不到 9002 通道而崩潰重啟時，都會先執行 FastAPI 的 `@app.on_event("startup")` 鉤子。這個名為 `[GPU Enforcer]` 的機制會立刻對 `http://127.0.0.1:11434` (Ollama) 發出 POST 請求進行 VRAM 預熱。這就是 **WSL 記憶體暴增與 CPU 飆升的絕對根本原因**。

## E. 建議保留的服務
*   `services.gateway.main` (目前確認收斂的單根主網關)。
*   Ollama (`ollama.service`) 與 OpenWebUI (`taiji-03-ui.service`, `openwebui_bridge`) 橋接相關的服務。
*   `wuchang-v15-9090.service` (五常/核心業務邏輯)。

## F. 建議移除的服務
*   **`wuchang-gateway-9002.service`**：這是一個過時的系統服務，它還在呼叫舊的 `taiji_unified_gateway_edge.py`。
*   *(註)* 根據您的 Git 紀錄（`M013 add deploy edge and cloud canonical baseline`），您其實已經將 `taiji_unified_gateway_edge.py` 移入或歸類到 `legacy_core/`，但您的 systemd 開機啟動腳本沒有跟著退役，導致它從墳墓裡爬出來作怪。

## G. 安全的修復與遷移步驟
請在終端機輸入以下指令：
1. **停止無限死亡迴圈**:
   `systemctl --user stop wuchang-gateway-9002.service`
2. **徹底拔除幽靈網關**:
   `systemctl --user disable wuchang-gateway-9002.service`
3. **確認新網關狀態**:
   確認 `taiji-gateway.service` 才是負責啟動新網關 (`services.gateway.main:app`) 的正確服務。

## H. 風險評估
您昨天的 Git 檔案傳輸測試，很有可能是不小心觸發了系統重新讀取設定，或者是拉取到了舊版的開機設定，才導致這個已經廢棄的 `wuchang-gateway-9002.service` 被重新打開。
這證明了架構演進中的「多根陷阱」確實存在。只要停用這個「幽靈服務」，系統狀態就會收斂，Ollama 也不會再被瘋狂轟炸了。