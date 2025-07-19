#!/bin/bash

# Quarantine directory
QUARANTINE_DIR="$HOME/Downloads/.quarantine"

# Ensure the quarantine directory exists
mkdir -p "$QUARANTINE_DIR"

# Move the infected file to the quarantine directory
mv "$1" "$QUARANTINE_DIR/"

# Send a desktop notification
su -c "notify-send 'Virus Detected' 'The file $(basename "$1") has been quarantined.'" -l "$USER"