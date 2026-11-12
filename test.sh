#!/bin/bash

set -euo pipefail

echo "Checking daily update timer and latest update result"
systemctl is-enabled --quiet xubuntu-workstation-update.timer
systemctl status xubuntu-workstation-update.service --no-pager || true
tail -n 40 /var/log/xubuntu-workstation-update.log

echo
echo "Checking cups cannot be controlled through sudo"
for action in start stop enable; do
    if sudo -l /usr/bin/systemctl "$action" cups; then
        echo "Unexpected sudo permission to $action CUPS" >&2
        exit 1
    fi
done

echo "Checking UFW is active and running"
if ! systemctl is-active --quiet ufw; then
    echo "UFW service is not active!"
    exit 1
fi
if ! ufw status | grep -q "Status: active"; then
    echo "UFW firewall is not enabled!"
    exit 1
fi

echo
echo "Checking venv is required"
! pip install jsonschema # should not work because no venv

echo
echo "Checking clamav is installed"
clamscan --version

echo
echo "Checking cups is not enabled"
! systemctl is-enabled cups

echo
echo "Checking clipboard clearing is working, need to wait to check..."
echo "hello" | xsel
sleep 61
if ! [ "" == "$(xsel -o)" ]; then
    echo "Default clipboard did not clear after 60 seconds"
    exit 1
fi

echo
echo "All good."
