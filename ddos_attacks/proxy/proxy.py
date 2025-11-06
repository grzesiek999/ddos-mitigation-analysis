import time, asyncio, random
from typing import List, Dict, Optional
from itertools import cycle


class Proxy:
    def __init__(self, ip: str, port: int, ping: int):
        self.ip = ip
        self.port = port
        self.ping = ping
        self.url = f"http://{ip}:{port}"
        self.semaphore = asyncio.Semaphore(5)
        self.failed_count = 0
        self.last_success = 0.0
        self.dead_until = 0.0

    def mark_success(self):
        self.failed_count = 0
        self.last_success = time.time()
        self.dead_until = 0

    def mark_failure(self):
        self.failed_count += 1
        if self.failed_count > 3:
            self.dead_until = time.time() + 30

class ProxyPool:
    def __init__(self, proxies: List[Dict], mode: str = "roundrobin"):
        self.proxies = [Proxy(p["ip"], p["port"], p["ping"]) for p in proxies]
        self.mode = mode
        self._rr = cycle(range(len(self.proxies))) if self.proxies else cycle([])
        self._lock = asyncio.Lock()

    async def get_proxy(self) -> Optional[Proxy]:
        now = time.time()
        alive = [p for p in self.proxies if p.dead_until < now]
        if not alive:
            return None
        if self.mode == "roundrobin":
            async with self._lock:
                for _ in range(len(self.proxies)):
                    idx = next(self._rr)
                    p = self.proxies[idx]
                    if p.dead_until < now:
                        return p
            return random.choice(self.proxies)
        elif self.mode == "random":
            return random.choice(alive)
        elif self.mode == "weighted":
            weights = [p["ping"] for p in alive]
            return random.choices(alive, weights=weights, k=1)[0] # ??
        else:
            return random.choice(alive)

    async def acquire(self, timeout: Optional[float] = None) -> Optional[Proxy]:
        start = time.time()
        while True:
            p = await self.get_proxy()
            if p is None:
                return None
            try:
                await asyncio.wait_for(p.semaphore.acquire(), timeout=0.1)
                return p
            except asyncio.TimeoutError:
                if timeout and (time.time() -  start) > timeout:
                    return None
                await asyncio.sleep(0)
                continue

    def release(self, p: Proxy):
        try:
            p.semaphore.release()
        except Exception:
            pass

    def report_success(self, p: Proxy):
        p.mark_success()

    def report_failure(self, p: Proxy):
        p.mark_failure()