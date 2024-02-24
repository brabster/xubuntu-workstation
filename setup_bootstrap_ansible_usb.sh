#!/bin/bash

set -euo pipefail

echo "Usage: 'USB_DEVICE'"
echo "Example: '/dev/sda'"

USB_DEVICE=$1
SCRIPT_DIR=$(dirname "$0")

echo "Wiping ${USB_DEVICE} MBR"
dd if=/dev/zero of=${USB_DEVICE} bs=512 count=1 conv=notrunc

echo "Partitioning ${USB_DEVICE}"
parted --script "${USB_DEVICE}" \
    mklabel gpt \
    mkpart primary 0% 100$

fdisk -l ${USB_DEVICE}

USB_PARTITION=${USB_DEVICE}1

echo "Formatting partition ${USB_PARTITION}"
mkfs.ext4 -L xubuntu_setup "${USB_PARTITION}"

MOUNT_DIR=$(mktemp -d)
mount -t auto -v "${USB_PARTITION}" "${MOUNT_DIR}"

for src_file in roles .vars.yml bootstrap.sh README.md workstation.yml vars.yml; do
    cp -r "${SCRIPT_DIR}"/${src_file} "${MOUNT_DIR}"
done
sync
umount "${USB_PARTITION}"
eject "${USB_PARTITION}"
rm -rf "${MOUNT_DIR}"




