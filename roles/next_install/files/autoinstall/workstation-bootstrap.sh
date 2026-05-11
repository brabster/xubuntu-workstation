#!/bin/bash

set -euo pipefail

LOG_FILE="/var/log/xubuntu-workstation-bootstrap.log"
MARKER="/var/lib/xubuntu-workstation/bootstrap.done"
FAILED_MARKER="/var/lib/xubuntu-workstation/bootstrap.failed"
REPO_DIR="/opt/xubuntu-workstation"

if [[ "${EUID}" -ne 0 ]]; then
    echo "ERROR: workstation-bootstrap.sh must run as root."
    exit 1
fi

mkdir -p "$(dirname "${LOG_FILE}")" "$(dirname "${MARKER}")"

if [[ -f "${MARKER}" ]]; then
    exit 0
fi

on_error() {
    local line_number="$1"
    touch "${FAILED_MARKER}"
    local message="ERROR: bootstrap failed at line ${line_number}. See ${LOG_FILE}."
    echo "${message}"
    echo "${message}" >>"${LOG_FILE}"
}

trap 'on_error ${LINENO}' ERR

{
    echo "=== Starting workstation bootstrap: $(date -Iseconds)"
    rm -f "${FAILED_MARKER}"
    cd "${REPO_DIR}"

    if [[ ! -f "${REPO_DIR}/.vars.yml" ]]; then
        echo "ERROR: ${REPO_DIR}/.vars.yml is missing."
        exit 1
    fi

    ansible-playbook -v -i inventory workstation.yml

    touch "${MARKER}"
    systemctl disable --now xubuntu-workstation-bootstrap.service
    echo "=== Workstation bootstrap complete: $(date -Iseconds)"
} >>"${LOG_FILE}" 2>&1
