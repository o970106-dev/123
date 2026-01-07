# 远程连接与管理 Ubuntu 服务器（Windows 环境）

本项目为 Windows 环境下，通过 SSH 连接和管理 Ubuntu 服务器及 Odoo POS 系统 的轻量工具集。

## 包含内容
- `config.example.json`：SSH 与 Odoo 连接配置模板
- `connect.ps1`：一键 SSH 交互连接脚本
- `manage_server.py`：服务器维护任务
- `diagnose_odoo.py`：检查 Odoo 连接状态
- `import_pos_menu.py`：从 Excel 导入 POS 菜单到 Odoo
- `requirements.txt`：Python 依赖

## 使用前准备

- 确保 Windows 已安装 OpenSSH 客户端。
- 准备好服务器和 Odoo 的登录信息。

## 快速开始

1. **配置**
   - 复制 `config.example.json` 为 `config.json`。
   - 根据您的环境填写 `ssh` 和 `odoo` 两部分的信息。

2. **安装依赖**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **服务器管理 (SSH)**
   - 交互式连接:
     ```powershell
     ./connect.ps1
     ```
   - 检查服务器状态:
     ```powershell
     python manage_server.py check
     ```

4. **Odoo POS 管理**
   - 首先，检查 Odoo 连接是否正常:
     ```powershell
     python diagnose_odoo.py
     ```
   - 然后，执行菜单导入 (详见下方 Odoo POS 管理部分)。

## 配置说明 (config.json)

配置文件 `config.json` 包含 `ssh` 和 `odoo` 两部分。

### SSH 配置
- `host`：服务器地址或公网 IP
- `port`：SSH 端口（默认 22）
- `user`：登录用户名
- `auth_method`：`key` 或 `password`
- `key_path`：私钥文件路径
- `password`：SSH 或 sudo 密码

### Odoo 配置
- `url`：Odoo 实例的 URL (例如 `https://your-odoo.com`)
- `db`：Odoo 数据库名称
- `login`：Odoo 管理员用户名
- `password`：Odoo 管理员密码

## Odoo POS 管理

### 1. 检查连接状态

在执行导入前，先检查 Odoo 连接配置是否正确：
```powershell
python diagnose_odoo.py
```
如果看到 `[ok]` 信息，表示连接成功。

### 2. 导入 POS 菜单 (Excel → Odoo)

**前置条件:**
- `config.json` 中已正确填写 `odoo` 相关配置。
- 已安装 `openpyxl` 依赖 (`pip install -r requirements.txt`)。
- 准备好菜单 Excel 文件。

**使用方式:**
- **预览模式** (不实际写入 Odoo):
  ```powershell
  python import_pos_menu.py --source .\path\to\your_menu.xlsx
  ```
- **实际导入** (读取 `config.json` 配置):
  ```powershell
  python import_pos_menu.py --source .\path\to\your_menu.xlsx --apply --update-existing
  ```

**说明:**
- 脚本会自动从 `config.json` 读取 Odoo 连接信息。
- 如需临时覆盖配置，仍可通过命令行参数传入，例如 `--url`、`--login` 等。

## 安全建议
- 优先使用 SSH 密钥认证。
- 不要将包含真实密码的 `config.json` 提交到版本控制。
