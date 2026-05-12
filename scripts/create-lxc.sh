#!/usr/bin/env bash
# =============================================================================
# create-lxc.sh — Creates the Colossus LXC on the Proxmox host
#
# THIS SCRIPT RUNS ON THE PROXMOX HOST (10.0.0.41).
# The Makefile uploads and executes it automatically:
#
#   make create-lxc COLOSSUS_IP=10.0.0.50
#
# Required env var:
#   COLOSSUS_IP   — the static LAN IP to permanently assign (e.g. 10.0.0.50)
#
# Optional env vars:
#   COLOSSUS_GW   — LAN gateway IP (default: 10.0.0.1, your Xfinity router)
#   COLOSSUS_VMID — override VMID (default: next available, auto-detected)
#   COLOSSUS_PW   — LXC root password (will prompt interactively if not set)
# =============================================================================

set -euo pipefail

# ── Config (all overridable via env) ──────────────────────────────────────────
LXC_IP="${COLOSSUS_IP:?Error: COLOSSUS_IP is required. e.g. COLOSSUS_IP=10.0.0.50}"
LXC_GW="${COLOSSUS_GW:-10.0.0.1}"
LXC_HOSTNAME="colossus"
LXC_CORES=4
LXC_RAM=8192       # MB
LXC_SWAP=512       # MB
LXC_DISK=60        # GB
LXC_BRIDGE="vmbr0"

# ── Colour helpers ────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BOLD='\033[1m'; NC='\033[0m'
info()  { echo -e "${GREEN}[create-lxc]${NC} $*"; }
warn()  { echo -e "${YELLOW}[create-lxc]${NC} $*"; }
error() { echo -e "${RED}[create-lxc]${NC} $*" >&2; exit 1; }

# ── Sanity checks ─────────────────────────────────────────────────────────────
command -v pct    &>/dev/null || error "pct not found — this script must run on the Proxmox host."
command -v pvesm  &>/dev/null || error "pvesm not found — this script must run on the Proxmox host."
command -v pveam  &>/dev/null || error "pveam not found — this script must run on the Proxmox host."

# Basic IP format check
[[ "${LXC_IP}" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] \
  || error "COLOSSUS_IP '${LXC_IP}' does not look like a valid IPv4 address."

# Warn if IP is already reachable on the network
if ping -c1 -W1 "${LXC_IP}" &>/dev/null 2>&1; then
  if [[ -t 0 ]]; then
    warn "WARNING: ${LXC_IP} is already responding to ping."
    read -rp "Continue anyway? [y/N] " CONFIRM
    [[ "${CONFIRM,,}" == "y" ]] || exit 1
  else
    error "${LXC_IP} is already responding to ping. Choose a different IP."
  fi
fi

# ── Root password ─────────────────────────────────────────────────────────────
if [[ -z "${COLOSSUS_PW:-}" ]]; then
  if [[ ! -t 0 ]]; then
    error "COLOSSUS_PW must be set when running non-interactively (no TTY detected)."
  fi
  echo -e "${GREEN}[create-lxc]${NC} Set a root password for the new Colossus LXC container:"
  read -rsp "  Password: " LXC_PW; echo
  read -rsp "  Confirm:  " LXC_PW2; echo
  [[ "${LXC_PW}" == "${LXC_PW2}" ]] || error "Passwords do not match."
else
  LXC_PW="${COLOSSUS_PW}"
  info "Using COLOSSUS_PW from environment."
fi

# ── VMID ──────────────────────────────────────────────────────────────────────
if [[ -n "${COLOSSUS_VMID:-}" ]]; then
  VMID="${COLOSSUS_VMID}"
  info "Using specified VMID: ${VMID}"
else
  VMID=$(pvesh get /cluster/nextid)
  info "Auto-selected VMID: ${VMID}"
fi

# ── Storage ───────────────────────────────────────────────────────────────────
# Order of preference: local-lvm (LVM-thin) > local (dir) > first available
info "Available storage pools:"
pvesm status | awk 'NR>1 {printf "  %-20s %s\n", $1, $2}'

if pvesm status | awk 'NR>1 {print $1}' | grep -qx 'local-lvm'; then
  STORAGE="local-lvm"
elif pvesm status | awk 'NR>1 {print $1}' | grep -qx 'local'; then
  STORAGE="local"
else
  STORAGE=$(pvesm status | awk 'NR==2 {print $1}')
  warn "Neither 'local-lvm' nor 'local' found — using first available: ${STORAGE}"
fi
info "Selected storage: ${STORAGE}"

# ── Ubuntu 24.04 template ─────────────────────────────────────────────────────
info "Refreshing Proxmox template index..."
pveam update 2>/dev/null || warn "pveam update failed (network?). Proceeding with cached list."

TEMPLATE_NAME=$(pveam available --section system 2>/dev/null \
  | awk '{print $2}' \
  | grep 'ubuntu-24.04' \
  | sort -V \
  | tail -1)

[[ -n "${TEMPLATE_NAME}" ]] \
  || error "No ubuntu-24.04 template found. Check: pveam available --section system"
info "Template: ${TEMPLATE_NAME}"

# Download template if not already local
if pveam list local 2>/dev/null | grep -q "${TEMPLATE_NAME}"; then
  info "Template already cached on this host."
else
  info "Downloading template (this takes 1-2 minutes on first run)..."
  pveam download local "${TEMPLATE_NAME}"
fi

# ── SSH key injection ─────────────────────────────────────────────────────────
# If your Mac's public key is already in Proxmox root's authorized_keys
# (which it will be after `ssh-copy-id`), it gets injected into the LXC.
# This means `ssh colossus` works immediately after creation — no extra steps.
SSH_KEY_ARG=""
if [[ -f /root/.ssh/authorized_keys ]] && [[ -s /root/.ssh/authorized_keys ]]; then
  KEY_COUNT=$(wc -l < /root/.ssh/authorized_keys)
  info "Found ${KEY_COUNT} SSH key(s) in /root/.ssh/authorized_keys — injecting into LXC."
  SSH_KEY_ARG="--ssh-public-keys /root/.ssh/authorized_keys"
else
  warn "No keys found in /root/.ssh/authorized_keys."
  warn "After creation, run: ssh-copy-id -i ~/.ssh/id_ed25519 root@${LXC_IP}"
fi

# ── Create the container ──────────────────────────────────────────────────────
echo ""
info "Creating LXC container..."
echo "  VMID:      ${VMID}"
echo "  Hostname:  ${LXC_HOSTNAME}"
echo "  IP:        ${LXC_IP}/24  (static, permanent)"
echo "  Gateway:   ${LXC_GW}"
echo "  CPU:       ${LXC_CORES} cores"
echo "  RAM:       ${LXC_RAM} MB"
echo "  Disk:      ${LXC_DISK} GB  (${STORAGE})"
echo "  Nesting:   enabled  (required for Docker)"
echo ""

# shellcheck disable=SC2086
pct create "${VMID}" "local:vztmpl/${TEMPLATE_NAME}" \
  --hostname     "${LXC_HOSTNAME}"                              \
  --cores        "${LXC_CORES}"                                 \
  --memory       "${LXC_RAM}"                                   \
  --swap         "${LXC_SWAP}"                                  \
  --rootfs       "${STORAGE}:${LXC_DISK}"                       \
  --net0         "name=eth0,bridge=${LXC_BRIDGE},ip=${LXC_IP}/24,gw=${LXC_GW},firewall=0" \
  --unprivileged 0                                              \
  --features     "nesting=1"                                    \
  --ostype       ubuntu                                         \
  --password     "${LXC_PW}"                                    \
  --onboot       1                                              \
  ${SSH_KEY_ARG}

# ── Start and verify ──────────────────────────────────────────────────────────
info "Starting container..."
pct start "${VMID}"

info "Waiting for container to boot..."
sleep 5

STATUS=$(pct status "${VMID}" | awk '{print $2}')
MAC=$(pct config "${VMID}" | grep 'net0:' | grep -oE '([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}' | head -1)

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}  ✓ Colossus LXC created successfully${NC}"
echo ""
echo "  ┌──────────────────────────────────────────────┐"
printf "  │  %-44s│\n" "VMID:       ${VMID}"
printf "  │  %-44s│\n" "Hostname:   ${LXC_HOSTNAME}"
printf "  │  %-44s│\n" "IP (static): ${LXC_IP}/24"
printf "  │  %-44s│\n" "Gateway:    ${LXC_GW}"
printf "  │  %-44s│\n" "MAC:        ${MAC}"
printf "  │  %-44s│\n" "Status:     ${STATUS}"
echo "  └──────────────────────────────────────────────┘"
echo ""
echo "  Back on your Mac:"
echo ""
echo "  1. Update ~/.ssh/config:   HostName ${LXC_IP}"
echo "  2. Update CONNECTION.md:   10.0.0.XXX → ${LXC_IP}"
if [[ -n "${SSH_KEY_ARG}" ]]; then
echo "  3. Test SSH (key already injected):"
echo "       ssh colossus 'echo ok'"
else
echo "  3. Copy your SSH key:"
echo "       ssh-copy-id -i ~/.ssh/id_ed25519 root@${LXC_IP}"
echo "       ssh colossus 'echo ok'"
fi
echo "  4. Bootstrap Docker + clone repo:"
echo "       COLOSSUS_REPO_URL=<git-url> make bootstrap"
echo ""
