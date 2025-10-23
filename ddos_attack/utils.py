import random
import time
import asyncio
import statistics
import math

TARGET = "http://YOUR.VPS.IP.OR.DOMAIN"
ENDPOINTS = ["/", "/api/items?page=1", "/health"]
USER_AGENTS = ["Mozilla/5.0", "curl/7.68.0", "CustomTestBot/1.0"]


async def bot(name, session, limiter, stats, stop_time):
    while time.time() < stop_time:
        await limiter.acquire()
        endpoint = random_choice(ENDPOINTS)
        headers = {"User-Agent": random_choice(USER_AGENTS)}
        start = time.time()
        try:
            async with session.get(TARGET + endpoint, headers=headers, timeout=10) as resp:
                text = await resp.text()  # krótkie użycie odpowiedzi
                latency = (time.time() - start) * 1000.0
                stats['response_times'].append(latency)
                stats['http_codes'].append(resp.status)
        except Exception as e:
            stats['errors_count'] += 1
        await asyncio.sleep(0)

# Return random choice from list
def random_choice(array):
    return random.choice(array)

# Statistic of bot
def bot_statistic(stats):
    print("Requests:", len(stats['response_times']))
    print("Errors:", stats['errors_count'])
    print("p50:", statistics.median(stats['response_times']))
    print("p95:", percentile(stats['response_times'], 95))
    print("p99:", percentile(stats['response_times'], 99))

# Calculate percentile
def percentile(data, p):
    data = sorted(data)
    if not data:
        return None
    k = (len(data)-1) * (p/100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return data[int(k)]
    d0 = data[int(f)] * (c-k)
    d1 = data[int(c)] * (k-f)
    return d0+d1