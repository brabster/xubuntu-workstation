# Xubuntu Workstation Automation

Xubuntu-workstation is an Ansible-based automated security configuration system for single-user Xubuntu workstations. It implements UK Cyber Essentials compliance through modular roles that configure security, development tools, and productivity applications.

**ALWAYS reference these instructions first** and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Prerequisites and Setup
- **CRITICAL**: Run these commands in order. **NEVER CANCEL** any build or test command - they may take 10+ minutes.
- Bootstrap dependencies:
  - `sudo apt-get update && sudo apt-get -y install git ansible`
  - `pip install ansible-lint` (for validation)
- Setup required configuration:
  - `cp .github/test_vars.yml .vars.yml` (use example vars for testing)
  - Modify `.vars.yml` with proper `git_name`, `git_email`, and `username` values

### Build and Test Process
- **Syntax validation**:
  - `ansible-playbook --syntax-check workstation.yml` -- takes 2 seconds
  - **NOTE**: ansible-lint requires internet access and may fail in restricted environments
- **Dry run (check mode)**:
  - `ansible-playbook -i inventory workstation.yml --check --diff` -- takes 5-10 minutes. **NEVER CANCEL**. Set timeout to 15+ minutes.
  - This shows what changes *would* be made without actually making them
- **Full execution**:
  - `ansible-playbook -i inventory workstation.yml` -- takes 15-30 minutes. **NEVER CANCEL**. Set timeout to 45+ minutes.
  - **WARNING**: Full execution modifies system configuration and requires root privileges

### Testing and Validation
- **Post-installation validation**:
  - `./test.sh` -- takes 2-5 minutes. Validates security configurations, service states, and functionality.
  - **MANUAL VALIDATION REQUIRED**: After running playbook, verify at least:
    1. `sudo update` works (passwordless updates)
    2. `clamscan --version` returns version info
    3. UFW firewall is active: `sudo ufw status`
    4. Git configuration: `git config --list | grep user`

### CI Environment Behavior
- Set `CI=true` environment variable to simulate GitHub Actions environment
- Many roles are **automatically skipped** in CI due to `when: not is_gh_actions` guards
- Roles that run in CI: networking, sudo, cleanup, updates, dev, chrome-browser, git, clamav
- Roles that **skip** in CI: cleanup_services, slack, vscode, xfce, cups, clipboard, ufw, nordvpn

## Repository Structure and Navigation

### Key Files and Directories
```
workstation.yml          # Main Ansible playbook - orchestrates all roles
bootstrap.sh            # Initial setup script (run as root)
test.sh                 # Post-installation validation script
inventory              # Ansible inventory (localhost only)
.vars.yml              # User-specific configuration (git config, username)
vars.yml               # Global variables and paths
roles/                 # Modular Ansible roles (see Role Architecture below)
.github/workflows/     # CI pipeline configuration
```

### Role Architecture
Roles are located in `roles/` directory. Each role handles a specific area:

**Core Security Roles:**
- `networking/` - DNS configuration (Cloudflare for Families)
- `sudo/` - Restrict sudo access and timeout policies
- `ufw/` - Firewall configuration (skipped in CI)
- `clamav/` - Antivirus installation and on-access scanning

**System Configuration:**
- `cleanup/` - Remove unnecessary packages
- `cleanup_services/` - Disable unused services (ModemManager, avahi)
- `updates/` - Automated update scripts with proper privileges

**Development Tools:**
- `dev/` - Development packages and Python virtual environment setup
- `git/` - Git configuration and aliases
- `vscode/` - Visual Studio Code installation (skipped in CI)

**Applications:**
- `chrome-browser/` - Google Chrome with security policies
- `firefox/` - Firefox with security configuration
- `slack/` - Slack installation (skipped in CI)
- `nordvpn/` - NordVPN client setup (skipped in CI, runs last)

### Common Commands and Expected Timing
- `ansible-playbook --syntax-check workstation.yml`: **2 seconds**
- `ansible-playbook -i inventory workstation.yml --check --diff`: **5-10 minutes** - NEVER CANCEL, set 15+ minute timeout
- `ansible-playbook -i inventory workstation.yml`: **15-30 minutes** - NEVER CANCEL, set 45+ minute timeout  
- `./test.sh`: **2-5 minutes** - validates system configuration
- `sudo ./bootstrap.sh`: **20-40 minutes** - full bootstrap from scratch

## Validation Scenarios

### Always Test After Changes
1. **Syntax validation**: Run `ansible-playbook --syntax-check workstation.yml`
2. **Dry run test**: Run `ansible-playbook -i inventory workstation.yml --check --diff`
3. **Role-specific testing**: Use `--tags <role_name>` to test specific roles
4. **Manual verification scenarios**:
   - Verify passwordless updates: `sudo update` should work without password
   - Verify git configuration: Check `.gitconfig` has correct user name/email
   - Verify security: `sudo ufw status` should show active firewall (not in CI)
   - Verify antivirus: `clamscan --version` should return version

### CI Validation
- GitHub Actions runs on `ubuntu:latest` and `ubuntu:rolling`
- CI environment automatically detected via `is_gh_actions` variable
- **Expected CI timing**: Full CI run takes 5-15 minutes
- CI validates syntax, basic role execution, and core functionality only

## Important Constraints and Limitations

### System Requirements
- **Target OS**: Xubuntu latest LTS or rolling release
- **Single-user system**: Designed for individual workstations, not multi-user servers
- **Network access required**: For package installation and updates
- **Root privileges required**: Most roles modify system-level configuration

### CI/CD Limitations
- **Container restrictions**: CI runs in Docker containers without systemd
- **No GUI testing**: Desktop environment roles cannot be fully tested in CI
- **Service limitations**: Cannot test service start/stop/enable operations in CI
- **Network restrictions**: Some external package sources may be blocked

### Security Considerations
- **UK Cyber Essentials compliance**: All security configurations reference this framework
- **Sudo restrictions**: After installation, sudo access is limited to essential operations only
- **Network security**: Firewall enabled by default, secure DNS configured
- **Antivirus**: ClamAV configured with on-access scanning (can be disabled via vars)

## Debugging and Troubleshooting

### Common Issues
- **"Group does not exist" error**: This occurs in check mode due to race conditions in group creation
- **Permission errors with user switching**: Some roles require proper user context setup
- **CI vs local execution differences**: Use `CI=true` to test CI-compatible execution locally
- **Missing variables**: Ensure `.vars.yml` is properly configured with all required variables

### Diagnostic Commands
- Check Ansible version: `ansible --version`
- List available tags: `ansible-playbook --list-tags workstation.yml`
- Run specific role: `ansible-playbook -i inventory workstation.yml --tags <role_name>`
- Verbose output: Add `-vvv` flag for detailed execution logs

### Recovery and Cleanup
- **Reset sudo configuration**: Edit `/etc/sudoers` manually if locked out
- **Disable firewall**: `sudo ufw disable` if network access is blocked
- **Check service status**: `systemctl status <service>` for service-related issues
- **Log locations**: Check `/var/log/` for system service logs, especially ClamAV logs

## Key Project Insights
- This is a **personal security automation project** - treat changes carefully
- **Compliance-driven design** - security choices are based on UK Cyber Essentials requirements
- **Guard pattern usage** - Many roles use `when: not is_gh_actions` to prevent CI execution
- **Modular architecture** - Each role is independent and can be run separately
- **Timing-critical operations** - Never cancel long-running builds or installations