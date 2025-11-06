import asyncio
from pathlib import Path
from utils.proxy_select_app.app.utils import read_json, write_json, select_data

DATA_PATH = Path(__file__).resolve().parents[1] / "data/data.json"
RESULTS_PATH = Path(__file__).resolve().parents[1] / "results/results.json"


if __name__ == '__main__':
    json_data = read_json(DATA_PATH)
    write_json(RESULTS_PATH, asyncio.run(select_data(json_data)))
