from ddos_attacks.attacks.l7_attack import L7Attack
import asyncio

def test():
    l7_attack = L7Attack(bots_count=1200, rps=6000)
    asyncio.run(l7_attack.attack())