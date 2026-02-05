#!/bin/bash
set -euo pipefail

# Security Audit Script (read-only): Runs gitleaks to scan each cloned repository and the current repository
# This script does NOT exfiltrate secrets. It writes reports to ./reports/ and suggests remediation steps.

REPORT_DIR="reports"
mkdir -p "$REPORT_DIR"

# Install gitleaks if not present (Linux runner / local with curl)
if ! command -v gitleaks >/dev/null 2>&1; then
  echo "gitleaks not found. Installing gitleaks..."
  # Install latest gitleaks release (Linux x86_64)
  # NOTE: This downloads a precompiled binary. For production use, consider verifying checksums
  # or using a trusted package manager for supply chain security.
  GL_VERSION="8.16.0"  # set a recent known version; adjust if needed
  curl -sL "https://github.com/zricethezav/gitleaks/releases/download/v${GL_VERSION}/gitleaks_${GL_VERSION}_linux_x64.tar.gz" -o /tmp/gitleaks.tar.gz
  tar -xzf /tmp/gitleaks.tar.gz -C /tmp
  # Ensure local bin directory exists for fallback installation
  mkdir -p "$HOME/.local/bin"
  sudo mv /tmp/gitleaks /usr/local/bin/gitleaks || mv /tmp/gitleaks "$HOME/.local/bin/gitleaks"
  # Ensure $HOME/.local/bin is on PATH so that gitleaks is discoverable
  case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) export PATH="$HOME/.local/bin:$PATH" ;;
  esac
fi

# List of aggregated repos (same as aggregate script). If you changed aggregation, update this list accordingly.
if [ -d "project_aggregation" ]; then
  # When run from repo root, aggregated repositories live under project_aggregation/
  REPO_DIRS=( $(ls -d project_aggregation/*/ 2>/dev/null || true) )
else
  # Fallback: when run from within aggregation dir or a flat layout, use all immediate subdirectories
  REPO_DIRS=( $(ls -d */ 2>/dev/null || true) )
fi

# Always scan the current repository first
echo "Scanning current repo: $(pwd)"
if [ -d .git ]; then
  gitleaks detect --source . --redact --report-path "$REPORT_DIR/current_repo_gitleaks.json" --report-format json || true
fi

# Scan each aggregated directory's git history
SCRIPT_DIR="$(pwd)"
for dir in "${REPO_DIRS[@]}"; do
  if [ -d "$dir/.git" ]; then
    dir_name=$(basename "${dir%/}")
    out="$SCRIPT_DIR/$REPORT_DIR/${dir_name}_gitleaks.json"
    echo "Scanning $dir (history) -> $out"
    (cd "$dir" && gitleaks detect --source . --redact --report-path "$out" --report-format json) || true
  fi
done

# Summarize
echo "Reports generated in $REPORT_DIR"
ls -la "$REPORT_DIR"

echo "IMPORTANT: Do NOT commit report files that contain secrets. Treat findings as sensitive and follow the remediation steps in docs/SECURITY_AUDIT.md"
