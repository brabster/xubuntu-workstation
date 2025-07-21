#!/bin/bash
set -euo pipefail

nordvpn set threatprotectionlite on

# already the default, setting a value to same value returns status code 1
# nordvpn set killswitch on # cannot have this on at end of install, unable to login without network access
# nordvpn set technology nordlynx
# nordvpn set meshnet off
