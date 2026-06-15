import subprocess, sys
from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parents[0] / "logs/logs.txt"

def run_ip_from_url_app(app: str):
    command = ["python", "-m", app]

    print("⏳ Get ip addess from url is running...")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Get ip addess from url app completed successfully.")
        if result.stdout:
            with open(LOGS_DIR, mode="w") as file:
                file.write(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Get ip addess from url app error: {e.stderr}", file=sys.stderr)
    except FileNotFoundError as e:
        print(f"❌ Command not found: {command[0]}. Check your PATH.", file=sys.stderr)