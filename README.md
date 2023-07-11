Single-user Xubuntu setup: repeatable and demonstrable software installs and configuration.

**Target OS: Xubuntu 22.04 LTS** (see OS version in [GitHub actions](.github/workflows/test_install.yml))

## Usage

- `sudo su -` to start a root shell
- `passwd` to set a root password
- `wget https://raw.githubusercontent.com/brabster/xubuntu-workstation/main/bootstrap.sh && chmod 755 bootstrap.sh`
- Run `bootstrap.sh` as root.
- Follow instructions printed in script output to setup software and config.

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
