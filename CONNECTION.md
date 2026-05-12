# Colossus — Connection & Development Workflow

## Where Does Each Action Run?

| Action | Where | Why |
|---|---|---|
| Code editing | **Local Mac** | Your editor, git, TS language server |
| `pnpm install` | **Local Mac** | IDE type-checking, linting, `@colossus/types` build |
| `expo prebuild` | **Local Mac** | Needs Xcode CLI tools to generate ios/ and android/ |
| `openssl rand -hex 32` (JWT key) | **Local Mac** | Then paste result into `.env` on the LXC |
| `cp .env.example .env` + fill values | **Colossus LXC** | `.env` must never leave the server |
| `docker compose up --build` | **Colossus LXC** | Docker daemon lives there |
| `alembic upgrade head` | **Colossus LXC** | Needs DB access inside the Docker network |
| `git push` | **Local Mac** → git remote | Triggers deploy via `make deploy` |

---

## Infrastructure

| Host | IP | SSH alias | What runs there |
|---|---|---|---|
| Proxmox | `10.0.0.41` | `proxmox` | Hypervisor — manages all LXC containers |
| YAMS | `10.0.0.243` | `yams` | Existing media stack — do not touch |
| Colossus LXC | `10.0.0.50` | `colossus` | VMID 108 — Docker host for all Colossus services |

> LXC provisioned. VMID 108, static IP `10.0.0.50`, MAC `BC:24:11:F7:22:D5`.

---

## SSH Setup (one-time, on your Mac)

Two hosts need SSH aliases: the **Proxmox hypervisor** (needed to create the
LXC) and the **Colossus LXC** itself (needed for all daily dev ops).

### 1 — Set up SSH to Proxmox

Proxmox's web UI is at `https://10.0.0.41:8006` but its CLI is available over
SSH. You may need to use a password the very first time:

```bash
# First time only — copies your Mac key to Proxmox (prompts for root password)
ssh-copy-id -i ~/.ssh/id_ed25519 root@10.0.0.41

# Verify key-based auth works
ssh root@10.0.0.41 'pveversion'
```

Then add the `proxmox` alias to `~/.ssh/config`:

```
Host proxmox
  HostName 10.0.0.41
  User root
  IdentityFile ~/.ssh/id_ed25519
  ControlMaster auto
  ControlPath ~/.ssh/cm-%r@%h:%p
  ControlPersist 10m
```

```bash
# Test the alias
ssh proxmox 'pveversion'
```

### 2 — Create the Colossus LXC (one command)

Pick an unused IP on your LAN. Based on your existing network, `10.0.0.50`
is a safe choice (your current static assignments are `.3`, `.4`, `.41`,
`.243`). The IP is assigned **statically inside the container config** —
there is no DHCP reservation needed and nothing to configure on your
Xfinity router.

```bash
make create-lxc COLOSSUS_IP=10.0.0.50
```

> ✅ **Done.** LXC created 2025, VMID 108, IP 10.0.0.50.

This will:
1. Upload `scripts/create-lxc.sh` to Proxmox via `scp`
2. Prompt you for a root password for the new LXC
3. Auto-download the Ubuntu 24.04 template if not cached
4. Create a privileged LXC with nesting enabled (required for Docker)
5. Assign `10.0.0.50` as a permanent static IP
6. **Inject your Mac's SSH key** from Proxmox's `authorized_keys` directly
   into the new LXC — so `ssh colossus` works immediately with no extra steps
7. Start the container

### 3 — Add the `colossus` alias to `~/.ssh/config`

Replace `10.0.0.XXX` with the IP you chose:

```
Host colossus
  HostName 10.0.0.50          # Colossus LXC (VMID 108)
  User root
  IdentityFile ~/.ssh/id_ed25519
  ControlMaster auto
  ControlPath ~/.ssh/cm-%r@%h:%p
  ControlPersist 10m
```

```bash
# Test — should print "connection ok" with no password prompt
ssh colossus 'echo "connection ok"'
```

### 4 — Bootstrap Docker and clone the repo

```bash
make bootstrap COLOSSUS_REPO_URL=git@github.com:you/colossus
```

This uploads `scripts/bootstrap-lxc.sh`, installs Docker CE on the LXC,
clones the repo to `~/colossus`, and copies `.env.example → .env`.

---

## Note on Xfinity DHCP reservations

You don't need one for this setup — the IP is baked into the container
config, not assigned by DHCP. However, if you ever need a DHCP reservation
for a different device (or want belt-and-suspenders protection against
IP collision), here's how on Xfinity:

1. Open a browser → `http://10.0.0.1` (your Xfinity gateway)
2. Log in (admin credentials printed on the side of the modem, or check
   the Xfinity app under **Account → My WiFi**)
3. Navigate to **Advanced → DHCP Reservation** (may also be under
   **Gateway → Connection → Local IP Network**)
4. Click **Add** — enter the device's MAC address and your chosen IP
5. Save and reboot the gateway if prompted

Alternatively: **Xfinity app → Connect → (your network) → See Network
→ Connected Devices → (device) → Assign Static IP**.

---

## Daily Dev Workflow

```
┌─ Local Mac ──────────────────────────────────────────────────────┐
│  1. Edit code in colossus/                                       │
│  2. git add . && git commit -m "feat: ..."                       │
│  3. git push                                                     │
│  4. make deploy          (git pull + docker compose up --build)  │
│  5. make logs-api        (tail FastAPI output)                   │
└──────────────────────────────────────────────────────────────────┘

┌─ Colossus LXC (automated via make) ──────────────────────────────┐
│  git pull                                                        │
│  docker compose up --build -d                                    │
└──────────────────────────────────────────────────────────────────┘
```

Run `make tunnel` to forward all service ports to localhost for direct
browser/curl testing without leaving your Mac:

| Forwarded port | Service |
|---|---|
| `localhost:8000` | FastAPI (`/health`, `/docs`) |
| `localhost:3000` | Next.js web |
| `localhost:9001` | MinIO console |
| `localhost:5432` | PostgreSQL (for DB GUIs like TablePlus) |

---

## Quick Reference

```bash
make deploy       # git pull on LXC + docker compose up --build -d
make logs         # follow all container logs
make logs-api     # follow colossus-api only
make logs-worker  # follow Celery worker only
make ps           # docker compose ps
make shell-api    # bash inside colossus-api container
make migrate      # alembic upgrade head
make tunnel       # SSH port-forward everything to localhost
make down         # docker compose down
make restart      # docker compose restart (no rebuild)
```

See `Makefile` at the repo root for the full list.
