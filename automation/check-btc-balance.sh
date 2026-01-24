#!/bin/bash
set -euo pipefail

# Read-only Bitcoin balance checker for multiple addresses
# Usage: ./automation/check-btc-balance.sh addresses.txt
# where addresses.txt contains one Bitcoin address per line.

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <addresses-file>"
  exit 1
fi

ADDR_FILE="$1"
if [ ! -f "$ADDR_FILE" ]; then
  echo "Addresses file not found: $ADDR_FILE"
  exit 2
fi

# Ensure dependencies
command -v curl >/dev/null 2>&1 || { echo "curl required but not found"; exit 3; }
command -v jq >/dev/null 2>&1 || { echo "jq required but not found. On Debian/Ubuntu: sudo apt-get install -y jq"; exit 3; }

OUT_DIR="reports/btc_balances"
mkdir -p "$OUT_DIR"

echo "Checking balances for addresses from $ADDR_FILE"
TS=$(date -u +"%Y%m%dT%H%M%SZ")
OUT_FILE="$OUT_DIR/balances_$TS.json"

echo "{" > "$OUT_FILE"
FIRST=true
while IFS= read -r ADDR || [ -n "$ADDR" ]; do
  ADDR=$(echo "$ADDR" | tr -d '\r\n' | xargs)
  [ -z "$ADDR" ] && continue

  # Skip obvious invalid lines
  if [[ ${#ADDR} -lt 26 || ${#ADDR} -gt 90 ]]; then
    echo "Skipping invalid-looking address: $ADDR" >&2
    continue
  fi

  echo "Checking: $ADDR"

  # Prepare JSON entry
  if [ "$FIRST" = true ]; then
    FIRST=false
  else
    echo "," >> "$OUT_FILE"
  fi

  echo "  \"$ADDR\": {" >> "$OUT_FILE"

  # 1) Blockstream API
  bs_raw=$(curl -sS "https://blockstream.info/api/address/$ADDR") || bs_raw=""
  if echo "$bs_raw" | jq -e . >/dev/null 2>&1; then
    funded=$(echo "$bs_raw" | jq -r '.chain_stats.funded_txo_sum // 0')
    spent=$(echo "$bs_raw" | jq -r '.chain_stats.spent_txo_sum // 0')
    bal=$((funded - spent))
    echo "    \"blockstream_sats\": $bal," >> "$OUT_FILE"
  else
    echo "    \"blockstream_sats\": null," >> "$OUT_FILE"
  fi

  # 2) blockchain.info
  b1=$(curl -sS "https://blockchain.info/q/addressbalance/$ADDR" || echo "")
  if [[ "$b1" =~ ^[0-9]+$ ]]; then
    echo "    \"blockchain_info_sats\": $b1," >> "$OUT_FILE"
  else
    echo "    \"blockchain_info_sats\": null," >> "$OUT_FILE"
  fi

  # 3) Blockchair
  bc_raw=$(curl -sS "https://api.blockchair.com/bitcoin/dashboards/address/$ADDR" || echo "")
  if echo "$bc_raw" | jq -e . >/dev/null 2>&1; then
    bc_bal=$(echo "$bc_raw" | jq -r ".data.\"$ADDR\".address.balance // null")
    if [ "$bc_bal" = "null" ] || [ -z "$bc_bal" ]; then
      echo "    \"blockchair_sats\": null" >> "$OUT_FILE"
    else
      echo "    \"blockchair_sats\": $bc_bal" >> "$OUT_FILE"
    fi
  else
    echo "    \"blockchair_sats\": null" >> "$OUT_FILE"
  fi

  echo "  }" >> "$OUT_FILE"

done < "$ADDR_FILE"

echo "}" >> "$OUT_FILE"

echo "Balances written to $OUT_FILE"

echo "SUMMARY (human-readable):"
cat "$OUT_FILE" | jq -r 'to_entries | .[] | "Address: " + .key + "\n  blockstream_sats: " + (if .value.blockstream_sats == null then "null" else (.value.blockstream_sats|tostring) end) + "\n  blockchain_info_sats: " + (if .value.blockchain_info_sats == null then "null" else (.value.blockchain_info_sats|tostring) end) + "\n  blockchair_sats: " + (if .value.blockchair_sats == null then "null" else (.value.blockchair_sats|tostring) end) + "\n"'

# Reminder
echo "\nNote: This script queries public explorers. It is read-only and does NOT require private keys. If you intend to scan many addresses repeatedly, be mindful of API rate limits."
