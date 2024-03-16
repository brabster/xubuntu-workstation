#!/bin/sh

set -eu

echo "=== setup.sh must be run as root."

echo "=== Updating packages and installing git & ansible"
sudo sh -c 'apt-get -y update && apt-get -y upgrade && apt-get -y install git ansible'

echo "=== Running playbook"
ansible-playbook -i inventory workstation.yml

echo "=== Log out and in again, no need to reboot."
