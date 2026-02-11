
import subprocess
import sys

def main():
    """
    Runs the system check by calling the manage_server.py script.
    """
    print("Starting system health check...")
    print("="*30)

    try:
        # Define the command to be executed
        command = [sys.executable, "manage_server.py", "check"]

        # Execute the command using subprocess.run()
        # This is a simpler and safer way to run a subprocess and capture its output.
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        # Print stdout and stderr
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        print("="*30)

        if result.returncode == 0:
            print("System health check completed successfully.")
        else:
            print(f"System health check failed with return code {result.returncode}.")

    except FileNotFoundError:
        print("Error: 'manage_server.py' not found. Make sure you are in the correct directory.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
