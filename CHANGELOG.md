# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Enable UFW Firewall by Default](https://github.com/brabster/xubuntu-workstation/pull/44)

### Added

-   **UFW Firewall Enabled and Running After Reboot**: The UFW role now ensures UFW is installed, enabled, and started on boot. This can be selectively enabled or disabled for different environments.

### Security

-   **Threat Model Assessment**: This change **significantly improves the system’s network security posture and facilitates compliance with UK Cyber Essentials requirements**.
    -   **Rationale**: Enabling UFW by default ensures that only explicitly allowed network traffic is permitted, reducing exposure to remote attacks and unauthorized access. UK Cyber Essentials mandates a properly configured firewall as a baseline control for all internet-connected devices.
    -   **Benefit**: The firewall acts as a first line of defense against network-based threats, especially important for systems exposed to untrusted networks. Automating its activation and persistence across reboots eliminates the risk of accidental misconfiguration or firewall downtime, and ensures the system meets regulatory requirements for basic cyber hygiene.

## Fixes and security improvement to ClamAV on-access setup

- [PR#39](https://github.com/brabster/xubuntu-workstation/pull/39)
- [PR#32](https://github.com/brabster/xubuntu-workstation/pull/32)
- [PR#31](https://github.com/brabster/xubuntu-workstation/pull/31)

### Changed

- **Disable NordVPN killswitch by default**: unable to login without network access. Updated post-install messaging to remind user.
- **Modern, lower-risk approach to ClamAV on-access scanning**: switch from `clamd` to `clamonacc` service performing the file quaratine operation, to avoid elevating privileges of `clamd` that scans potentially malicious code.

### Security

- **NordVPN killswitch off by default**: no change to threat model, as killswitch must be disabled to log in.
- **clamonacc performs quarantine**: reduces the risk of infection, by reducing the permissions of the riskier `clamd` service.

## [Configure NordVPN](https://github.com/brabster/xubuntu-workstation/pull/30)

### Added

-   **Opinionated NordVPN Configuration**: The `nordvpn` role now automates post-installation configuration to enforce secure defaults. This includes enabling the `threatprotectionlite` feature.

### Security

-   **Threat Model Assessment**: This change **reduces the risk of malware infection**. The addition of threat protection blocks malicious websites at the DNS level. Automating these settings ensures a consistent and secure baseline, mitigating risks associated with manual configuration.

## [Automate ISO download and signature verification](https://github.com/brabster/xubuntu-workstation/pull/29)

### Added

-   **Automated ISO Download and Verification**: Introduced a new script to securely download the latest Xubuntu ISO and verify its integrity using SHA256 checksums. This ensures the base operating system image is authentic and has not been tampered with.

### Security

-   **Threat Model Assessment**: This feature **improves the security and integrity of the initial installation media**. By automating the verification of the ISO, it mitigates the risk of installing a compromised or corrupt operating system, which is a critical step in establishing a secure baseline.

## [Fix Ansible lint errors](https://github.com/brabster/xubuntu-workstation/pull/28)

### Fixed

-   **Ansible Linting Errors**: Resolved all linting issues reported by `ansible-lint`. This improves the overall quality and maintainability of the Ansible automation code.

### Security

-   **Threat Model Assessment**: This change has **no direct impact on the threat model** of the deployed workstation. It is a maintenance update focused on code quality, which indirectly supports security by ensuring the automation is robust and predictable.

## [Add ClamAV on-access scanning](https://github.com/brabster/xubuntu-workstation/pull/27)

### Added

-   **On-Access AV Scanning**: Implemented real-time, blocking antivirus scanning for the `~/Downloads` directory using ClamAV and `fanotify`.
-   **Automated Quarantine & Notification**: Infected files are now automatically moved to a quarantine folder (`~/Downloads/.quarantine`), and a desktop notification is sent to the user.

### Security

-   **Threat Model Assessment for On-Access Scanning**: This feature represents a **significant improvement in overall security posture**.
    -   **Rationale**: The shift from manual-only scanning to real-time, blocking on-access scanning drastically reduces the window of vulnerability for malware entering via the `~/Downloads` directory. By using the kernel's `fanotify` capabilities, the system prevents any access to a new file until it is confirmed to be safe.
    -   **Benefit**: This proactive and automated threat containment mechanism significantly lowers the risk of accidental malware execution by the user, providing a much more robust defense against common threat vectors.

## [Passwordless sudo for update script](https://github.com/brabster/xubuntu-workstation/pull/26)

### Added

-   **Passwordless `sudo` for Update Script**: The `update` script can now be executed via `sudo update` without requiring a password, making routine system maintenance more convenient. (#26)

### Security

-   **Threat Model Assessment for Passwordless Updates**: A threat model assessment was conducted for the passwordless `sudo` feature. The conclusion is that this change represents a **net decrease in overall risk**. (#26)
    -   **Rationale**: While it introduces a minor theoretical risk (an attacker with user-level access can trigger a system update), this is heavily mitigated because the script itself is owned by `root` and cannot be modified by the user.
    -   **Benefit**: The removal of friction for a routine, safe task encourages more frequent system updates. This tangible improvement in security posture outweighs the minor introduced risk.

