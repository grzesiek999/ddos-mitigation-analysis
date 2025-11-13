import asyncio, time
from ddos_attacks.attacks.l7_attack import L7Attack
from stats.analyze import best_params


# Test n attack series
def attack_series(n: int = 10):
    def temp(bc: list, rps: list, proxy: bool):
        '''for b, r in zip(bc, rps):
            if proxy:
                l7_attack = L7Attack(bots_count=b, rps=r, proxy=proxy)
            else:
                l7_attack = L7Attack(bots_count=b, rps=r)
            for i in range(n):
                asyncio.run(l7_attack.attack())
                time.sleep(10)'''
        best_params(proxy_flag=proxy)

    bot_count = [250, 500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000]
    requests_per_second = [ x*5 for x in bot_count ]
    temp(bot_count, requests_per_second, True)
    temp(bot_count, requests_per_second, False)