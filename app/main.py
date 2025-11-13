from tests import l7_tests, l4_tests


def main():
    # l7_tests.attack(proxy=True)
    # l4_tests.search_ip()
    l4_tests.attack()

if __name__ == "__main__":
    main()