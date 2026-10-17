# Xubuntu workstation setup

This repository automates the setup and maintenance of a personal, single-user Xubuntu workstation with Ansible. It is tailored to my own use; review the playbook and variables before using it on another machine.

**Target OS: Xubuntu latest LTS and rolling.** CI checks the playbook in `ubuntu:latest` and `ubuntu:rolling` containers; it does not test a graphical Xubuntu desktop.

The playbook configures networking, sudo, system and user updates, development tools, Chrome, Git, ClamAV, Slack, Visual Studio Code, and (outside CI) desktop settings, CUPS, clipboard clearing, UFW, and NordVPN.

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

Use a minimal Xubuntu install, a bootable USB for the Xubuntu installer, and a separate USB for this repository. The setup scripts erase their target USB device, so check the device path carefully before running them.

The [next_install role](./roles/next_install) installs the USB setup scripts in a non-user-modifiable directory and grants the `install_users` group permission to run them. The scripts check that the target is a USB device, but this does not prevent data loss if the wrong device is selected.

The setup ends by configuring NordVPN. **Its network killswitch is OFF** until you log in and enable it. NordVPN supports login with an emailed one-time code.

### Setup Distro USB

- wipes any existing USB content
- run `sudo setup_linux_usb.sh iso_image_path target_usb_device` (for example, `sudo setup_linux_usb.sh ~/Downloads/xubuntu.iso /dev/sdX`)

### Create Bootstrap USB

- wipes any existing USB content
- use [.vars_example.yml](./.vars_example.yml) to create a file .vars.yml with appropriate settings
- optionally edit [workstation.yml](./workstation.yml) to customise this install
- run `sudo setup_ansible_usb.sh repo_root_dir target_usb_device` (for example, `sudo setup_ansible_usb.sh ~/projects/xubuntu-workstation /dev/sdX`)

### Install Xubuntu

- insert bootable USB
- interrupt boot process, set USB as temp boot device
- install distro
    - can connect to network now or in bootstrap
    - use LVM/encrypt HDD
    - as this is a single-user device, can use same strong password for disk encryption as for login - one stronger better than two weaker
- allow reboot
- remove USB
- boot, decrypt and log in

### Bootstrap

- insert bootstrap USB
- mount, open terminal in directory
- `sudo su -` to start a root shell (you will lose ability to `sudo` arbitrarily as part of install to meet Cyber Essentials regulations)
- `passwd` to set a root password
- `cd` back to the mount directory
- ensure connected to network for updates and installs
- `./bootstrap.sh`
- log out and back in to activate the XFCE keyboard shortcut and Whisker Menu changes

### Smoke test

The `xfce_desktop` CI workflow tests the XFCE tasks separately on an authenticated
Xvfb display with a disposable user, real XFWM4/settings daemons, and a panel
running Whisker Menu. It sends Super+Arrow key events and checks window geometry,
checks that Ctrl+F2 opens the launcher, and verifies restart persistence,
preservation of unrelated shortcuts, and idempotence for fresh and existing
profiles. A deliberately incorrect binding must fail the geometry check.
Desktop and Ansible logs are uploaded as CI artifacts; package versions appear
in the job log. Focused unit tests also cover the live-session updater.

This tests the Ubuntu runner's packaged X11 desktop, not an exact Xubuntu image,
physical keyboard, GPU, display-manager login/logout, multi-monitor setup, or
Wayland session. The tested Whisker 2.8 package migrates rc settings into xfconf;
the test verifies that migration but cannot demonstrate that `button-trigger=0`
disables the originally reported Super-key grab. The desktop restart checks
reload and persistence but do not replace a full login/logout test.

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
- [chrome](roles/chrome_browser) applies security settings by policy

## Testing

CI runs the playbook in Ubuntu containers. It checks that Ansible tasks execute, but cannot cover tasks that need a graphical desktop or systemd.

After installation, log out and back in, then run `./test.sh` as the normal user to check behavior on the target machine.

For local Ansible linting, install dev dependencies and enable the repository git hooks:

- `python3 -m pip install -r requirements-dev.txt`
- `git config core.hooksPath .githooks`

CI also runs `ansible-lint` on the playbooks and roles before merge.

Contributor and agent steering for this repository lives in [AGENTS.md](./AGENTS.md) and the versioned wiki under [docs/wiki/](./docs/wiki/).
