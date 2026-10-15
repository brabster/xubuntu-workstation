# ADR 0002: Workstation sudo access and Cyber Essentials

- Status: Proposed — explicit maintainer approval required
- Date: 2026-10-15
- Related PR: [#103](https://github.com/brabster/xubuntu-workstation/pull/103)

## Context

This playbook targets a personal, single-user workstation. Its sudo setup removes the configured user from the general `sudo` group and sets the sudo timestamp timeout to zero (`roles/sudo/tasks/main.yml`). Other roles still grant that same user specific sudoers access:

- `roles/updates/tasks/main.yml` adds the user to `updaters` and permits passwordless sudo for the update script.
- `roles/cups/tasks/main.yml` adds the user to `cups_users` and permits starting and stopping CUPS with sudo. This role runs outside CI.
- `roles/next_install/tasks/main.yml` defines a sudoers grant for the USB setup scripts, but `next_install` is not included in `workstation.yml`; it is not applied by the main workstation playbook.

The bootstrap instructions also set a password for the separate root account. That does not remove the sudoers grants from the everyday user account.

## Cyber Essentials evidence

The NCSC's [Cyber Essentials Requirements for IT Infrastructure v3.3 (April 2026)](https://www.ncsc.gov.uk/files/cyber-essentials-requirements-for-it-infrastructure-v3-3.pdf), under **User Access Control — Separate administrative accounts**, says:

> “Your organisation must use separate accounts to perform administrative activities only (no emailing, web browsing or other standard user activities that may expose administrative privileges to avoidable risks).”

The standard does not prescribe Linux `sudo`, a particular group, or a specific sudoers syntax. Applying its account-separation requirement to this workstation is an interpretation: when the everyday account performs privileged operations through sudo, it is being used for administrative activity. The text does not distinguish unrestricted sudo from command-specific sudoers grants.

## Assessment

- **Is this setup compliant with the separate-account requirement?** No, not on the configuration shown here: the ordinary user account retains sudoers grants for administrative operations. Removing that user from the general `sudo` group and restricting the commands reduces the scope of privilege, but does not make the account separate from the everyday account.
- **Is a separate administrator account with no sudoers access for the everyday account better aligned?** Yes. Keep the everyday account unprivileged and use a distinct administrator account only for administrative activity. The separate admin account may itself use sudo; Cyber Essentials does not require that no account use sudo. “No sudoers access” should refer to the everyday account, not every administrator.
- **Does this alone establish overall Cyber Essentials compliance?** No. Compliance depends on the full in-scope environment and its actual use; this decision addresses only account separation. A certification body should be consulted if relying on command-specific delegation as an exception.

The Linux interpretation above is not a Linux-specific rule stated by the NCSC. The quoted wording and section heading were available in an indexed transcription, but the official PDF could not be retrieved during this research. Verify the exact wording and placement with NCSC or IASME before relying on it as certification evidence; no requirement number or page is cited because neither was verified.

## Decision requested

The maintainer must explicitly choose whether to retain this single-user command-whitelist model as a documented departure from the separate-account requirement, or to authorize a future change to use an unprivileged everyday account and a distinct administrator account. Until that approval is recorded, this assessment is proposed and the repository must not describe the current sudo setup as Cyber Essentials compliant.
