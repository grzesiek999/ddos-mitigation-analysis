import statistics
from pathlib import Path
from utils.utils import save_jsonl, load_jsonl

L4SYN_ATTACK_LOGS = Path(__file__).resolve().parents[2] / "logs/l4syn_attack.jsonl"
BEST_THRDS_NUM_RESULTS = Path(__file__).resolve().parents[0] / "results/l4/best_thrds_num.jsonl"

def search_best_thrds_num():
    logs = load_jsonl(L4SYN_ATTACK_LOGS)
    data = {}
    threads_arr = []

    for log in logs:
        data_key = list(log.keys())[0]
        params = log[data_key]["---PARAMS---"]
        stats = log[data_key]["---STATS---"]
        thrds_num = params["Threads number"]
        if thrds_num not in data:
            threads_arr.append(thrds_num)
            data[thrds_num] = {}
            data[thrds_num]['Packet Sent'] = []
            data[thrds_num]['Pps'] = []
            data[thrds_num]['Errors'] = []
            if stats['Packets Sent'] >= 100_000:
                data[thrds_num]['Packet Sent'].append(stats['Packets Sent'])
                data[thrds_num]['Pps'].append(stats['Pps'])
                data[thrds_num]['Errors'].append(stats['Errors'])
        else:
            if stats['Packets Sent'] >= 100_000:
                data[thrds_num]['Packet Sent'].append(stats['Packets Sent'])
                data[thrds_num]['Pps'].append(stats['Pps'])
                data[thrds_num]['Errors'].append(stats['Errors'])

    ps_avg = []
    pps_avg = []
    errors_avg = []
    for thread in threads_arr:
        ps_avg.append(statistics.mean(data[thread]['Packet Sent']))
        pps_avg.append(statistics.mean(data[thread]['Pps']))
        errors_avg.append(statistics.mean(data[thread]['Errors']))

    idx = ps_avg.index(max(ps_avg))
    results = {
        "Threads number": threads_arr[idx],
        "Packets Sent": round(ps_avg[idx]),
        "Pps": round(pps_avg[idx], 2),
        "Errors": round(errors_avg[idx], 1),
    }
    save_jsonl(filename=BEST_THRDS_NUM_RESULTS, data=results, show=True)