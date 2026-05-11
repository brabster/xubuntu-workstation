# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## [Show recent freshclam output when current log is empty](https://github.com/brabster/xubuntu-workstation/pull/70)

### Fixed

- **ClamAV verify output after overnight suspend**: `clamav-verify.sh` now falls back to rotated `freshclam` logs (`freshclam.log.1` and `.gz` archives) when `/var/log/clamav/freshclam.log` is empty. This keeps the "latest antivirus update log" section populated after log rotation windows where no new lines have been appended yet.

### Security

- **Threat Model Assessment**: This change **reduces risk** by improving visibility of antivirus update evidence without changing ClamAV execution or privilege boundaries.
    - **Rationale**: After overnight suspend/resume, log rotation can leave the active `freshclam.log` temporarily empty even when update activity recently occurred, which hides operational evidence and can mask stale-signature conditions during manual checks.
    - **Benefit**: Operators reliably see recent update events during health checks, supporting UK Cyber Essentials intent for effective malware protection operations and routine verification.

## [Fix updates role Ansible fact deprecation warning](https://github.com/brabster/xubuntu-workstation/pull/66)

### Fixed

- **Deprecated fact reference in sudoers update task**: Replaced `ansible_hostname` with `ansible_facts["hostname"]` in `roles/updates/tasks/main.yml` to align with ansible-core deprecation guidance and avoid reliance on top-level fact injection (`INJECT_FACTS_AS_VARS`).

### Security

- **Threat Model Assessment**: This change **slightly reduces operational risk** and does not change workstation privilege boundaries.
    - **Rationale**: The `updates` role manages privileged update access (`/etc/sudoers`). Removing deprecated fact usage prevents future ansible-core behavior changes from silently breaking this automation path.
    - **Benefit**: Keeps security update workflows reliable over ansible-core upgrades, supporting UK Cyber Essentials intent for timely, dependable patching processes.
## [Make cleanup_services idempotent after avahi-daemon removal](https://github.com/brabster/xubuntu-workstation/pull/63)

### Fixed

- **Repeat setup runs after service removal**: The `cleanup_services` role now skips stop/disable actions when `service_facts` reports `not-found` for `avahi-daemon.service` or `ModemManager.service`. This prevents reruns failing after the packages were already removed on a previous run.

### Security

- **Threat Model Assessment**: This change **keeps net risk unchanged** while improving reliability of the hardening workflow.
    - **Rationale**: The role still removes unnecessary services and packages to reduce exposed functionality. The update only prevents failures when units are already absent, preserving least-functionality controls expected by UK Cyber Essentials.
    - **Benefit**: Re-running setup remains safe and repeatable without weakening existing service-removal protections.

## [Fix ISO signature verification by using Ubuntu archive keyring](https://github.com/brabster/xubuntu-workstation/pull/61)

### Fixed

- **ISO verification public key failure**: `download_verified_iso.sh` now verifies `SHA256SUMS.gpg` with the system Ubuntu archive keyring (`/usr/share/keyrings/ubuntu-archive-keyring.gpg`) instead of the caller's personal GPG keyring. This resolves `gpg: Can't check signature: No public key` when validating current Xubuntu release images.

### Security

- **Threat Model Assessment**: This change **reduces risk** in installation media verification while preserving existing trust boundaries.
    - **Rationale**: Verifying against the explicit, distro-managed Ubuntu archive keyring prevents false verification failures caused by missing user keyring state, and avoids ad-hoc key imports from keyservers that can increase supply-chain and trust-on-first-use risk.
    - **Benefit**: ISO authenticity checks are now reliable on clean systems where `ubuntu-keyring` is installed, improving integrity assurance for bootstrap media and supporting UK Cyber Essentials expectations for using trusted software sources and verification.

## [Set up a minimal devcontainer image](https://github.com/brabster/xubuntu-workstation/pull/58)

### Added

- **Devcontainer configuration**: Added `.devcontainer/Dockerfile` and `.devcontainer/devcontainer.json` to support development of this project in a GitHub Codespace. The image extends `mcr.microsoft.com/devcontainers/base:ubuntu` and pre-installs `ansible` and `ansible-lint`, providing the minimum tooling needed to edit roles, run linting (`ansible-lint workstation.yml`), and test in check mode (`ansible-playbook --check`).

### Security

- **Threat Model Assessment**: This change has a **small net reduction in contributor setup risk** and **no change to managed workstation runtime risk**.
    - **Rationale**: Using the official Microsoft devcontainers base image (`mcr.microsoft.com/devcontainers/base:ubuntu`) ensures a maintained, trusted foundation with a non-root user by default, reducing privilege-escalation risk in the development environment. Only `ansible` and `ansible-lint` are added on top, and no secrets or credentials are embedded.
    - **Benefit**: Contributors can develop and validate Ansible roles in an isolated, reproducible container without needing to configure a local environment manually. This reduces the risk of environment-specific configuration drift and accidental changes to a developer's own system while leaving production and workstation security controls unchanged.


## [Prevent GitHub Actions from running on documentation changes](https://github.com/brabster/xubuntu-workstation/pull/55)

### Changed

- **CI path filtering added**: The `push` trigger in `.github/workflows/test_install.yml` now uses `paths-ignore` to skip CI runs when only documentation and meta files are changed (`**/*.md`, `prompts/**`, `.vars_example.yml`). The `workflow_dispatch` and `schedule` triggers are unaffected and continue to run unconditionally.

### Security

- **Threat Model Assessment**: This change **does not affect workstation runtime configuration or security posture**.
    - **Rationale**: Running the full CI suite on every documentation commit wastes compute resources and adds noise without providing any validation signal, since documentation files are not exercised by the Ansible playbook tests.
    - **Benefit**: CI runs remain reliable and fast for changes that matter; documentation-only commits no longer consume runner minutes unnecessarily. This does not weaken any control required by UK Cyber Essentials, as the CI validation suite is unchanged.

## [Disable DNS over TLS to restore name resolution when using NordVPN](https://github.com/brabster/xubuntu-workstation/pull/54)

### Fixed

-   **DNS resolution broken when using NordVPN**: `DNSOverTLS=yes` has been removed from the Cloudflare for Families `systemd-resolved` configuration. DNS over TLS (DoT) requires a direct TLS connection to Cloudflare on port 853, which NordVPN intercepts and breaks, causing name resolution to fail entirely while the VPN is active.

### Security

-   **Threat Model Assessment**: This change **removes DNS over TLS (DoT) from the Cloudflare for Families configuration** to restore compatibility with NordVPN.
    -   **Rationale**: DoT provides transport-layer encryption for DNS queries, protecting against eavesdropping on the local network path to the resolver. However, when NordVPN is active it routes all DNS traffic through its own encrypted tunnel, so DoT's protection is effectively duplicated. Enabling DoT simultaneously causes TLS handshake failures to port 853, breaking DNS for all applications.
    -   **Benefit**: DNS resolution is reliable whether or not NordVPN is in use. The Cloudflare for Families content-filtering DNS servers (blocking malware and adult content) remain in effect. When NordVPN is connected, DNS traffic is protected by the VPN tunnel, maintaining confidentiality without requiring DoT. This aligns with UK Cyber Essentials requirements for a functioning, consistently available network configuration.

## [Set up Copilot coding agent instructions](https://github.com/brabster/xubuntu-workstation/pull/53)

### Added

- **Repository Copilot instructions**: Added `.github/copilot-instructions.md` to define secure and stable coding-agent defaults, faster validation feedback loops, and explicit prompting-quality guidance (including suggesting prompt improvements when interactions are inefficient).

### Security

- **Threat Model Assessment**: This change **improves delivery safety and consistency without changing workstation runtime configuration**.
    - **Rationale**: Standardized agent instructions reduce the risk of unsafe automation suggestions (for example unnecessary privilege escalation or weak provenance practices), and reinforce evidence-first diagnostics before remediation.
    - **Benefit**: Improves alignment with UK Cyber Essentials intent by reinforcing secure change behaviour, traceable security rationale, and reliable validation practices in repository contributions.

## [Ubuntu 26.04 compatibility: fix Chrome install on rolling release](https://github.com/brabster/xubuntu-workstation/pull/52)

### Fixed

- **Chrome installation on Ubuntu 26.04+**: Google Chrome's `.deb` package declares a dependency on `libasound2 (>= 1.0.17)`, but in Ubuntu 24.04 the ALSA sound library was renamed to `libasound2t64` as part of the 64-bit `time_t` transition. In Ubuntu 26.04, `libasound2t64` no longer provides `libasound2` as a virtual package, making the dependency unsatisfiable and blocking Chrome installation. The `chrome-browser` role now pre-installs `libasound2t64` (with a cache refresh) before installing Chrome, which satisfies the runtime library requirement and allows the plain `apt install` of Chrome to succeed.

### Security

- **Threat Model Assessment**: This change **maintains the existing security posture** while restoring Chrome installation on the latest Ubuntu rolling release.
    - **Rationale**: Without this fix, Chrome could not be installed on Ubuntu 26.04, leaving users without a managed, policy-controlled browser. Pre-installing `libasound2t64` is a minimal, targeted change that ensures the required ALSA shared library is present before Chrome is installed.
    - **Benefit**: Chrome's managed policy configuration (enforced HTTPS, Safe Browsing, download restrictions) remains fully applied on Ubuntu 26.04, maintaining the browser security controls required for UK Cyber Essentials compliance. Chrome updates via Google's apt repository (registered automatically by the Chrome installer) remain unaffected.

## [Disable and remove unneeded services by default](https://github.com/brabster/xubuntu-workstation/pull/45)

Fixes on [PR#46](https://github.com/brabster/xubuntu-workstation/pull/46).

### Added

- **Unnecessary services disabled and removed**: The cleanup role now disables the ModemManager and avahi-daemon services and removes the associated packages by default. This ensures the services are not running after reboot and the packages are not present unless explicitly required.

### Security

- **Threat Model Assessment**: This change **reduces the attack surface and supports compliance with UK Cyber Essentials requirements**.
    - **Rationale**: Services are not required for most workstation use cases and represents an unnecessary service and software package. Disabling and removing it aligns with the principle of least functionality, as mandated by UK Cyber Essentials, and reduces the risk of exploitation via unused system components.
    - **Benefit**: Ensures only necessary services are present and running, improving overall system security and regulatory compliance.

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
