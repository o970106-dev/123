#!/usr/bin/env python3
import subprocess
import sys

def main():
    print("Starting system diagnostic check...")
    try:
        # Execute manage_server.py check
        result = subprocess.run(
            [sys.executable, "manage_server.py", "check"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Errors/Warnings during check:")
            print(result.stderr)

        if result.returncode == 0:
            print("System connectivity check completed successfully.")
        else:
            print(f"System connectivity check failed with return code {result.returncode}.")
            sys.exit(result.returncode)

    except Exception as e:
        print(f"An error occurred while running the diagnostic check: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
