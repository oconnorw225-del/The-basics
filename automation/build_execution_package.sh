#!/usr/bin/env bash
set -euo pipefail

OUTDIR="${1:-workspace/execution}"
mkdir -p "$OUTDIR"

# Masked manifest location candidates
MANIFESTS=("workspace/artifacts/consolidated_manifest.json" "workspace/artifacts/consolidated-manifest.json" "workspace/artifacts/consolidated_manifest" "artifacts/consolidated_manifest.json")
for m in "${MANIFESTS[@]}"; do
  if [ -f "$m" ]; then
    jq 'del(.secrets) // .' "$m" > "$OUTDIR/manifest.json" 2>/dev/null || cp "$m" "$OUTDIR/manifest.json"
    break
  fi
done

# copy scan results and backups if available (but do not copy any secret files)
mkdir -p "$OUTDIR/scan_results" "$OUTDIR/backups" "$OUTDIR/test_results"
[ -d "workspace/scan_results" ] && cp -r --no-preserve=mode,ownership workspace/scan_results/* "$OUTDIR/scan_results/" 2>/dev/null || true
[ -d "workspace/backups" ] && cp -r --no-preserve=mode,ownership workspace/backups/* "$OUTDIR/backups/" 2>/dev/null || true
[ -f "data/test_results.json" ] && cp data/test_results.json "$OUTDIR/test_results/test_results.json" 2>/dev/null || true

# Add a placeholder unsigned tx info file that instructs operators to create PSBT offline
cat > "$OUTDIR/unsigned_tx_info.txt" <<'TXT'
This execution package is for manual review and signing only.
DO NOT BROADCAST ANY TRANSACTIONS AUTOMATICALLY.

To execute a transfer you MUST:
1) Review manifest.json and test_results.json.
2) Generate an unsigned PSBT (or raw tx) offline on a secure, air-gapped or hardware wallet machine.
3) Sign the PSBT using your hardware wallet or multi-sig process.
4) Verify the signed transaction and broadcast manually from a secure host.

The CI DOES NOT create or sign transactions. This file is a placeholder with instructions only.
TXT

# Create the execution package zip
cd "$(dirname "$OUTDIR")" || true
zip -r "${OUTDIR%/*}/execution_package.zip" "$(basename "$OUTDIR")" >/dev/null 2>&1 || true

echo "Execution package created: ${OUTDIR%/*}/execution_package.zip"
