#!/bin/sh

set -eu

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install git ansible

mkdir -p ~/projects/brabster
cd ~/projects/brabster
git clone https://github.com/brabster/xubuntu-workstation.git

cd ~/projects/brabster/xubuntu-workstation
ansible-playbook -K workstation.yml
git remote rm origin
git remote add origin git@github.com:brabster/xubuntu-workstation.git