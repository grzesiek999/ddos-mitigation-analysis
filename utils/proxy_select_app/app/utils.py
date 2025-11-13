import json, aiohttp, asyncio, time
from pathlib import Path
from ddos.utils import load_json

def read_json(filename):
    with open(filename, mode="r") as file:
        return json.load(file)

def write_json(filename, data):
    with open(filename, mode="w") as file:
        json.dump(data, file, indent=4)

async def calculate_ping(proxy_url, proxy_port):
    ddos_config = load_json(Path(__file__).resolve().parents[3] / "config/l7ddos.json" )
    url = ddos_config["l7"]["TARGET"]
    proxy = f"http://{proxy_url}:{proxy_port}"
    proxies_fallback = [
        f"http://{proxy_url}:80",
        f"http://{proxy_url}:8888",
        f"http://{proxy_url}:8080",
        f"http://{proxy_url}:3128"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    timeout = aiohttp.ClientTimeout(total=10)
    connector = aiohttp.TCPConnector(limit=1)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        start = time.time()
        try:
            async with session.get(url, proxy=proxy, headers=headers) as response:
                await response.text()
                return int((time.time() - start)*1000)
        except Exception as e:
            start = time.time()
            for proxy_fallback in proxies_fallback:
                try:
                    async with session.get(url, proxy=proxy_fallback, headers=headers) as def_response:
                        await def_response.text()
                        return int((time.time() - start) * 1000)
                except Exception as err:
                    print(f"Error: {err}")
                    continue
            return float("inf")

async def select_data(data):
    results = {
        "proxies": [
        ]
    }
    tasks = []

    for proxy in data["PROXIES"]:
        proxy_url = proxy['IP']
        proxy_port = int(proxy['PORT'])
        tasks.append(calculate_ping(proxy_url, proxy_port))

    pings = await asyncio.gather(*tasks, return_exceptions=True)

    for proxy, ping in zip(data["PROXIES"], pings):
        if ping <= 300:
            results["proxies"].append({
                "ip": proxy["IP"],
                "port": proxy["PORT"],
                "ping": int(ping)
            })

    results["proxies"].sort(key=lambda x: x["ping"])
    return results