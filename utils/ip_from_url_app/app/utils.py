import json, socket
from typing import Dict
from urllib.parse import urlparse
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data/data.json"
RESULTS_DIR = Path(__file__).resolve().parents[1] / "results/results.json"


def get_target_ip(urls: list[str]) -> Dict | None:
    if len(urls) == 0:
        return None

    parsed_urls = [urlparse(url) for url in urls]
    hostnames = [parsed_urls[i].netloc for i in range(len(parsed_urls))]

    results = {}
    for hostname, url in zip(hostnames, urls):
        if not hostname:
            raise ValueError(f"Cannot catch host name from: {url}")
        try:
            ip = socket.gethostbyname(hostname)
            results[url] = ip
        except socket.gaierror as e:
            raise ConnectionError(f"Cannot find IP address for host {hostname}: {e}")

    return results

def save_results(data: dict):
    with open(RESULTS_DIR, "w") as file:
        json.dump(data, file, indent=4)

def read_data() -> list:
    with open(DATA_DIR) as file:
        data = json.load(file)
        file.close()
        return data["URLS"]