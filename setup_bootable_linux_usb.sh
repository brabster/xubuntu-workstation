#!/bin/bash

set -euo pipefail

echo "Usage: 'ISO_IMAGE USB_DEVICE'"
echo "Example: '~/Downloads/my.iso /dev/sda'"

ISO_IMAGE=$1
USB_DEVICE=$2

cp ${ISO_IMAGE} ${USB_DEVICE} && sync
eject /dev/sda