from tests import l7_tests, l4_tests


def main():
    # l7_tests.attack(proxy=True)
    # l7_tests.attack_series(n=20)
    # l4_tests.search_ip()
    # l4_tests.attack()
    l4_tests.attack_series(n=20)

if __name__ == "__main__":
    main()