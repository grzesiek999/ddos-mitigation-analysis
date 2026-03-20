#!/bin/bash
set -e

sysctl -w net.ipv4.icmp_ratelimit=1000
sysctl -w net.ipv4.icmp_ratemask=6168

# Delete iptables rules if exist
iptables -D INPUT -p icmp --icmp-type echo-request -m limit --limit 50/second --limit-burst 100 -j ACCEPT 2>/dev/null || true
iptables -D INPUT -p icmp --icmp-type echo-request -j DROP 2>/dev/null || true

echo off > /etc/l3-mitigation/active_profile
echo "L3 profile: off"
