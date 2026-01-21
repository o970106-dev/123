import argparse
import subprocess
import os

MODS = ['pm', 'pf', 'vt', 'cc', 'sc', 'er']
DEFAULT_BASE_PATH = "/{mod}/core/odoo19-shadow"

def run_command(mod, cmd_list, base_path_template):
    # Path logic as per create_modules.py
    path = base_path_template.format(mod=mod)
    if not os.path.exists(path):
        print(f"Directory {path} does not exist. Skipping.")
        return

    print(f"Executing for {mod} in {path}: {' '.join(cmd_list)}")
    try:
        # Using list-based command and cwd for better security/reliability
        subprocess.run(cmd_list, cwd=path, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command for {mod}: {e}")
    except FileNotFoundError:
        print(f"Command {' '.join(cmd_list)} not found.")

def main():
    parser = argparse.ArgumentParser(description="PMS Multi-module Orchestrator")
    parser.add_argument("action", choices=["up", "down", "ps", "logs", "restart"])
    parser.add_argument("--mod", help="Specific module to target (default: all)")
    parser.add_argument("--base-path", default=DEFAULT_BASE_PATH, help="Template for base path (e.g. '/{mod}/core/...')")

    args = parser.parse_args()

    targets = [args.mod] if args.mod else MODS

    cmd_map = {
        "up": ["docker-compose", "up", "-d"],
        "down": ["docker-compose", "down"],
        "ps": ["docker-compose", "ps"],
        "logs": ["docker-compose", "logs", "--tail=20"],
        "restart": ["docker-compose", "restart"]
    }

    for mod in targets:
        run_command(mod, cmd_map[args.action], args.base_path)

if __name__ == "__main__":
    main()
