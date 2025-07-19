#!/bin/sh
set -e

# The full path to the infected file is the first argument.
INFECTED_FILE="$1"

# The quarantine directory is now passed as the second argument.
QUARANTINE_DIR="$2"

# Ensure the quarantine directory exists (though Ansible should have made it).
mkdir -p "$QUARANTINE_DIR"

# Move the infected file into it. No sudo is needed.
mv "$INFECTED_FILE" "$QUARANTINE_DIR/"

exit 0