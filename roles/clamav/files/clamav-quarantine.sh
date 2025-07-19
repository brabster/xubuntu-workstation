#!/bin/sh
set -e

# This script is run by clamd as the 'clamav' user.
# The full path to the infected file is passed as the first argument.
INFECTED_FILE="$1"

# The quarantine directory must have a hardcoded path or be passed as an argument.
# It cannot rely on the user's HOME environment variable.
QUARANTINE_DIR="/home/tester/Downloads/.quarantine"

# Ensure the quarantine directory exists.
mkdir -p "$QUARANTINE_DIR"

# Move the infected file into it.
mv "$INFECTED_FILE" "$QUARANTINE_DIR/"

# Send a desktop notification
su -c "notify-send 'Virus Detected' 'The file $(basename "$1") has been quarantined.'" -l "$USER"

exit 0