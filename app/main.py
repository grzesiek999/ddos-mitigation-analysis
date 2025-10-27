from ddos_attacks.attacks.l7_attack import L7Attack
import asyncio

if __name__ == "__main__":
    l7_attack = L7Attack()
    asyncio.run(l7_attack.attack())
    l7_attack.attack_statistic()