import statistics
from pathlib import Path
from ddos.utils import load_jsonl
from utils.analyses.utils import save_jsonl

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
        if log[date_key]['---PARAMS---']['Bot Count'] not in data:
            bot_count_arr.append(bc)
            rps_arr.append(rps)
            data[bc] = {}
            data[bc]['Requests'] = []
            data[bc]['Errors'] = []
            if stats['Requests'] >= 10000:
                data[bc]['Requests'].append(stats['Requests'])
                data[bc]['Errors'].append(stats['Errors'])
        else:
            if stats['Requests'] >= 10000:
                data[bc]['Requests'].append(stats['Requests'])
                data[bc]['Errors'].append(stats['Errors'])

    req_avg = []
    err_avg = []
    for item in bot_count_arr:
        req_avg.append(statistics.mean(data[item]['Requests']))
        err_avg.append(statistics.mean(data[item]['Errors']))

    max_val = max(req_avg)
    for i in range(len(req_avg)):
        if max_val - req_avg[i] > 1000:
            req_avg[i] = 0

    score = []
    for i in range(len(bot_count_arr)):
        score.append(req_avg[i] / err_avg[i])

    idx = score.index(max(score))
    results = {
        "Proxy": proxy_flag,
        "Bots count": bot_count_arr[idx],
        "Rps": rps_arr[idx],
        "Score": round(score[idx], 2)
    }
    save_jsonl(filename=BEST_PARAMS_RESULTS, data=results, show=True)