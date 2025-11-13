import statistics
from pathlib import Path
from ddos_attacks.utils import load_jsonl

L7_ATTACK_LOGS = Path(__file__).resolve().parents[1] / "logs/l7attack.jsonl"
BEST_PARAMS_RESULTS = Path(__file__).resolve().parents[0] / "results/best_params.txt"


# Analyze statistics l7 attack from logs in search best params
def best_params(proxy_flag: bool):
    logs = load_jsonl(L7_ATTACK_LOGS)
    data = {}
    temp = []

    for log in logs:
        date_key = list(log.keys())[0]
        params = log[date_key]['---PARAMS---']
        if params['Proxy'] != proxy_flag:
            continue
        stats = log[date_key]['---STATS---']
        bc = params['Bot Count']
        if log[date_key]['---PARAMS---']['Bot Count'] not in data:
            temp.append(bc)
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

    for item in temp:
        req_avg.append(statistics.mean(data[item]['Requests']))
        err_avg.append(statistics.mean(data[item]['Errors']))

    max_val = max(req_avg)

    for i in range(len(req_avg)):
        if max_val - req_avg[i] > 1000:
            req_avg[i] = 0

    score = []

    for i in range(len(temp)):
        score.append(req_avg[i] / err_avg[i])

    idx = score.index(max(score))

    results = f"Proxy: {proxy_flag}   Bots count: {temp[idx]}   Rps: {temp[idx]*5}   Score: {round(score[idx], 2)}\n"
    with open(BEST_PARAMS_RESULTS, "a", encoding="utf-8") as file:
        file.write(results)
        file.close()
    print(results)