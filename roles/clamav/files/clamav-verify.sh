#!/usr/bin/env bash

set -euo pipefail

# --- Configuration ---
TARGET_USER="$1"
if [ -z "$TARGET_USER" ]; then
    echo "ERROR: Username must be provided as the first argument." >&2
    exit 1
fi

DOWNLOADS_DIR="/home/${TARGET_USER}/Downloads"
QUARANTINE_DIR="/var/lib/clamav/quarantine"

EICAR_STRING='X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
TEST_FILE_NAME=".health-check-$(date +%s).txt"
TEST_FILE_PATH="${DOWNLOADS_DIR}/${TEST_FILE_NAME}"
QUARANTINED_FILE_PATH="${QUARANTINE_DIR}/${TEST_FILE_NAME}"

# --- Main Logic ---
cleanup() {
  runuser -l "${TARGET_USER}" -c "rm -f '${TEST_FILE_PATH}'" &>/dev/null || true
  rm -f "${QUARANTINED_FILE_PATH}" &>/dev/null || true
}
trap cleanup EXIT

runuser -l "${TARGET_USER}" -c "echo '${EICAR_STRING}' > '${TEST_FILE_PATH}'"

POLL_TIMEOUT=15
SECONDS=0
while [ $SECONDS -lt $POLL_TIMEOUT ]; do
  if [ -f "${QUARANTINED_FILE_PATH}" ]; then
      echo "ClamAV on-access scanning is working correctly."
      exit 0
  fi
  sleep 1
done

# --- Failure Path with Diagnostics ---
echo "ERROR: ClamAV on-access test failed. Test file was not quarantined." >&2
echo "" >&2
echo "--- DIAGNOSTICS ---" >&2
echo "--- Running Processes:" >&2
ps aux | grep -E '[c]lamd|[c]lamonacc' || true
echo "" >&2
echo "--- clamd.log (last 30 lines):" >&2
tail -n 30 /var/log/clamav/clamd.log || true
echo "" >&2
echo "--- clamonacc.log (last 30 lines):" >&2
tail -n 30 /var/log/clamav/clamonacc.log || true
echo "-------------------" >&2

exit 1
