#!/bin/sh
set -e

# In modern ClamAV, the filename is passed via an environment variable.
INFECTED_FILE="$CLAM_VIRUSEVENT_FILENAME"

# Define the global quarantine directory.
QUARANTINE_DIR="/var/lib/clamav/quarantine"

# Exit cleanly if the filename variable is empty for any reason.
if [ -z "$INFECTED_FILE" ]; then
    exit 0
fi

# Move the infected file.
# We no longer need sudo since the quarantine dir is owned by clamav.
mv "$INFECTED_FILE" "$QUARANTINE_DIR/"

exit 0