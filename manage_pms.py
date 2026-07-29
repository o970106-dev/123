#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys

# Modules as defined in the PMS architecture
MODULES = ['pm', 'pf', 'vt', 'cc', 'sc', 'er']

def get_module_path(module, base_dir=None):
    """
    Determines the path to the module's docker-compose directory.
    Precedence:
    1. Base directory provided via argument.
    2. Absolute path from architecture (/{module}/core/odoo19-shadow).
    3. Relative path from current working directory (./odoo19-shadow/modules/{module}).
    """
    if base_dir:
        return os.path.join(base_dir, module)

    # Architecture path
    abs_path = f"/{module}/core/odoo19-shadow"
    if os.path.exists(abs_path):
        return abs_path

    # Local fallback for development/sandbox
    local_path = os.path.join(os.getcwd(), 'odoo19-shadow', 'modules', module)
    # Check if we should use the root odoo19-shadow for all (if modules are not split)
    if not os.path.exists(local_path) and os.path.exists(os.path.join(os.getcwd(), 'odoo19-shadow')):
         return os.path.join(os.getcwd(), 'odoo19-shadow')

    return local_path

def run_docker_command(module, command, base_dir=None):
    path = get_module_path(module, base_dir)
    if not os.path.exists(path):
        print(f"Error: Path {path} for module {module} does not exist.")
        return False

    # Try to find docker-compose.yml or docker-compose.fixed.yml (seen in repo)
    compose_files = ['docker-compose.yml', 'docker-compose.fixed.yml']
    compose_file = None
    for cf in compose_files:
        if os.path.exists(os.path.join(path, cf)):
            compose_file = cf
            break

    if not compose_file:
        print(f"Error: No docker-compose file found in {path}")
        return False

    cmd = ['docker-compose', '-f', compose_file, command]
    print(f"Executing: {' '.join(cmd)} in {path}")

    try:
        # Actually execute the command
        subprocess.run(cmd, cwd=path, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return False
    except FileNotFoundError:
        print("Error: docker-compose command not found. Please ensure Docker is installed.")
        return False

def main():
    parser = argparse.ArgumentParser(description="PMS Module Orchestrator")
    parser.add_argument("command", choices=['up', 'down', 'restart', 'logs', 'ps', 'build'], help="Docker-compose command")
    parser.add_argument("--module", choices=MODULES + ['all'], default='all', help="Target module (default: all)")
    parser.add_argument("--base-dir", help="Manually specify base directory for modules")

    args = parser.parse_args()

    target_modules = MODULES if args.module == 'all' else [args.module]

    success = True
    for mod in target_modules:
        if not run_docker_command(mod, args.command, args.base_dir):
            success = False

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
