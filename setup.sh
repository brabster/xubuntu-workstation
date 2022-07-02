#!/bin/sh

set -eu

echo "=== Updating packages and installing git & ansible (sudo required)"
sudo sh -c 'apt-get update && apt-get upgrade && apt-get install git ansible'

echo "=== Cloning repo"
mkdir -p ~/projects/brabster
cd ~/projects/brabster
git clone https://github.com/brabster/xubuntu-workstation.git
cd ~/projects/brabster/xubuntu-workstation

echo "=== Running playbook (sudo required)"
ansible-playbook -K workstation.yml
git remote rm origin
git remote add origin git@github.com:brabster/xubuntu-workstation.git
