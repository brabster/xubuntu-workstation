#!/bin/sh

set -eu

echo "=== setup.sh must be run as root."

echo "=== Updating packages and installing git & ansible"
sudo sh -c 'apt-get update && apt-get upgrade && apt-get install git ansible'

echo "=== Cloning repo into $(pwd)"
git clone https://github.com/brabster/xubuntu-workstation.git

echo "=== Update undefined vars.yml"
echo "=== Then run ansible-playbook workstation.yml"

