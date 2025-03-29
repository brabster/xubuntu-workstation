#!/bin/bash

set -euo pipefail

echo "Usage: 'PROJECT_ROOT USB_DEVICE', example '~/projects/xubuntu-workstation /dev/sda'"

PROJECT_ROOT=$1
USB_DEVICE=$2

if ! lsblk --filter 'TRAN == "usb"' -o PATH | grep "${USB_DEVICE}"; then
    echo "${USB_DEVICE} does not appear to be a USB device. Aborting, disable this check and run again to proceed anyway"
    exit 1
fi

echo "Wiping ${USB_DEVICE} MBR"
dd if=/dev/zero of=${USB_DEVICE} bs=512 count=10

echo "Partitioning ${USB_DEVICE}"

parted -l

parted --script "${USB_DEVICE}" mklabel gpt mkpart primary 0% 100%

parted -l

USB_PARTITION=${USB_DEVICE}1

echo "Formatting partition ${USB_PARTITION}"
mkfs.ext4 -vL xubuntu_setup "${USB_PARTITION}"

echo "Mounting new partition"
MOUNT_DIR=$(mktemp -d)
mount -t auto -v "${USB_PARTITION}" "${MOUNT_DIR}"

echo "Copying bootstrap files"
for src_file in roles bootstrap.sh test.sh README.md workstation.yml vars.yml .vars.yml; do
    cp -r "${PROJECT_ROOT}"/${src_file} "${MOUNT_DIR}"
done
sync

echo "All done, ejecting"
umount "${USB_PARTITION}"
eject "${USB_PARTITION}"
rm -rf "${MOUNT_DIR}"




