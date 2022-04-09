#!/bin/sh

set -eu

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install git ansible

mkdir -p ~/projects/brabster
cd ~/projects/brabster
git clone https://github.com/brabster/xubuntu-workstation.git

cd ~/projects/xubuntu-workstation
ansible-playbook -Kvv workstation.yml
git remote rm origin
git remote add origin git@github.com:brabster/xubuntu-workstation.git