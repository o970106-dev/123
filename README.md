# 远程连接与管理 Ubuntu 服务器（Windows 环境）

本项目为 Windows 环境下，快速通过 SSH 连接并管理 Ubuntu 服务器的轻量工具集。

包含内容：
- `config.example.json`：配置模板（主机、端口、用户、密钥路径等）
- `connect.ps1`：一键 SSH 交互连接脚本
- `manage_server.py`：常见维护任务（更新、ESM/Pro状态、升级检查、任意命令执行）
- `requirements.txt`：Python 依赖（Paramiko, Requests, OpenPyXL）
- `import_pos_menu.py`：从 Excel 导入 POS 菜单到 Odoo 的脚本
- `check_system.py`：**（新）** 一键检查服务器与 Odoo 服务状态的诊断脚本

## 使用前准备

- 确保 Windows 已安装 OpenSSH 客户端（Windows 10/11 默认包含，可在 PowerShell 运行 `ssh -V` 验证）。
- 准备好服务器的登录方式（建议使用 SSH 私钥）。
- 获取服务器与 Odoo 的连接信息。

## 快速开始

1. 复制配置模板：
   - 将 `config.example.json` 复制为 `config.json`
   - 按您的服务器信息填写：

2. 交互式 SSH 连接：
   - 在 PowerShell 中运行：
     ```powershell
     ./connect.ps1
     ```

3. 安装 Python 依赖：
   - 在 PowerShell 中运行：
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     pip install -r requirements.txt
     ```

4. **系统健康检查**：
   - 运行全面的服务器与 Odoo 状态检查：
     ```powershell
     python check_system.py
     ```

5. 常见维护任务：
   - 查看更新与状态检查（仅服务器）：
     ```powershell
     python manage_server.py check
     ```
   - 执行系统更新（`apt update && apt upgrade -y`）：
     ```powershell
     python manage_server.py upgrade
     ```
   - 在远端执行任意命令：
     ```powershell
     python manage_server.py run --cmd "uname -a"
     ```

## 配置说明（config.json）

配置文件分为 `ssh` 和 `odoo` 两个部分。

### SSH 配置 (`ssh`)
- `host`：服务器地址或公网 IP
- `port`：SSH 端口（默认 22）
- `user`：登录用户名（如 `ubuntu`）
- `auth_method`：`key` 或 `password`（建议 `key`）
- `key_path`：私钥文件路径（`auth_method: "key"` 时使用）
- `password`：密码（`auth_method: "password"` 时使用；不建议存明文）

### Odoo 配置 (`odoo`)
- `url`：Odoo 实例的 URL (例如 `https://your.domain.com`)
- `db`：要连接的数据库名称
- `login`：Odoo 管理员用户名
- `password`：Odoo 管理员密码

> 注：如使用密码登录，`connect.ps1` 会在连接时交互式提示输入密码；`manage_server.py` 会在需要 `sudo` 时将密码通过安全方式传入（如配置了 `password`）。

## 安全建议
- 优先使用密钥认证，并为私钥设置口令。
- 不要将真实密码提交到版本控制；如需使用密码，在本地 `config.json` 中暂存或运行时输入。
- 初次连接建议启用 `StrictHostKeyChecking=accept-new`，后续保持主机指纹校验。

## 常见问题
- 远程命令需要 `sudo` 权限时：确保账号在 `sudoers`，并在 `config.json` 填写 `password` 或配置免密 `sudo`（谨慎）。
- `do-release-upgrade` 通常为交互式流程，脚本中使用 `-c` 仅做检查；实际升级请在交互 SSH 会话中执行。

## 导入 POS 菜单（Excel → Odoo）

前置：
- 安装依赖：`pip install -r requirements.txt`（需要 `openpyxl`）
- 准备 Excel：第一行是表头，至少包含「品名/名稱」「售價/價格」「類別/分類」三欄（英文亦可：`name`、`price`、`category`）。

使用方式：
- 预览（不写入）：
  ```powershell
  python import_pos_menu.py --source .\data\source_menu.xlsx
  ```
- 实际写入 Odoo（建立/更新品项与 POS 類別）：
  ```powershell
  python import_pos_menu.py --source .\data\source_menu.xlsx --apply --update-existing \
    --url http://34.80.194.190 --login admin@wuchang.life --password poiuY926
  ```
- 可选参数：`--sheet <工作表名稱>`、`--db <資料庫>`。

说明：
- 脚本会尝试自动识别表头中的常见中文/英文字段，并创建缺失的 `pos.category`，将商品导入为 `product.template`（`available_in_pos=True`）。
- 若 Odoo 版本字段为 `pos_categ_id`（旧版）脚本会自动回退处理。

## 参考链接
- 文档参考：`https://help.ubuntu.com`
- 管理工具：`https://landscape.canonical.com`
- 技术支持：`https://ubuntu.com/pro`
- ESM 扩展安全维护：`https://ubuntu.com/esm`
