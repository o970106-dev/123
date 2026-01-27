# 五常小J 的秘密基地 - 遠端管理與 PMS 工具集

這是一個專為五常專案開發的輕量化工具集，用於管理 Ubuntu 伺服器、Odoo POS 系統以及物業管理 (PMS) 模組。

## 核心建築願景：Double J Architecture & STAPS

本專案遵循 **Double J 協作架構**，旨在實現雲端中樞 (CNS) 與地端神經適配器 (Neural Adapter) 的完美同步。

- **時空絕對位置系統 (STAPS)**：利用絕對座標映射實現 $O(1)$ 零延遲存取，確保指令能跨越空間直接命中目標。
- **1 對 8 調度模型**：最優化調度效率，由 1 位雲端中樞統一指揮 8 個關鍵地端節點，達成全系統同步。

## 核心功能

- **系統診斷** (`check_system.py`): 一鍵檢查 SSH 與 Odoo API 的連線狀態。
- **伺服器管理** (`manage_server.py`): 遠端執行 `apt update`, `upgrade`, 查看 Pro 狀態等維護任務。
- **PMS 模組管理** (`manage_pms.py`): 統一管理多個物業管理模組（pm, pf, vt, cc, sc, er）的 Docker 生命週期。
- **POS 菜單導入** (`import_pos_menu.py`): 從 Excel 快速導入品項與客製化設定至 Odoo。
- **一鍵連線** (`connect.ps1`): PowerShell 下的快速 SSH 互動式連線。

## 快速開始

### 1. 配置環境

- 複製配置範本：
  ```bash
  cp config.example.json config.json
  ```
- 按需求填寫 `config.json` 中的 `ssh` 與 `odoo` 區段。

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 系統診斷

在開始操作前，建議先執行診斷：
```bash
python check_system.py
```

## 使用說明

### 伺服器維護 (`manage_server.py`)

- 查看更新狀態：`python manage_server.py check`
- 執行系統升級：`python manage_server.py upgrade`
- 執行自訂命令：`python manage_server.py run --cmd "df -h"`

### 物業管理模組 (`manage_pms.py`)

- 生成模組配置：`python generate_pms_composes.py`
- 啟動所有模組：`python manage_pms.py up -d`
- 查看模組狀態：`python manage_pms.py ps`
- 重啟特定模組：`python manage_pms.py restart --module sc`

### POS 菜單導入 (`import_pos_menu.py`)

- 預覽導入：`python import_pos_menu.py --source .\data\menu.xlsx`
- 實際執行：`python import_pos_menu.py --source .\data\menu.xlsx --apply --update-existing`

## 使用前準備

- 確保 Windows 已安裝 OpenSSH 客戶端（PowerShell 執行 `ssh -V` 驗證）。
- 準備好伺服器的登入方式（建議使用 SSH 私鑰）。
- 獲取伺服器連線資訊：`host`、`port`（預設 22）、`user`、私鑰路徑或密碼。

## 配置說明 (config.json)

`config.json` 採用巢狀結構區分 SSH 與 Odoo 配置：

```json
{
  "ssh": {
    "host": "your.server.ip",
    "port": 22,
    "user": "ubuntu",
    "auth_method": "key",
    "key_path": "C:\\Users\\<you>\\.ssh\\id_rsa",
    "password": null
  },
  "odoo": {
    "url": "http://your.odoo.url",
    "db": "your_database",
    "login": "admin",
    "password": "your_password"
  }
}
```

## 安全建議
- 優先使用密鑰認證，並為私鑰設置口令。
- 不要將真實密碼提交到版本控制；`config.json` 已被列入 `.gitignore`。
- 初次連線建議啟用 `StrictHostKeyChecking=accept-new`。

## 常見問題
- 遠端命令需要 `sudo` 權限時：確保帳號在 `sudoers`，並在 `config.json` 填寫 `password`。
- `do-release-upgrade` 通常為互動式流程，`manage_server.py` 僅做檢查；實際升級請在互動 SSH 會話中執行。

## 參考連結
- 官方文件：`https://help.ubuntu.com`
- Odoo RPC 客戶端：`https://github.com/odoo/odoo-rpc-client` (或本專案內建 `odoo_jsonrpc.py`)
