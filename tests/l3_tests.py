import time
from ddos.attacks.l3_attack import L3Attack
from utils.analyses.l3_analyses import search_best_thrds_num


# Test n attack series for search best params
def attack_series(n: int = 10):
    l3_attack = L3Attack()
    threads = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
    for thread_num in threads:
        for i in range(n):
            l3_attack.attack(num_threads=thread_num)
            time.sleep(10)
    search_best_thrds_num()

# Test single attack
def attack():
    l3_attack = L3Attack()
    l3_attack.attack(num_threads=4)