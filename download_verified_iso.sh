#!/bin/bash
set -euo pipefail

if [[ $# -ne 1 || -z "$1" ]]; then
    echo "Error: You must provide the full URL to the ISO image." >&2
    echo "Usage: $0 <URL_to_ISO>" >&2
    exit 1
fi

ISO_URL="$1"
ISO_FILE=$(basename "${ISO_URL}")
BASE_URL=$(dirname "${ISO_URL}")/
SUMS_FILE="SHA256SUMS"
SIG_FILE="SHA256SUMS.gpg"

echo "Verifying: ${ISO_FILE}"
echo "--------------------------------------------------------"

echo "Downloading required files from ${BASE_URL}..."
wget -q --show-progress -c "${ISO_URL}"
wget -q --show-progress -c "${BASE_URL}${SUMS_FILE}"
wget -q --show-progress -c "${BASE_URL}${SIG_FILE}"
echo "Downloads complete."
echo ""

echo "Verifying the GPG signature of ${SUMS_FILE}..."
if ! gpg --verify "${SIG_FILE}" "${SUMS_FILE}" >/dev/null 2>&1; then
    echo "   GPG keys not found. Attempting to fetch official Ubuntu keys..."
    gpg --keyserver hkp://keyserver.ubuntu.com --recv-keys 0x46181433FBB75451 0xD94AA3F0EFE21092 >/dev/null
fi

echo "   A 'Good signature' message confirms the checksum file is authentic."
echo "   A 'key is not certified' warning is normal and can be safely ignored."
gpg --verify "${SIG_FILE}" "${SUMS_FILE}"
echo "GPG signature is valid."
echo ""

echo "Verifying the checksum of ${ISO_FILE}..."
grep "${ISO_FILE}" "${SUMS_FILE}" | sha256sum --check --strict
echo ""

echo "--------------------------------------------------------"
echo "Success! ${ISO_FILE} is fully downloaded and verified."