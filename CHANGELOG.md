# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## [PR#30](https://github.com/brabster/xubuntu-workstation/pull/30)

### Added

-   **Opinionated NordVPN Configuration**: The `nordvpn` role now automates post-installation configuration to enforce secure defaults. This includes enabling the `killswitch` and `threatprotectionlite` features.

### Security

-   **Threat Model Assessment**: This change **reduces the risk of IP address exposure and malware infection**. By enabling the kill switch, it prevents traffic from leaking if the VPN disconnects. The addition of threat protection blocks malicious websites at the DNS level. Automating these settings ensures a consistent and secure baseline, mitigating risks associated with manual configuration.

## [PR#29](https://github.com/brabster/xubuntu-workstation/pull/29)

### Added

-   **Automated ISO Download and Verification**: Introduced a new script to securely download the latest Xubuntu ISO and verify its integrity using SHA256 checksums. This ensures the base operating system image is authentic and has not been tampered with.

### Security

-   **Threat Model Assessment**: This feature **improves the security and integrity of the initial installation media**. By automating the verification of the ISO, it mitigates the risk of installing a compromised or corrupt operating system, which is a critical step in establishing a secure baseline.

## [PR#28](https://github.com/brabster/xubuntu-workstation/pull/28)

### Fixed

-   **Ansible Linting Errors**: Resolved all linting issues reported by `ansible-lint`. This improves the overall quality and maintainability of the Ansible automation code.

### Security

-   **Threat Model Assessment**: This change has **no direct impact on the threat model** of the deployed workstation. It is a maintenance update focused on code quality, which indirectly supports security by ensuring the automation is robust and predictable.

## [PR#27](https://github.com/brabster/xubuntu-workstation/pull/27)


### Added

-   **On-Access AV Scanning**: Implemented real-time, blocking antivirus scanning for the `~/Downloads` directory using ClamAV and `fanotify`.
-   **Automated Quarantine & Notification**: Infected files are now automatically moved to a quarantine folder (`~/Downloads/.quarantine`), and a desktop notification is sent to the user.

### Security

-   **Threat Model Assessment for On-Access Scanning**: This feature represents a **significant improvement in overall security posture**.
    -   **Rationale**: The shift from manual-only scanning to real-time, blocking on-access scanning drastically reduces the window of vulnerability for malware entering via the `~/Downloads` directory. By using the kernel's `fanotify` capabilities, the system prevents any access to a new file until it is confirmed to be safe.
    -   **Benefit**: This proactive and automated threat containment mechanism significantly lowers the risk of accidental malware execution by the user, providing a much more robust defense against common threat vectors.

## [PR#26](https://github.com/brabster/xubuntu-workstation/pull/26)

### Added

-   **Passwordless `sudo` for Update Script**: The `update` script can now be executed via `sudo update` without requiring a password, making routine system maintenance more convenient. (#26)

### Security

-   **Threat Model Assessment for Passwordless Updates**: A threat model assessment was conducted for the passwordless `sudo` feature. The conclusion is that this change represents a **net decrease in overall risk**. (#26)
    -   **Rationale**: While it introduces a minor theoretical risk (an attacker with user-level access can trigger a system update), this is heavily mitigated because the script itself is owned by `root` and cannot be modified by the user.
    -   **Benefit**: The removal of friction for a routine, safe task encourages more frequent system updates. This tangible improvement in security posture outweighs the minor introduced risk.