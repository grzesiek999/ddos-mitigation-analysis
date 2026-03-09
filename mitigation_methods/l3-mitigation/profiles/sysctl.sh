#!/bin/bash
set -e

sysctl -w net.ipv4.icmp_ratelimit=100
sysctl -w net.ipv4.icmp_ratemask=88089

iptables -D INPUT -p icmp --icmp-type echo-request -j L3_ICMP_MITIGATION 2>/dev/null || true
iptables -F L3_ICMP_MITIGATION 2>/dev/null || true
iptables -X L3_ICMP_MITIGATION 2>/dev/null || true

echo sysctl > /etc/l3-mitigation/active_profile
echo "L3 profile: sysctl"
