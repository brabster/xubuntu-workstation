You are an expert Ansible developer and a security champion tasked with implementing a new feature in the `xubuntu-workstation` repository. The goal is to enhance the existing ClamAV installation, which currently only provides manual scanning, into a robust, real-time antivirus solution.

### High-Level Objective
Modify the Ansible role responsible for workstation setup to configure ClamAV for on-access scanning of the user's `~/Downloads` directory.

### Core Requirements
1.  **Real-Time Monitoring**: Use the `clamav-daemon` service to actively monitor the `~/Downloads` directory.
2.  **Blocking Scan**: Employ the kernel's `fanotify` capability (`OnAccessPrevention`) to block any access to a newly created file until it has been scanned and cleared by ClamAV.
3.  **Quarantine Action**: If a virus is detected, the infected file must be immediately moved to a dedicated quarantine directory located at `~/Downloads/.quarantine/`.
4.  **User Notification**: Upon detecting and quarantining a file, a desktop notification must be sent to the user, clearly stating what was found and what action was taken.
5.  **System Stability**: Proactively tune kernel parameters to ensure the file watching service is stable and does not run out of resources.

### Implementation Plan

Please generate the Ansible tasks and corresponding file templates to execute the following plan. Assume the changes will be made within an existing Ansible role named `workstation`.

#### Step 1: Ensure Required Packages are Installed
In `roles/workstation/tasks/main.yml`, add a task to ensure the `clamav-daemon` package is installed using the `ansible.builtin.apt` module.

#### Step 2: Create a Templated `clamd.conf`
Create a new template file at `roles/workstation/templates/clamd.conf.j2`. This template should configure the ClamAV daemon. Key parameters must include:
```ini
# roles/workstation/templates/clamd.conf.j2
LogFile /var/log/clamav/clamav.log
PidFile /run/clamav/clamd.pid
LocalSocket /var/run/clamav/clamd.ctl
FixStaleSocket true
LocalSocketGroup clamav
LocalSocketMode 666
User clamav

ScanOnAccess yes
OnAccessIncludePath {{ ansible_user_dir }}/Downloads
OnAccessPrevention yes
OnAccessExtraScanning yes

# Action to take when a virus is found.
VirusEvent /usr/local/bin/clamav-quarantine.sh "%f"