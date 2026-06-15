from utils.ip_from_url_app.app.utils import get_target_ip, save_results, read_data


def main():
    ulrs_arr = read_data()
    results = get_target_ip(urls=ulrs_arr)
    save_results(data=results)

if __name__ == "__main__":
    main()