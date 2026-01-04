import argparse
import json
import os
import sys
import subprocess

from paramiko import SSHClient, AutoAddPolicy, AuthenticationException, SSHException
from invoke import UnexpectedExit, Result

def load_config(config_path='config.json'):
    if not os.path.exists(config_path):
        print(f"[警告] 未找到 {config_path}，将尝试使用 config.example.json", file=sys.stderr)
        config_path = 'config.example.json'
        if not os.path.exists(config_path):
            print(f"[错误] {config_path} 也不存在，请创建您的 config.json", file=sys.stderr)
            sys.exit(1)

    with open(config_path) as f:
        return json.load(f).get('ssh', {})

def get_ssh_client(config):
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    auth_method = config.get('auth_method', 'key')

    try:
        if auth_method == 'key':
            key_path = os.path.expanduser(config.get('key_path', '~/.ssh/id_rsa'))
            if not os.path.exists(key_path):
                raise FileNotFoundError(f"SSH key not found at {key_path}")
            client.connect(config['host'], port=config.get('port', 22),
                           username=config['user'], key_filename=key_path, timeout=10)
        elif auth_method == 'password':
            client.connect(config['host'], port=config.get('port', 22),
                           username=config['user'], password=config['password'], timeout=10)
        else:
            raise ValueError(f"Unsupported authentication method: {auth_method}")

    except FileNotFoundError as e:
        print(f"[错误] {e}", file=sys.stderr)
        print("\n[提示] 请在 config.json 中提供正确的 SSH 私钥路径，", file=sys.stderr)
        print("或联系管理员以获取必要的凭据。", file=sys.stderr)
        sys.exit(1)
    except (AuthenticationException, SSHException) as e:
        print(f"[错误] SSH 认证失败: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[错误] 连接到 {config.get('host')} 时发生错误: {e}", file=sys.stderr)
        sys.exit(1)

    return client

def run_remote_command(client, command, sudo_pass=None):
    if 'sudo' in command and sudo_pass:
        # Use invoke for commands requiring sudo password
        try:
            from invoke import Connection
            conn = Connection(
                host=client.get_transport().getpeername()[0],
                user=client.get_transport().get_username(),
                connect_kwargs={
                    "pkey": client._get_pkey(),
                }
            )
            result = conn.sudo(command.replace('sudo', '').strip(), password=sudo_pass, pty=True)
            return result.exited, result.stdout, result.stderr
        except ImportError:
            print("[警告] `invoke` 库未安装，sudo 密码传递可能无法正常工作。", file=sys.stderr)
            print("请运行: pip install invoke", file=sys.stderr)
            # Fallback to basic exec_command without password
            pass
        except Exception as e:
            print(f"使用 invoke 执行 sudo 命令时出错: {e}", file=sys.stderr)
            # Fallback or re-raise
            pass


    stdin, stdout, stderr = client.exec_command(command, get_pty=True)
    exit_status = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    return exit_status, output, error

def main():
    parser = argparse.ArgumentParser(description="远程服务器管理工具")
    subparsers = parser.add_subparsers(dest='command', required=True)

    check_parser = subparsers.add_parser('check', help='检查服务器状态和更新')
    upgrade_parser = subparsers.add_parser('upgrade', help='更新服务器软件包')
    pro_status_parser = subparsers.add_parser('pro-status', help='检查 Ubuntu Pro/ESM 状态')
    release_check_parser = subparsers.add_parser('release-check', help='检查是否有新的发行版升级')
    run_parser = subparsers.add_parser('run', help='在远程服务器上执行任意命令')
    run_parser.add_argument('--cmd', required=True, help='要执行的命令')

    args = parser.parse_args()

    config = load_config()
    client = get_ssh_client(config)

    sudo_password = config.get('password')

    commands = {
        'check': [
            "echo '--- 系统信息 ---'", "uname -a",
            "echo '\n--- 可用更新 ---'", "apt list --upgradable 2>/dev/null | grep -v 'Listing...'",
        ],
        'upgrade': ["sudo apt-get update && sudo apt-get -y upgrade"],
        'pro-status': ["sudo pro status"],
        'release-check': ["do-release-upgrade -c"],
        'run': [args.cmd] if args.command == 'run' else [],
    }

    full_command = " && ".join(commands[args.command])

    print(f"在 {config['host']} 上执行: {full_command}\n")
    exit_status, output, error = run_remote_command(client, full_command, sudo_pass=sudo_password)

    if output:
        print(output)
    if error:
        print(f"错误输出:\n{error}", file=sys.stderr)

    client.close()

if __name__ == "__main__":
    main()
