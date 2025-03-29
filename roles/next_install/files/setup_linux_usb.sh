#!/bin/bash

set -euo pipefail

echo "Usage: 'ISO_IMAGE USB_DEVICE'"
echo "Example: '~/Downloads/my.iso /dev/sda'"

ISO_IMAGE=$1
USB_DEVICE=$2

if ! lsblk --filter 'TRAN == "usb"' -o PATH | grep "${USB_DEVICE}"; then
    echo "${USB_DEVICE} does not appear to be a USB device. Aborting, disable this check and run again to proceed anyway"
    exit -1
fi

echo "Copying ISO image"
dd if=${ISO_IMAGE} of=${USB_DEVICE} bs=4M status=progress && sync

echo "All done, ejecting"
eject ${USB_DEVICE}
