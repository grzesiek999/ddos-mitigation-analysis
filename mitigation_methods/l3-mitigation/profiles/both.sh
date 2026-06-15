#!/bin/bash
set -e

sysctl -w net.ipv4.icmp_ratelimit=100
sysctl -w net.ipv4.icmp_ratemask=88089

# delete old rules if exist
iptables -D INPUT -p icmp --icmp-type echo-request -m limit --limit 50/second --limit-burst 100 -j ACCEPT 2>/dev/null || true
iptables -D INPUT -p icmp --icmp-type echo-request -j DROP 2>/dev/null || true

# Add iptables rules
iptables -I INPUT 1 -p icmp --icmp-type echo-request -m limit --limit 50/second --limit-burst 100 -j ACCEPT
iptables -I INPUT 2 -p icmp --icmp-type echo-request -j DROP

echo both > /etc/l3-mitigation/active_profile
echo "L3 profile: both"
