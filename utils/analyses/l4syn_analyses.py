import statistics
from pathlib import Path
from utils.utils import save_jsonl, load_jsonl

L4SYN_ATTACK_LOGS = Path(__file__).resolve().parents[2] / "logs/l4syn_attack.jsonl"
BEST_THRDS_NUM_RESULTS = Path(__file__).resolve().parents[0] / "results/l4syn/best_thrds_num.jsonl"

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
            create_data_tables(data=data, thrds_num=thrds_num)
            if stats['Packets Sent'] >= 100_000:
                fill_data_tables(data_dict=data[thrds_num], stats=stats)
        else:
            if stats['Packets Sent'] >= 100_000:
                fill_data_tables(data_dict=data[thrds_num], stats=stats)

    ps_avg = []
    pps_avg = []
    errors_avg = []
    for thread in threads_arr:
        fill_avg_arrays(ps_avg, pps_avg, errors_avg, data, thread)

    idx = ps_avg.index(max(ps_avg))
    results = {
        "Threads number": threads_arr[idx],
        "Packets Sent": round(ps_avg[idx]),
        "Pps": round(pps_avg[idx], 1),
        "Errors": round(errors_avg[idx], 1),
    }
    save_jsonl(filename=BEST_THRDS_NUM_RESULTS, data=results, show=True)

def fill_avg_arrays(ps_avg: list, pps_avg: list, errors_avg: list, data: dict, thread: int):
    ps_avg.append(statistics.mean(data[thread]["Packets Sent"]))
    pps_avg.append(statistics.mean(data[thread]["Pps"]))
    errors_avg.append(statistics.mean(data[thread]["Errors"]))

def fill_data_tables(data_dict: dict, stats: dict):
    data_dict["Packets Sent"].append(stats["Packets Sent"])
    data_dict["Pps"].append(stats["Pps"])
    data_dict["Errors"].append(stats["Errors"])

def create_data_tables(data: dict, thrds_num: int):
    data[thrds_num] = {}
    data[thrds_num]["Packets Sent"] = []
    data[thrds_num]["Pps"] = []
    data[thrds_num]["Errors"] = []