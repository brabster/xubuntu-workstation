#!/bin/sh

set -eu

echo "=== setup.sh must be run as root."

echo "=== Updating packages and installing git & ansible"
sudo sh -c 'apt-get update && apt-get upgrade && apt-get install git ansible'

echo "=== Cloning repo into $(pwd)"
git clone https://github.com/brabster/xubuntu-workstation.git

echo "=== cd into xubuntu-workstation.."
echo "=== Create gitignored .vars.yml with undefined form vars.yml (or pass --extra-vars arg on next instruction)"
echo "=== Then run ansible-playbook workstation.yml"
echo "=== Finally, log out and in again, no need to reboot."

