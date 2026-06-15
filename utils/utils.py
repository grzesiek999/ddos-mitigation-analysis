import math, json, subprocess, sys
from pathlib import Path
from utils.proxy_select_app.run import run_proxy_select_app

PROXY_SELECT_APP = "utils.proxy_select_app.app.main"
PROXIES = Path(__file__).resolve().parents[0] / "proxy_select_app/data/data.json"
PROXY_RESULTS_DIR = Path(__file__).resolve().parents[0] / "proxy_select_app/results/results.json"
PROXY_POOL_DIR = Path(__file__).resolve().parents[1] / "data/proxypool.json"

# Load json file
def load_json(filename):
    path = filename
    if not path.exists():
        raise FileNotFoundError(f"File {filename} not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))

# Save Jsonl file
def save_jsonl(filename, data, show: bool = False):
    with open(filename, "a", encoding='utf-8') as file:
        file.write(json.dumps(data) + '\n')
    if show:
        print(json.dumps(data, indent=4))

# Load Jsonl file
def load_jsonl(filename):
    logs = []
    with open(filename, "r", encoding='utf-8') as file:
        for line in file:
            logs.append(json.loads(line))
    return logs

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

# Select allive proxy and copy to data
def select_allive_proxy():
    run_proxy_select_app(app=PROXY_SELECT_APP, args=[PROXIES, PROXY_RESULTS_DIR])

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