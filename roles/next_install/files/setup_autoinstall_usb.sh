#!/bin/bash

set -euo pipefail

LOG_FILE="/var/log/setup_autoinstall_usb.log"
STATE_DIR="${XUBUNTU_AUTOINSTALL_STATE_DIR:-/var/cache/xubuntu-autoinstall-build}"
DD_BLOCK_SIZE="${XUBUNTU_AUTOINSTALL_DD_BS:-4M}"

exec > >(tee -a "${LOG_FILE}") 2>&1

on_error() {
    local line_number="$1"
    echo "ERROR: setup_autoinstall_usb.sh failed at line ${line_number}. See ${LOG_FILE} for details."
}
trap 'on_error ${LINENO}' ERR

usage() {
    echo "Usage: sudo setup_autoinstall_usb.sh <ISO_URL> <PROJECT_ROOT> <USB_DEVICE>"
    echo "Example: sudo setup_autoinstall_usb.sh https://cdimage.ubuntu.com/xubuntu/releases/24.04/release/xubuntu-24.04.2-desktop-amd64.iso ~/projects/xubuntu-workstation /dev/sda"
    echo "Optional override: set XUBUNTU_AUTOINSTALL_STATE_DIR to change cached build artifact location."
}

require_cmd() {
    local cmd="$1"
    if ! command -v "${cmd}" >/dev/null 2>&1; then
        echo "ERROR: Required command '${cmd}' is not installed."
        exit 1
    fi
}

if [[ "${EUID}" -ne 0 ]]; then
    echo "ERROR: This script must run as root (use sudo)."
    exit 1
fi

if [[ $# -ne 3 ]]; then
    usage
    exit 1
fi

ISO_URL="$1"
PROJECT_ROOT="$2"
USB_DEVICE="$3"

if [[ ! -d "${PROJECT_ROOT}" ]]; then
    echo "ERROR: PROJECT_ROOT '${PROJECT_ROOT}' does not exist."
    exit 1
fi

if ! lsblk --filter 'TRAN == "usb"' -o PATH | grep -q "^${USB_DEVICE}$"; then
    echo "ERROR: ${USB_DEVICE} does not appear to be a USB device."
    exit 1
fi

VARS_FILE="${PROJECT_ROOT}/.vars.yml"
if [[ ! -f "${VARS_FILE}" ]]; then
    echo "ERROR: ${VARS_FILE} not found."
    echo "Create it from ${PROJECT_ROOT}/.vars_example.yml before running this script."
    exit 1
fi

require_cmd wget
require_cmd gpgv
require_cmd xorriso
require_cmd rsync
require_cmd awk
require_cmd sed
require_cmd dd
require_cmd mount
require_cmd umount
require_cmd sync

read_var() {
    local key="$1"
    awk -F': *' -v target="${key}" '$1 == target { sub(/^"/, "", $2); sub(/"$/, "", $2); print $2; exit }' "${VARS_FILE}"
}

USERNAME="$(read_var username)"
GIT_NAME="$(read_var git_name)"
GIT_EMAIL="$(read_var git_email)"
AUTOINSTALL_PASSWORD_HASH="$(read_var autoinstall_password_hash)"
AUTOINSTALL_HOSTNAME="$(read_var autoinstall_hostname)"

if [[ -z "${USERNAME}" || -z "${GIT_NAME}" || -z "${GIT_EMAIL}" || -z "${AUTOINSTALL_PASSWORD_HASH}" ]]; then
    echo "ERROR: .vars.yml must define username, git_name, git_email, and autoinstall_password_hash."
    exit 1
fi

if [[ -z "${AUTOINSTALL_HOSTNAME}" ]]; then
    AUTOINSTALL_HOSTNAME="${USERNAME}-workstation"
fi

mkdir -p "${STATE_DIR}"
chmod 0700 "${STATE_DIR}"
WORK_DIR="$(mktemp -d)"
MOUNT_DIR="${WORK_DIR}/iso_mount"
ISO_EXTRACT_DIR="${WORK_DIR}/iso_extract"
AUTOINSTALL_DIR="${ISO_EXTRACT_DIR}/autoinstall"

cleanup() {
    if mountpoint -q "${MOUNT_DIR}"; then
        umount "${MOUNT_DIR}"
    fi
    rm -rf "${WORK_DIR}"
}
trap cleanup EXIT

ISO_FILE="$(basename "${ISO_URL}")"
VERIFIED_ISO_PATH="${STATE_DIR}/${ISO_FILE}"
AUTOINSTALL_ISO_PATH="${STATE_DIR}/autoinstall-${ISO_FILE}"

echo "State directory: ${STATE_DIR}"
echo "Log file: ${LOG_FILE}"

if [[ ! -f "${VERIFIED_ISO_PATH}" ]]; then
    echo "Step 1/4: Downloading and verifying ISO"
    (
        cd "${STATE_DIR}"
        /usr/local/bin/download_verified_iso.sh "${ISO_URL}"
    )
else
    echo "Step 1/4: Reusing previously verified ISO at ${VERIFIED_ISO_PATH}"
fi

if [[ ! -f "${AUTOINSTALL_ISO_PATH}" ]]; then
    echo "Step 2/4: Building autoinstall ISO"
    mkdir -p "${MOUNT_DIR}" "${ISO_EXTRACT_DIR}" "${AUTOINSTALL_DIR}"

    mount -o loop "${VERIFIED_ISO_PATH}" "${MOUNT_DIR}"
    rsync -a "${MOUNT_DIR}/" "${ISO_EXTRACT_DIR}/"
    umount "${MOUNT_DIR}"

    cp "${PROJECT_ROOT}/roles/next_install/files/autoinstall/meta-data" "${AUTOINSTALL_DIR}/meta-data"
    cp "${PROJECT_ROOT}/roles/next_install/files/autoinstall/workstation-bootstrap.sh" "${AUTOINSTALL_DIR}/workstation-bootstrap.sh"
    cp "${PROJECT_ROOT}/roles/next_install/files/autoinstall/xubuntu-workstation-bootstrap.service" "${AUTOINSTALL_DIR}/xubuntu-workstation-bootstrap.service"
    cp "${PROJECT_ROOT}/roles/next_install/files/autoinstall/user-data.template" "${AUTOINSTALL_DIR}/user-data"

    sed -i "s|__USERNAME__|${USERNAME}|g" "${AUTOINSTALL_DIR}/user-data"
    sed -i "s|__HOSTNAME__|${AUTOINSTALL_HOSTNAME}|g" "${AUTOINSTALL_DIR}/user-data"
    sed -i "s|__PASSWORD_HASH__|${AUTOINSTALL_PASSWORD_HASH}|g" "${AUTOINSTALL_DIR}/user-data"

    mkdir -p "${AUTOINSTALL_DIR}/xubuntu-workstation"
    rsync -a --delete \
        --exclude='.git' \
        --exclude='.github' \
        --exclude='.devcontainer' \
        --exclude='.venv' \
        --exclude='.vars.yml' \
        --exclude='*.retry' \
        "${PROJECT_ROOT}/" "${AUTOINSTALL_DIR}/xubuntu-workstation/"
    cp "${VARS_FILE}" "${AUTOINSTALL_DIR}/xubuntu-workstation/.vars.yml"

    for boot_cfg in "${ISO_EXTRACT_DIR}/boot/grub/grub.cfg" "${ISO_EXTRACT_DIR}/isolinux/txt.cfg"; do
        if [[ -f "${boot_cfg}" ]]; then
            sed -i 's| quiet ---| autoinstall ds=nocloud\\;s=/cdrom/autoinstall/ quiet ---|g' "${boot_cfg}"
        fi
    done

    if [[ -f "${ISO_EXTRACT_DIR}/md5sum.txt" ]]; then
        (
            cd "${ISO_EXTRACT_DIR}"
            # Exclude md5sum.txt itself and El Torito boot catalog to match Ubuntu ISO checksum conventions.
            find . -type f ! -name md5sum.txt ! -path './isolinux/boot.cat' -print0 | xargs -0 md5sum > md5sum.txt
        )
    fi

    xorriso -as mkisofs \
        -r \
        -V "XUBUNTU_AUTOINSTALL" \
        -o "${AUTOINSTALL_ISO_PATH}" \
        -J -joliet-long -l \
        -b isolinux/isolinux.bin \
        -c isolinux/boot.cat \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -eltorito-alt-boot \
        -e boot/grub/efi.img \
        -no-emul-boot \
        -isohybrid-gpt-basdat \
        "${ISO_EXTRACT_DIR}"
else
    echo "Step 2/4: Reusing previously built autoinstall ISO at ${AUTOINSTALL_ISO_PATH}"
fi

echo "Step 3/4: Writing autoinstall ISO to ${USB_DEVICE}"
mapfile -t MOUNT_POINTS < <(lsblk -nrpo MOUNTPOINT "${USB_DEVICE}" | awk 'NF')
if (( ${#MOUNT_POINTS[@]} > 0 )); then
    for mount_point in "${MOUNT_POINTS[@]}"; do
        if ! umount -f "${mount_point}"; then
            echo "ERROR: Failed to unmount ${mount_point}. Check active processes with lsof/fuser and retry."
            exit 1
        fi
    done
fi
dd if="${AUTOINSTALL_ISO_PATH}" of="${USB_DEVICE}" bs="${DD_BLOCK_SIZE}" status=progress conv=fsync
sync

echo "Step 4/4: Done"
echo "Autoinstall USB created successfully: ${USB_DEVICE}"
echo "Boot from this USB and the workstation bootstrap will run automatically on first boot."
echo "On failure, inspect /var/log/xubuntu-workstation-bootstrap.log on the installed machine."
