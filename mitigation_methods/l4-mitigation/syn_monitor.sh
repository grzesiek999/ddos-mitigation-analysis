#!/bin/bash

DURATION=65
END=$((SECONDS+DURATION))

echo "time,syn_recv" > syn_monitor.csv

while [ $SECONDS -lt $END ]; do
    SYN=$(ss -H -ant state syn-recv | wc -l)
    echo "$(date +%s),$SYN" >> syn_monitor.csv
    sleep 1
done