#!/bin/sh

set -eu

echo "=== setup.sh must be run as root."

echo "=== Updating packages and installing git & ansible"
sudo sh -c 'apt-get update && apt-get upgrade && apt-get install git ansible'

echo "=== Running playbook"
ansible-playbook workstation.yml

echo "=== Log out and in again, no need to reboot."

