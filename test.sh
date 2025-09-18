#!/bin/bash

set -euo pipefail

echo "Checking update script works"
sudo update

echo
echo "Checking cups can be started and stopped, but not enabled"
sudo systemctl start cups
sudo systemctl stop cups
! sudo systemctl enable cups

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
