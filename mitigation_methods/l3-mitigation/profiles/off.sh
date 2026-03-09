#!/bin/bash
set -e

sysctl -w net.ipv4.icmp_ratelimit=1000
sysctl -w net.ipv4.icmp_ratemask=6168

iptables -D INPUT -p icmp --icmp-type echo-request -j L3_ICMP_MITIGATION 2>/dev/null || true
iptables -F L3_ICMP_MITIGATION 2>/dev/null || true
iptables -X L3_ICMP_MITIGATION 2>/dev/null || true

echo off > /etc/l3-mitigation/active_profile
echo "L3 profile: off"
