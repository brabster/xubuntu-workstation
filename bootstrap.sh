#!/bin/sh

set -eu

if [ "$(id -u)" -ne 0 ]; then
  echo "=== bootstrap.sh must be run as root." >&2
  exit 1
fi

echo "=== Updating packages and installing git, ansible-core, sudo and bzip2"
apt-get -y update
apt-get -y upgrade
apt-get -y install git ansible-core sudo bzip2

echo "=== Installing declared Ansible collections"
ansible-galaxy collection install -r roles/requirements.yml

echo "=== Running playbook"
ansible-playbook -i inventory workstation.yml

echo "=== Log out and in again, them run test.sh. No need to reboot."
echo "=== Note that the NordVPN network killswitch is OFF and requires activation"
