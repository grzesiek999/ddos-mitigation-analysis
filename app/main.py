from tests import l7_tests, l4syn_tests, l4udp_tests, l3_tests
from utils.analyses import l3_l4_stats, l7_stats
import time

def main():
    l3_tests.attack_series(n=20)
    time.sleep(1200)
    l4syn_tests.attack_series(n=20)
    time.sleep(1200)
    l4udp_tests.attack_series(n=20)
    time.sleep(1200)
    l7_tests.attack_series(n=20)

    #l3_l4_stats.run_analysis()
    #l7_stats.run_l7_stats(proxy=True)
    #l7_stats.run_l7_stats(proxy=False)


if __name__ == "__main__":
    main()