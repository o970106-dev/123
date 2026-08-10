# 远程连接与管理 Ubuntu 服务器（Windows 环境）

本项目为 Windows 环境下，通过 SSH 连接和管理 Ubuntu 服务器及 Odoo 应用的工具集。

## 主要功能

- **SSH 连接**: 一键式 PowerShell 脚本 (`connect.ps1`)，用于快速建立交互式 SSH 会话。
- **服务器管理**: Python 脚本 (`manage_server.py`)，提供常见的维护任务，如系统更新、状态检查、远程命令执行等。
- **Odoo POS 菜单导入**: 功能强大的脚本 (`import_pos_menu.py`)，可将结构化的 Excel 菜单数据批量导入 Odoo 的 POS 系统。

## 使用前准备

1. **安装依赖**:
   - **OpenSSH 客户端**: Windows 10/11 通常已内置。可在 PowerShell 中运行 `ssh -V` 进行验证。
   - **Python**: 建议使用 Python 3.8 或更高版本。
   - **Python 依赖库**:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     pip install -r requirements.txt
     ```

2. **准备服务器信息**:
   - **SSH**: `host`, `port`, `user` 以及认证方式（密钥路径或密码）。
   - **Odoo**: Odoo 服务器的 `url`, `db` 名称, `login` 用户名和 `password`。

## 快速开始

1. **创建配置文件**:
   - 将 `config.example.json` 复制为 `config.json`。
   - 根据您的服务器和 Odoo 信息填写 `ssh` 和 `odoo` 两部分的内容。

2. **SSH 连接与管理**:
   - **交互式连接**:
     ```powershell
     ./connect.ps1
     ```
   - **服务器维护**:
     ```powershell
     # 检查系统更新与 Pro/ESM 状态
     python manage_server.py check

     # 执行系统升级
     python manage_server.py upgrade

     # 远程执行任意命令
     python manage_server.py run --cmd "uname -a"
     ```

## 配置说明 (`config.json`)

配置文件分为 `ssh` 和 `odoo` 两个主要部分：

### `ssh` 配置
- `host`: 服务器地址或公网 IP。
- `port`: SSH 端口（默认 22）。
- `user`: 登录用户名。
- `auth_method`: 认证方式，`key` 或 `password`（建议使用 `key`）。
- `key_path`: SSH 私钥文件的绝对路径。
- `password`: 登录密码（若使用密码认证）。

### `odoo` 配置
- `url`: Odoo 服务器的访问地址（例如 `http://your.odoo.server:8069`）。
- `db`: 要操作的 Odoo 数据库名称。
- `login`: Odoo 管理员用户名。
- `password`: Odoo 管理员密码。

> **安全提示**: `config.json` 已被列入 `.gitignore`，不会被提交到版本控制中，以保护您的敏感信息。

## Odoo POS 菜单导入 (`import_pos_menu.py`)

此脚本用于将 Excel 文件中的菜单数据导入 Odoo，自动创建或更新商品及 POS 分类。

### 使用方式

1. **准备 Excel 文件**:
   - 确保第一行为表头。
   - 至少包含「品名/名稱」、「售價/價格」、「類別/分類」三列。
   - 脚本会自动识别常见的中文和英文字段名。

2. **执行导入**:
   - **预览模式** (不实际写入 Odoo):
     ```powershell
     python import_pos_menu.py --source .\data\source_menu.xlsx
     ```
   - **应用模式** (写入 Odoo):
     ```powershell
     # 脚本将从 config.json 读取 Odoo 连接信息
     python import_pos_menu.py --source .\data\source_menu.xlsx --apply --update-existing
     ```
   - **覆盖配置** (通过命令行参数覆盖 `config.json` 中的设置):
     ```powershell
     python import_pos_menu.py --source .\data\source_menu.xlsx --apply \
       --url http://custom.odoo.url --login user --password pass --db custom_db
     ```

### 功能说明
- **自动分类**: 如果 Excel 中指定的 POS 类别不存在，脚本会自动创建。
- **商品更新**: 使用 `--update-existing` 参数，脚本会根据商品名称更新已存在的记录。
- **版本兼容**: 自动处理不同 Odoo 版本中 POS 分类字段的差异 (`pos_category_id` vs `pos_categ_id`)。

## 常见问题

- **SSH `sudo` 权限**: 确保 `manage_server.py` 所用的用户具有 `sudo` 权限，并在 `config.json` 的 `ssh` 部分填写了 `password`，以便脚本自动处理需要密码的 `sudo` 命令。
- **数据库未找到**: 确保 `config.json` 中的 `db` 名称正确，或 Odoo 服务器上至少存在一个数据库。
