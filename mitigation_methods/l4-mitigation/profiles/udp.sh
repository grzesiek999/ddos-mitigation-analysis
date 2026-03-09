#!/bin/bash
set -e

# Return base TCP rules
sysctl -w net.ipv4.tcp_syncookies=1
sysctl -w net.ipv4.tcp_max_syn_backlog=256
sysctl -w net.core.somaxconn=4096
sysctl -w net.ipv4.tcp_synack_retries=5

# Delete old UDP rules
iptables -D INPUT -p udp -j L4_UDP_MITIGATION 2>/dev/null || true
iptables -F L4_UDP_MITIGATION 2>/dev/null || true
iptables -X L4_UDP_MITIGATION 2>/dev/null || true

# Add UDP mitigation rules
iptables -N L4_UDP_MITIGATION
iptables -A L4_UDP_MITIGATION -m limit --limit 1000/second --limit-burst 2000 -j ACCEPT
iptables -A L4_UDP_MITIGATION -j DROP
iptables -A INPUT -p udp -j L4_UDP_MITIGATION

echo udp > /etc/l4-mitigation/active_profile
