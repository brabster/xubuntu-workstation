Single-user Xubuntu setup: repeatable and demonstrable software installs and configuration.

**Target OS: Xubuntu 22.04 LTS** (see OS version in [GitHub actions](.github/workflows/test_install.yml))

## Usage

Most convenient way to do this is to create a bootable USB for the xubuntu distro, and a separate non-bootable USB from this repo. Minimal Xubuntu distro expected.

### Setup Distro USB

- requires root permissions to write the USB device
- wipes any existing USB content
- run [setup_bootable_linux_usb.sh](./setup_bootable_linux_usb.sh)

### Create Bootstrap USB

- requires root permissions to write the USB device
- wipes any existing USB content
- use [vars_example.yml](./vars_example.yml) to create a file .vars.yml with appropriate settings
- run [setup_bootstrap_ansible_usb.sh](./setup_bootstrap_ansible_usb.sh)

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


## Security

### OS install:
- minimal install (minimise unneeded packages)
- encrypt HDD (optionally same password as user account)

### Playbook
- [sudo](roles/sudo) remove sudo timeout - you need to put your password in each time
- [sudo](roles/sudo) restrict sudo commands to only applying updates
- [updates](roles/updates)
    - update all known supply chains, incl. OS, firmware, snap, pip
    - apply system-level updates as root
    - su to user to apply user updates
- [firefox](roles/firefox), [chrome](roles/chrome-browser) apply security settings by policy
- [expressvpn](roles/expressvpn) install VPN
- [clamav](roles/clamav) install clamav and freshclam, add custom context menu to scan in Thunar file manager, notes versions and signature update version/date in update script

## Testing

[GitHub actions](.github/workflows) runs playbook on a container of the same OS as target. Tasks requiring a graphical target or container management not easily exercised this way.
