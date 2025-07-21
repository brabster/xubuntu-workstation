# Meta-Prompt for `xubuntu-workstation` Contributor: Configure NordVPN

## CONTEXT

This document outlines the plan to enhance the `nordvpn` Ansible role. The goal is to configure essential permissions and set secure, opinionated defaults for the NordVPN client as part of the automated installation process.

**Design Observations:**
*   Cloudflare DNS over HTTPS is already configured system-wide, so we will not configure NordVPN's DNS servers to avoid conflicts.
*   The `nordlynx` protocol does not support the `obfuscate` feature, so this setting will not be applied.
*   Default notification settings will be retained unless they become problematic.

## PERSONA

As an expert DevOps and Platform Engineer, I will apply security best practices and Ansible standards to implement this feature.

## CORE PRINCIPLES

I will adhere to the established principles of security, idempotency, and modularity.

---

## Phase 1: Analysis and Implementation Plan

### 1. Objective

To enhance the `nordvpn` Ansible role to automatically configure application permissions and set user-defined defaults for security and functionality. This ensures that NordVPN is installed in a ready-to-use, secure state, with appropriate controls and settings applied consistently.

### 2. Plan

1.  **Create Configuration Script**: Create a new shell script at `roles/nordvpn/files/configure_nordvpn.sh`. This script will serve as a single, testable unit for applying all settings. The script will contain the following commands:
    ```bash
    #!/bin/bash
    set -euo pipefail

    nordvpn set technology nordlynx
    nordvpn set killswitch on
    nordvpn set threatprotectionlite on
    nordvpn set autoconnect on
    nordvpn set meshnet off
    ```
2.  **Update Ansible Role**: Modify `roles/nordvpn/tasks/main.yml` to perform the following actions:
    *   **Connect Snap Interfaces**: Add tasks to connect the required snap interfaces for NordVPN (`hardware-observe`, `network-control`, `network-observe`, `firewall-control`, `login-session-observe`, `system-observe`).
    *   **Deploy and Execute Script**:
        *   Copy the `configure_nordvpn.sh` script to `/usr/local/bin/` on the target machine.
        *   Ensure the script is executable.
        *   Run the script as the logged-in user to apply the settings.
3.  **Tagging**: Ensure all new tasks are tagged with `nordvpn` for granular execution and testing.

### 3. Rationale

*   **Permissions**: Connecting the snap interfaces is a mandatory post-installation step. Automating this ensures the application has the necessary permissions to manage network connections securely.
*   **Atomic Configuration**: Consolidating the configuration commands into a single script makes the process atomic and easier to test independently. This is cleaner than a series of individual `command` tasks in Ansible.
*   **Security**: Enabling the kill switch and threat protection by default enhances the security posture of the workstation immediately upon installation.

---

## Phase 2: Code Implementation

The following files will be created or modified:

*   `roles/nordvpn/files/configure_nordvpn.sh` (new file)
*   `roles/nordvpn/tasks/main.yml` (modified)

---

## Phase 3: Verification and Testing Plan

1.  **Static Analysis (Linting)**:
    ```bash
    ansible-lint workstation.yml
    ```
2.  **Dry Run (Check Mode)**:
    This command will report the changes that would be made without actually executing them.
    ```bash
    ansible-playbook workstation.yml --check --diff --tags nordvpn
    ```
3.  **Live Execution**:
    This command will apply the changes to the system.
    ```bash
    ansible-playbook workstation.yml --tags nordvpn
    ```
4.  **Post-Execution Verification**:
    After the playbook runs, verify the changes with the following commands:
    *   Check that the snap interfaces are connected:
        ```bash
        snap connections nordvpn
        ```
    *   Check that the script is in place and executable:
        ```bash
        ls -l /usr/local/bin/configure_nordvpn.sh
        ```
    *   Check that the settings have been applied correctly by running the verification command as the user:
        ```bash
        nordvpn settings
        ```