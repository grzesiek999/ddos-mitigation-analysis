import random, math, json, subprocess, sys
from pathlib import Path
from utils.proxy_select_app.run import run_proxy_select_app

PROXY_RESULTS_DIR = Path(__file__).resolve().parents[1] / "utils/proxy_select_app/results/results.json"
PROXY_POOL_DIR = Path(__file__).resolve().parents[1] / "data/proxypool.json"

# Return random choice from list
def random_choice(array):
    return random.choice(array)

# Calculate percentile
def percentile(data, p):
    data = sorted(data)
    if not data:
        return None
    k = (len(data)-1) * (p/100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return data[int(k)]
    d0 = data[int(f)] * (c-k)
    d1 = data[int(c)] * (k-f)
    return d0+d1

# Load config
def load_json(filename):
    path = filename
    if not path.exists():
        raise FileNotFoundError(f"File {filename} not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))

# Select allive proxy
def select_allive_proxy():
    run_proxy_select_app()

    command = ["cp", PROXY_RESULTS_DIR, PROXY_POOL_DIR]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Proxy Pool copy completed successfully.")
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Proxy Pool copy error: {e.stderr}", file=sys.stderr)
    except FileNotFoundError as e:
        print(f"❌ Command not found: {command[0]}. Check your PATH.", file=sys.stderr)