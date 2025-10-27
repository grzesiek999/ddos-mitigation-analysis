import random
import statistics
import math
import json
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"

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
def load_config(filename):
    path = CONFIG_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Config file {filename} not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))