from utils.ip_from_url_app.run import run_ip_from_url_app
from ddos.attacks.l4_attack import L4SYNAttack


# Test single attack
def attack():
    l4syn_attack = L4SYNAttack()
    l4syn_attack.attack()

# Test get ip address from url app
def search_ip():
    ip_from_url_app = "utils.ip_from_url_app.app.main"
    run_ip_from_url_app(ip_from_url_app)