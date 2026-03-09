#!/bin/bash
set -e

sysctl -w net.ipv4.icmp_ratelimit=100
sysctl -w net.ipv4.icmp_ratemask=88089

iptables -D INPUT -p icmp --icmp-type echo-request -j L3_ICMP_MITIGATION 2>/dev/null || true
iptables -F L3_ICMP_MITIGATION 2>/dev/null || true
iptables -X L3_ICMP_MITIGATION 2>/dev/null || true

iptables -N L3_ICMP_MITIGATION
iptables -A L3_ICMP_MITIGATION -m limit --limit 50/second -j ACCEPT
iptables -A L3_ICMP_MITIGATION -j DROP
iptables -A INPUT -p icmp --icmp-type echo-request -j L3_ICMP_MITIGATION

echo both > /etc/l3-mitigation/active_profile
echo "L3 profile: both"
