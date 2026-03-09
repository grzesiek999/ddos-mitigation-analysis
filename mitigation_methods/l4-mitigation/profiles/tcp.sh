#!/bin/bash
set -e

# Turn on TCP/SYN
sysctl -w net.ipv4.tcp_syncookies=1
sysctl -w net.ipv4.tcp_max_syn_backlog=4096
sysctl -w net.core.somaxconn=4096
sysctl -w net.ipv4.tcp_synack_retries=3

# Delete UDP mitigation rules, if exist
iptables -D INPUT -p udp -j L4_UDP_MITIGATION 2>/dev/null || true
iptables -F L4_UDP_MITIGATION 2>/dev/null || true
iptables -X L4_UDP_MITIGATION 2>/dev/null || true

echo tcp > /etc/l4-mitigation/active_profile
