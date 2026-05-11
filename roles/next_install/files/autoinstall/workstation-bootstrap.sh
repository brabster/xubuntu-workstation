#!/bin/bash

set -euo pipefail

LOG_FILE="/var/log/xubuntu-workstation-bootstrap.log"
MARKER="/var/lib/xubuntu-workstation/bootstrap.done"
REPO_DIR="/opt/xubuntu-workstation"

if [[ "${EUID}" -ne 0 ]]; then
    echo "ERROR: workstation-bootstrap.sh must run as root."
    exit 1
fi

mkdir -p "$(dirname "${LOG_FILE}")" "$(dirname "${MARKER}")"

if [[ -f "${MARKER}" ]]; then
    exit 0
fi

{
    echo "=== Starting workstation bootstrap: $(date -Iseconds)"
    cd "${REPO_DIR}"

    if [[ ! -f "${REPO_DIR}/.vars.yml" ]]; then
        echo "ERROR: ${REPO_DIR}/.vars.yml is missing."
        exit 1
    fi

    ansible-playbook -i inventory workstation.yml

    touch "${MARKER}"
    systemctl disable --now xubuntu-workstation-bootstrap.service
    echo "=== Workstation bootstrap complete: $(date -Iseconds)"
} >>"${LOG_FILE}" 2>&1
