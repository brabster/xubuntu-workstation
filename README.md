Single-user Xubuntu setup: repeatable and demonstrable software installs and configuration.

**Target OS: Xubuntu latest LTS and rolling** (see OS version in [GitHub actions](.github/workflows/test_install.yml))

## Support

**I provide no commitment to support your use of this repository and you use it at your own risk.**

This repository is for my own use and shared to inform and accelerate others.
I have placed it under the MIT licence for simplicity and permissiveness.
You are welcome to raise issues and submit pull requests but **I reserve the absolute right to refuse as I see fit**.

See [CHANGELOG.md](./CHANGELOG.md) for summaries of changes and reasons.

## Supporting Materials

- [Show and Tell Video](https://www.youtube.com/watch?v=CyuGg4F850g)
- [Why I automated this (Feb 2024)](https://tempered.works/posts/2024-02-27-automated-laptop-build-intro/)
- [Living with this automated build (Mar 2024)](https://tempered.works/posts/2024-02-27-automated-laptop-build-intro/)

## Usage

Most convenient way is now a single autoinstall USB that handles OS install plus first-boot provisioning. Minimal Xubuntu distro expected.

The [next_install role](./roles/next_install) places these scripts in a non-user modifiable directory and grants sudo rights to execute them. Some safety checks are in place but user takes responsibility for any data loss that may occur.

NOTE: the setup ends by setting up NordVPN with some security-related settings. **The network killswitch will be OFF** and will need login to enable. Username/password not required, emailed one-time code option is available to login.

### Prepare variables once

- copy [.vars_example.yml](./.vars_example.yml) to `.vars.yml`
- set your `git_name`, `git_email`, `username`
- set `autoinstall_password_hash` using a Linux password hash, for example:
  - `openssl passwd -6`

### Create one autoinstall USB (primary path)

- wipes any existing USB content
- run:
  - `sudo setup_autoinstall_usb.sh <xubuntu_iso_url> <repo_root_dir> <target_usb_device>`
  - example:
    - `sudo setup_autoinstall_usb.sh https://cdimage.ubuntu.com/xubuntu/releases/24.04/release/xubuntu-24.04.2-desktop-amd64.iso ~/projects/xubuntu-workstation /dev/sdb`
- warning:
  - always verify the USB target with `lsblk` before writing, to avoid wiping the wrong disk

This command:
- downloads and verifies the ISO signature/checksum
- injects autoinstall seed files
- embeds this repo and `.vars.yml`
- writes a bootable autoinstall USB

### Install and auto-bootstrap

- boot from the autoinstall USB
- installer creates the configured user and installs base packages
- on first boot, a one-shot systemd service runs:
  - `ansible-playbook -i inventory workstation.yml`
- service logs to:
  - `/var/log/xubuntu-workstation-bootstrap.log`
- on success it creates marker file:
  - `/var/lib/xubuntu-workstation/bootstrap.done`
  - and disables itself

### Two-USB fallback (backup path only)

If autoinstall media is not suitable for your hardware/firmware, keep using the existing scripts:
- [setup_linux_usb.sh](./roles/next_install/files/setup_linux_usb.sh)
- [setup_ansible_usb.sh](./roles/next_install/files/setup_ansible_usb.sh)
- [bootstrap.sh](./bootstrap.sh)

### Smoke test

Numerous setup options cannot be checked in GitHub actions, as the VM is locked down, the container does not run systemd and the whole thing is headless. The build mainly checks that the Ansible playbook executes successfully and very basic things are working.

A test script is provided to run on the target machine after installation as the normal user account.

## Security

### OS install

- minimal install (minimise unneeded packages)
- encrypt HDD (optionally same password as user account)
- remove any packages that I know I don't need
- disable any services that I rarely need, add service-specific start/stop via sudoers

### ClamAV on-access scanning

This install uses **ClamAV** as its antivirus solution. [CHANGELOG](CHANGELOG.md#fixes-and-security-improvement-to-clamav-on-access-setup)

| Solution | Pros | Cons |
| :--- | :--- | :--- |
| **ClamAV** | ✅ Free and open-source.<br>✅ **Highest supply chain security** due to installation and verification via `apt`.<br>✅ Highly configurable and scriptable. | ❌ On-access scanning is complex to configure correctly.<br>❌ Lacks a central management GUI out of the box.<br>❌ May have lower detection rates for some threats vs. top commercial options. |
| **Bitdefender** | ✅ Excellent malware detection rates.<br>✅ Modern features like machine learning. | ❌ **Not available for individuals on Linux**; requires a business registration.<br>❌ Opaque software supply chain (direct download). |
| **ESET** | ✅ Good detection rates from a reputable vendor.<br>✅ Standalone product available for Linux desktops. | ❌ Paid product.<br>❌ **Weak software supply chain**; the direct website download puts the verification burden on the user. |
| **Sophos** | ✅ Reputable security vendor. | ❌ **No longer offers a standalone/home product for Linux**; it's now part of their business platform.<br>❌ Opaque software supply chain (direct download). |


### Playbook
- [sudo](roles/sudo) remove sudo timeout - you need to put your password in each time
- [sudo](roles/sudo) restrict sudo commands to essential tasks
    - applying updates,
    - preparing installation media for the next update
    - temporarily starting and stopping rarely-needed services
- [clamav](roles/clamav) install clamav and freshclam, add custom context menu to scan in Thunar file manager, notes versions and signature update version/date in update script
- [updates](roles/updates)
    - update all known supply chains, incl. OS, firmware, snap, pip, clamav
    - apply system-level updates as root
    - su to user to apply user updates
- [firefox](roles/firefox), [chrome](roles/chrome-browser) apply security settings by policy

## Testing

[GitHub actions](.github/workflows) runs playbook on a container of the same OS as target. Tasks requiring a graphical target or systemd interaction (snap, systemctl) cannot be tested in a container.
