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

| Host | IP | What runs there |
|---|---|---|
| Proxmox | `10.0.0.41` | Hypervisor — create the Colossus LXC here |
| YAMS | `10.0.0.243` | Existing media stack — DO NOT put Colossus here |
| Colossus LXC | `10.0.0.XXX` | **Set this once the LXC is provisioned** |

> The Colossus LXC IP is assigned during Proxmox LXC creation. Update the
> `HostName` in `~/.ssh/config` (see below) and in this file once known.

---

## SSH Setup (one-time, on your Mac)

### 1 — Add the `colossus` host alias

Append to `~/.ssh/config`:

```
Host colossus
  HostName 10.0.0.XXX          # ← replace with real LXC IP
  User root
  IdentityFile ~/.ssh/id_ed25519
  ControlMaster auto
  ControlPath ~/.ssh/cm-%r@%h:%p
  ControlPersist 10m
```

`ControlMaster` + `ControlPersist` means the TCP connection is reused for 10
minutes — rapid `make deploy` + `make logs` cycles feel instant.

### 2 — Copy your key to the new LXC

```bash
# Run once after the LXC is booted
ssh-copy-id -i ~/.ssh/id_ed25519 root@10.0.0.XXX

# Verify
ssh colossus 'echo "connection ok"'
```

### 3 — Clone the repo on the LXC

```bash
ssh colossus
# Inside the LXC:
git clone <your-git-remote-url> ~/colossus
cd ~/colossus
cp .env.example .env
# Edit .env with real passwords before first `docker compose up`
```

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
