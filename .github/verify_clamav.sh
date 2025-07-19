#!/usr/bin/env bash

set -euo pipefail

# --- Configuration ---
EICAR_STRING='X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
# Determine the target user and their home directory
TARGET_USER="${SUDO_USER:-${USER}}"
TARGET_HOME=$(eval echo "~$TARGET_USER")
DOWNLOADS_DIR="${TARGET_HOME}/Downloads"
QUARANTINE_DIR="${DOWNLOADS_DIR}/.quarantine"
EICAR_TEST_FILE="eicar_test_file.txt"
EICAR_SOURCE_PATH="/tmp/${EICAR_TEST_FILE}"
EICAR_DEST_PATH="${DOWNLOADS_DIR}/${EICAR_TEST_FILE}"
QUARANTINED_FILE_PATH="${QUARANTINE_DIR}/${EICAR_TEST_FILE}"
POLL_TIMEOUT_SECONDS=15
POLL_INTERVAL_SECONDS=1

# --- Functions ---

# Log a message to stderr
log() {
  echo "[*] $1" >&2
}

# Clean up created files
cleanup() {
  log "Cleaning up..."
  # In case the script fails before the move
  rm -f "${EICAR_SOURCE_PATH}"
  # In case the quarantine failed
  rm -f "${EICAR_DEST_PATH}"
  # Clean up the quarantined file
  if [[ -f "${QUARANTINED_FILE_PATH}" ]]; then
    log "Removing quarantined test file."
    rm -f "${QUARANTINED_FILE_PATH}"
  fi
}

# --- Main Script ---

# Ensure cleanup runs on script exit
trap cleanup EXIT

log "Creating EICAR test file at ${EICAR_SOURCE_PATH}..."
echo "${EICAR_STRING}" > "${EICAR_SOURCE_PATH}"

# Ensure the target Downloads directory exists
log "Ensuring ${DOWNLOADS_DIR} exists..."
runuser -l "${TARGET_USER}" -c "mkdir -p '${DOWNLOADS_DIR}'"

log "Moving test file to ${EICAR_DEST_PATH} as user ${TARGET_USER} to trigger scan..."
# This command will trigger the OnAccessPrevention scan
runuser -l "${TARGET_USER}" -c "mv '${EICAR_SOURCE_PATH}' '${EICAR_DEST_PATH}'"

log "Polling for quarantined file at ${QUARANTINED_FILE_PATH} (timeout: ${POLL_TIMEOUT_SECONDS}s)..."
SECONDS=0
while [[ $SECONDS -lt $POLL_TIMEOUT_SECONDS ]]; do
  if runuser -l "${TARGET_USER}" -c "test -f '${QUARANTINED_FILE_PATH}'"; then
    log "SUCCESS: EICAR file was successfully quarantined after ${SECONDS} seconds."
    # Also check that the original file is gone
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
journalctl -u clamav-daemon --no-pager -n 50
exit 1
