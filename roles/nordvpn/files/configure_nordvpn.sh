#!/bin/bash
set -euo pipefail

nordvpn set technology nordlynx
nordvpn set killswitch on
nordvpn set threatprotectionlite on
nordvpn set meshnet off
