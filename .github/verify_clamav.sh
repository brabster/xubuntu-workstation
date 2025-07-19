#!/usr/bin/env bash

set -euo pipefail

# --- Configuration (CI Environment) ---
TARGET_USER="tester"
DOWNLOADS_DIR="/home/${TARGET_USER}/Downloads"
QUARANTINE_DIR="${DOWNLOADS_DIR}/.quarantine"

EICAR_STRING='X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
EICAR_TEST_FILE="eicar_test_file.txt"
EICAR_DEST_PATH="${DOWNLOADS_DIR}/${EICAR_TEST_FILE}"
QUARANTINED_FILE_PATH="${QUARANTINE_DIR}/${EICAR_TEST_FILE}"

POLL_TIMEOUT_SECONDS=15
POLL_INTERVAL_SECONDS=1

# --- Functions ---
log() {
  echo "[*] $1" >&2
}

# --- Main Script ---

# Define a cleanup function to run on exit
cleanup() {
  log "Cleaning up..."
  # Use runuser to clean up files owned by the target user
  runuser -l "${TARGET_USER}" -c "rm -f '${EICAR_DEST_PATH}' '${QUARANTINED_FILE_PATH}'" &>/dev/null || true
}
trap cleanup EXIT

log "Creating EICAR test file directly in ${EICAR_DEST_PATH} as user ${TARGET_USER} to trigger scan..."
runuser -l "${TARGET_USER}" -c "echo '${EICAR_STRING}' > '${EICAR_DEST_PATH}'"

log "Polling for quarantined file at ${QUARANTINED_FILE_PATH} (timeout: ${POLL_TIMEOUT_SECONDS}s)..."
SECONDS=0
while [[ $SECONDS -lt $POLL_TIMEOUT_SECONDS ]]; do
  if runuser -l "${TARGET_USER}" -c "test -f '${QUARANTINED_FILE_PATH}'"; then
    log "SUCCESS: EICAR file was successfully quarantined after ${SECONDS} seconds."
    if runuser -l "${TARGET_USER}" -c "test ! -f '${EICAR_DEST_PATH}'"; then
        log "SUCCESS: Original file was correctly removed from Downloads."
        exit 0
    else
        log "ERROR: Quarantined file exists, but original file was NOT removed."
        exit 1
    fi
  fi
  sleep "${POLL_INTERVAL_SECONDS}"
done

log "ERROR: Timed out waiting for EICAR file to be quarantined."
log "Dumping ClamAV logs for debugging..."
tail -n 50 /var/log/clamav/clamav.log || true
tail -n 50 /var/log/clamav/clamonacc.log || true
exit 1