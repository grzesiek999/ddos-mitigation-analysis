from tests import l7_tests, l4syn_tests, l4udp_tests, l3_tests
import time

def main():
    '''L4 tcp.sh'''
    l4syn_tests.attack_series(n=2)
    time.sleep(600)
    '''L4 udp.sh'''
    l4udp_tests.attack_series(n=2)
    #time.sleep(1200)
    '''l7 Rate limiting'''
    #l7_tests.attack_series(n=20)
    #time.sleep(1200)
    '''l7 Connection limiting'''
    #l7_tests.attack_series(n=20)


if __name__ == "__main__":
    main()