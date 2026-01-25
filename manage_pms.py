import argparse
import os
import subprocess
import sys

MODS = ['pm', 'pf', 'vt', 'cc', 'sc', 'er']

def get_compose_path(mod):
    return os.path.join('pms_modules', mod, 'core', 'odoo19-shadow', 'docker-compose.yml')

def run_command(mod, action):
    compose_path = get_compose_path(mod)
    if not os.path.exists(compose_path):
        print(f"[Error] {compose_path} not found for module {mod}")
        return

    cmd = ['docker-compose', '-f', compose_path, action]
    if action == 'up':
        cmd.append('-d')

    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"[Success] Executed {action} for {mod}")
    except Exception as e:
        print(f"[Error] Failed to execute {action} for {mod}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Manage PMS Modules Lifecycle")
    parser.add_argument("action", choices=["up", "down", "restart", "logs"], help="Action to perform")
    parser.add_argument("--mod", choices=MODS + ['all'], default='all', help="Target module (default: all)")

    args = parser.parse_args()

    target_mods = MODS if args.mod == 'all' else [args.mod]

    for mod in target_mods:
        run_command(mod, args.action)

if __name__ == "__main__":
    main()
