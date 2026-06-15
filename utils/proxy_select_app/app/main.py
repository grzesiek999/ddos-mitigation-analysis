import asyncio, argparse
from pathlib import Path
from utils.proxy_select_app.app.utils import read_json, write_json, select_data


def main():
    parser = argparse.ArgumentParser(
        description="Application to selects and sorts proxy addresses which are allive."
    )
    parser.add_argument(
        'proxies_base_path',
        type = Path,
        help = "Base path for proxies json file.",
    )
    parser.add_argument(
        'selected_proxies_path',
        type = Path,
        help = "Path to selected proxies json file."
    )
    args = parser.parse_args()
    json_data = read_json(args.proxies_base_path.resolve())
    write_json(args.selected_proxies_path.resolve(), asyncio.run(select_data(json_data)))

if __name__ == '__main__':
    main()