#!/usr/bin/env bash
# =============================================================================
# bootstrap-lxc.sh — First-time setup for the Colossus LXC
#
# Run this ONCE on a fresh Ubuntu 24.04 LXC (as root).
# Installs: Docker CE, git, nano, and clones the repo.
#
# Usage from your Mac (after ssh-copy-id):
#   ssh colossus 'bash -s' < scripts/bootstrap-lxc.sh
#
# Or set COLOSSUS_REPO_URL before running:
#   COLOSSUS_REPO_URL=git@github.com:you/colossus.git \
#     ssh colossus 'bash -s' < scripts/bootstrap-lxc.sh
# =============================================================================

set -euo pipefail

REPO_URL="${COLOSSUS_REPO_URL:-}"
REPO_DIR="${HOME}/colossus"
GIT_BRANCH="${COLOSSUS_BRANCH:-main}"

# ── Colour output ──────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[bootstrap]${NC} $*"; }
warn()  { echo -e "${YELLOW}[bootstrap]${NC} $*"; }
error() { echo -e "${RED}[bootstrap]${NC} $*" >&2; exit 1; }

# ── Require root ───────────────────────────────────────────────────────────────
[[ "${EUID}" -eq 0 ]] || error "This script must be run as root."

# ── System packages ───────────────────────────────────────────────────────────
info "Updating apt and installing prerequisites..."
apt-get update -qq
apt-get install -y -qq \
  ca-certificates \
  curl \
  git \
  gnupg \
  lsb-release \
  nano \
  unzip

# ── Docker CE ─────────────────────────────────────────────────────────────────
if command -v docker &>/dev/null; then
  info "Docker already installed: $(docker --version)"
else
  info "Installing Docker CE..."
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg

  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" \
    > /etc/apt/sources.list.d/docker.list

  apt-get update -qq
  apt-get install -y -qq \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

  systemctl enable --now docker
  info "Docker installed: $(docker --version)"
fi

# ── Clone repo ────────────────────────────────────────────────────────────────
if [[ -z "${REPO_URL}" ]]; then
  warn "COLOSSUS_REPO_URL is not set. Skipping git clone."
  warn "After setting your git remote, run:"
  warn "  git clone <url> ${REPO_DIR} && cd ${REPO_DIR} && cp .env.example .env"
else
  if [[ -d "${REPO_DIR}/.git" ]]; then
    info "Repo already cloned at ${REPO_DIR}, pulling latest..."
    git -C "${REPO_DIR}" pull origin "${GIT_BRANCH}"
  else
    info "Cloning ${REPO_URL} → ${REPO_DIR}..."
    git clone --branch "${GIT_BRANCH}" "${REPO_URL}" "${REPO_DIR}"
  fi
fi

# ── .env setup ────────────────────────────────────────────────────────────────
if [[ -d "${REPO_DIR}" && ! -f "${REPO_DIR}/.env" ]]; then
  info "Copying .env.example → .env (edit before running docker compose)..."
  cp "${REPO_DIR}/.env.example" "${REPO_DIR}/.env"
  warn "IMPORTANT: Edit ${REPO_DIR}/.env and set real passwords before continuing."
  warn "  Minimum required edits:"
  warn "    POSTGRES_PASSWORD=<strong-password>"
  warn "    MINIO_PASSWORD=<strong-password>"
  warn "    JWT_SECRET_KEY=<output of: openssl rand -hex 32>"
fi

# ── Docker permissions ────────────────────────────────────────────────────────
# (Not strictly needed when running as root, but good if you add a non-root user later)
# usermod -aG docker <your-user>

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
info "Bootstrap complete. Next steps:"
echo ""
echo "  1. Edit the .env file:"
echo "     nano ${REPO_DIR}/.env"
echo ""
echo "  2. Start all services:"
echo "     cd ${REPO_DIR} && docker compose up --build -d"
echo ""
echo "  3. Run the first DB migration (after colossus-api is running):"
echo "     docker exec colossus-api alembic upgrade head"
echo ""
echo "  4. Check the health endpoint:"
echo "     curl http://localhost:8000/health"
echo ""
