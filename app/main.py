from tests import l7_tests, l4syn_tests, l4udp_tests, l3_tests
from utils.analyses.l7_stats import run_l7_stats

def main():
    #l7_tests.attack(proxy=False)
    #l4syn_tests.search_ip()
    #l4syn_tests.attack()
    #l4syn_tests.attack_series(n=20)
    #l4udp_tests.attack()
    #l4udp_tests.attack_series(n=20)
    #l3_tests.attack()
    #l3_tests.attack_series(n=20)
    #l7_tests.attack_series(n=20)
    #run_analysis()
    run_l7_stats(proxy=False)

if __name__ == "__main__":
    main()