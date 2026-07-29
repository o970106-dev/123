
import subprocess
import sys

def main():
    """
    Runs the system check from manage_server.py.
    """
    try:
        command = [sys.executable, "manage_server.py", "check"]
        # Using Popen to stream output in real-time
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

        # Read and print stdout
        for line in process.stdout:
            print(line, end='')

        # Read and print stderr
        for line in process.stderr:
            print(line, end='', file=sys.stderr)

        process.wait()

        if process.returncode != 0:
            print(f"\n[INFO] 'manage_server.py' finished with return code {process.returncode}.", file=sys.stderr)
            # Do not exit with the same code, as the script itself ran successfully.
            # The underlying error is shown in the stderr stream.

    except FileNotFoundError:
        print("[ERROR] 'manage_server.py' not found. Please ensure the script is in the current directory.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[UNEXPECTED ERROR] An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
