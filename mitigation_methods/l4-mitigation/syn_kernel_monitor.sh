#!/bin/bash

OUTFILE="syn_cookie_results.csv"

get_syncookies() {
    awk '
    $1=="TcpExt:" && !header_seen {
        for (i=1; i<=NF; i++) {
            if ($i=="SyncookiesSent") {
                col=i
                header_seen=1
                next
            }
        }
    }
    $1=="TcpExt:" && header_seen {
        print $col
        exit
    }' /proc/net/netstat
}

echo "Starting SYN cookie monitor..."
echo ""

BEFORE=$(get_syncookies)

echo "SyncookiesSent BEFORE attack: $BEFORE"
echo ""
echo "Uruchom teraz atak SYN i naciśnij ENTER po zakończeniu..."
read

AFTER=$(get_syncookies)

DELTA=$((AFTER - BEFORE))

echo ""
echo "SyncookiesSent AFTER attack: $AFTER"
echo "SyncookiesSent DELTA: $DELTA"
echo ""

DATE=$(date "+%Y-%m-%d %H:%M:%S")
echo "$DATE,$BEFORE,$AFTER,$DELTA" >> "$OUTFILE"

echo "Saved result to $OUTFILE"