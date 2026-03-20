#!/bin/bash
set -e

# Return base TCP rules
sysctl -w net.ipv4.tcp_syncookies=0
sysctl -w net.ipv4.tcp_max_syn_backlog=256
sysctl -w net.core.somaxconn=512
sysctl -w net.ipv4.tcp_synack_retries=5

# Delete old UDP rules if exist
iptables -D INPUT -p udp --dport 9999 -m limit --limit 50/second --limit-burst 100 -j ACCEPT 2>/dev/null || true
iptables -D INPUT -p udp --dport 9999 -j DROP 2>/dev/null || true
iptables -D INPUT -p udp --dport 9999 -j ACCEPT 2>/dev/null || true

# add new rules
iptables -I INPUT 1 -p udp --dport 9999 -m limit --limit 50/second --limit-burst 100 -j ACCEPT
iptables -I INPUT 2 -p udp --dport 9999 -j DROP

echo udp > /etc/l4-mitigation/active_profile
echo "L4 profile: udp"