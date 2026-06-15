import statistics
from pathlib import Path
from utils.utils import save_jsonl, load_jsonl

L7_ATTACK_LOGS = Path(__file__).resolve().parents[2] / "logs/l7attack.jsonl"
BEST_PARAMS_RESULTS = Path(__file__).resolve().parents[0] / "results/l7/best_params.jsonl"


# Analyze statistics l7 attack from logs in search best params
def search_best_params(proxy_flag: bool):
    logs = load_jsonl(L7_ATTACK_LOGS)
    data = {}
    bot_count_arr = []
    rps_arr = []

    for log in logs:
        date_key = list(log.keys())[0]
        params = log[date_key]['---PARAMS---']
        if params['Proxy'] != proxy_flag:
            continue
        stats = log[date_key]['---STATS---']
        bc = params['Bot Count']
        rps = params['Rps']
        if bc not in data:
            bot_count_arr.append(bc)
            rps_arr.append(rps)
            create_data_tables(data=data, bc=bc)
            if stats['Requests'] >= 10_000:
                fill_data_tables(data_dict=data[bc], stats=stats)
        else:
            if stats['Requests'] >= 10_000:
                fill_data_tables(data_dict=data[bc], stats=stats)

    req_avg = []
    errors_avg = []
    p50_avg = []
    p95_avg = []
    p99_avg = []
    for bc in bot_count_arr:
        fill_avg_arrays(req_avg, errors_avg, p50_avg, p95_avg, p99_avg, data, bc)

    score = []
    calculate_score(score, req_avg, bot_count_arr, errors_avg)
    idx = score.index(max(score))
    results = {
        "Proxy": proxy_flag,
        "Bots count": bot_count_arr[idx],
        "Rps": rps_arr[idx],
        "Score": round(score[idx], 2)
    }
    save_jsonl(filename=BEST_PARAMS_RESULTS, data=results, show=True)

def calculate_score(score: list, req_avg, bot_count_arr, errors_avg):
    max_val = max(req_avg)
    for i in range(len(req_avg)):
        if max_val - req_avg[i] > 1000:
            req_avg[i] = 0
    for i in range(len(bot_count_arr)):
        if errors_avg[i] > 0:
            score.append(req_avg[i] / errors_avg[i])
        elif errors_avg[i] == 0:
            score.append(req_avg[i] / 1)
        else:
            raise Exception("AVG < 0, something went wrong")

def fill_avg_arrays(req_avg, errors_avg, p50_avg, p95_avg, p99_avg, data:dict, bc: int):
    req_avg.append(statistics.mean(data[bc]["Requests"]))
    errors_avg.append(statistics.mean(data[bc]["Errors"]))
    p50_avg.append(statistics.mean(data[bc]["p50"]))
    p95_avg.append(statistics.mean(data[bc]["p95"]))
    p99_avg.append(statistics.mean(data[bc]["p99"]))

def fill_data_tables(data_dict: dict, stats: dict):
    data_dict["Requests"].append(stats["Requests"])
    data_dict["Errors"].append(stats["Errors"])
    data_dict['p50'].append(stats["p50"])
    data_dict['p95'].append(stats["p95"])
    data_dict['p99'].append(stats["p99"])

def create_data_tables(data: dict, bc: int):
    data[bc] = {}
    data[bc]['Requests'] = []
    data[bc]['Errors'] = []
    data[bc]['p50'] = []
    data[bc]['p95'] = []
    data[bc]['p99'] = []