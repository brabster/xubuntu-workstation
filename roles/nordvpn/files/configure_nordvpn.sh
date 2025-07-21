#!/bin/bash
set -euo pipefail

nordvpn set killswitch on
nordvpn set threatprotectionlite on

# already the default, setting a value to same value returns status code 1
# nordvpn set technology nordlynx
# nordvpn set meshnet off
