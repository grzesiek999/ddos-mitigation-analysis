from tests import l7_tests, l4syn_tests, l4udp_tests


def main():
    #l7_tests.attack(proxy=True)
    #l7_tests.attack_series(n=20)
    #l4syn_tests.search_ip()
    #l4syn_tests.attack()
    #l4syn_tests.attack_series(n=20)
    #l4udp_tests.attack()
    l4udp_tests.attack_series(2)

if __name__ == "__main__":
    main()