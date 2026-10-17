# ADR 0002: Workstation update privileges and Cyber Essentials

- Status: Proposed — update execution model changed; Cyber Essentials interpretation remains unconfirmed
- Date: 2026-10-15
- Related PR: [#103](https://github.com/brabster/xubuntu-workstation/pull/103)

## Context

This playbook targets a personal, single-user workstation. The configured everyday user is removed from the general `sudo` group and sudo's timestamp timeout is zero (`roles/sudo/tasks/main.yml`). The update role removes the legacy `updaters` grant and membership, and runs the root-owned update script from a systemd timer shortly after boot and hourly (`roles/updates/tasks/main.yml` and `roles/updates/templates/`).

- `roles/cups/tasks/main.yml` stops and disables CUPS and removes the legacy `cups_users` sudoers rule and group membership.
- `roles/next_install/tasks/main.yml` defines an `install_users` sudoers grant for two USB setup scripts, but `next_install` is not included in `workstation.yml`; that rule is not installed by the main workstation playbook.

The timer starts updates shortly after boot and repeats hourly while the machine is on. The service runs as root without an interactive user session. Its command output and timestamped completion result are recorded in a user-readable log. A failed service remains failed until the next hourly timer activation retries it. A desktop-session monitor notifies the user of failed runs or no successful run in 26 hours. This is a change to the update execution model, not a claim that unattended system services satisfy any particular CE account-separation interpretation.

## Cyber Essentials evidence

The NCSC's [Cyber Essentials Requirements for IT Infrastructure v3.3 (April 2026)](https://www.ncsc.gov.uk/files/cyber-essentials-requirements-for-it-infrastructure-v3-3.pdf), under **User Access Control — Separate administrative accounts**, says:

> “Your organisation must use separate accounts to perform administrative activities only (no emailing, web browsing or other standard user activities that may expose administrative privileges to avoidable risks).”

The standard does not prescribe Linux `sudo`, a particular group, or a specific sudoers syntax. Applying its account-separation requirement to this workstation is an interpretation: when the everyday account performs privileged operations through sudo, it is being used for administrative activity. The text does not distinguish unrestricted sudo from command-specific sudoers grants.

## Assessment

- **Does the daily system service resolve the account-separation question?** It removes the everyday user's direct sudo invocation of the update operation, but whether unattended root services satisfy the relevant CE requirement is not established by the source reviewed here.
- **Is a separate administrator account with no sudoers access for the everyday account better aligned?** It remains the clearest human account-separation arrangement. A root-owned system service is a different execution model and needs direct assessor interpretation before making a compliance claim.
- **Are other sudoers grants configured by the main workstation playbook?** The update and CUPS role grants are removed. The `next_install` role still defines `install_users` access for two root-installed USB setup scripts, but it is not invoked in `workstation.yml`. Confirm whether that separate install workflow is used on the target before considering its grant in an audit.
- **Does this alone establish overall Cyber Essentials compliance?** No. Compliance depends on the full in-scope environment and its actual use; this decision addresses only account separation. A certification body should be consulted if relying on command-specific delegation as an exception.

The Linux interpretation above is not a Linux-specific rule stated by the NCSC. The quoted wording and section heading were available in an indexed transcription, but the official PDF could not be retrieved during this research. Verify the exact wording and placement with NCSC or IASME before relying on it as certification evidence; no requirement number or page is cited because neither was verified.

## Decision requested

The update execution model has been changed to a root systemd service. Confirm with IASME or the certification body whether this satisfies account separation, and separately assess the remaining CUPS sudo grant, before describing the workstation as Cyber Essentials compliant.
