#!/bin/sh
set -e

INFECTED_FILE="$1"
QUARANTINE_DIR="$2"

# Ensure the quarantine directory exists.
mkdir -p "$QUARANTINE_DIR"

# Execute the move command with elevated privileges to bypass AppArmor.
sudo /bin/mv "$INFECTED_FILE" "$QUARANTINE_DIR/"

exit 0