# ─── Colossus Makefile ────────────────────────────────────────────────────────
# Usage: make <target>
# Remote targets run on the Colossus LXC via SSH.
# See CONNECTION.md for SSH setup.

# SSH alias for the Proxmox host (10.0.0.41)
PROXMOX := proxmox
# SSH alias for the Colossus LXC
REMOTE := colossus
# Repo path on the LXC
REMOTE_DIR := ~/colossus
# LAN gateway (Xfinity router)
COLOSSUS_GW := 10.0.0.1
COMPOSE := docker compose
API_CONT := colossus-api
WORKER_CONT := colossus-worker

.DEFAULT_GOAL := help

# ─── Help ─────────────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "  Colossus — available targets"
	@echo ""
	@echo "  LOCAL ──────────────────────────────────────────────────────"
	@echo "  install        pnpm install (local node_modules)"
	@echo "  types-build    build @colossus/types (needed before web/mobile type-check)"
	@echo "  type-check     tsc --noEmit across all packages"
	@echo "  prebuild       expo prebuild --clean (generates ios/ android/)"
	@echo "  jwt-secret     generate a 32-byte hex JWT secret"
	@echo ""
	@echo "  REMOTE (Colossus LXC) ──────────────────────────────────────"
	@echo "  deploy         git pull + docker compose up --build -d"
	@echo "  up             docker compose up -d (no rebuild)"
	@echo "  down           docker compose down"
	@echo "  restart        docker compose restart (no rebuild)"
	@echo "  ps             docker compose ps"
	@echo "  logs           follow all container logs"
	@echo "  logs-api       follow colossus-api logs"
	@echo "  logs-web       follow colossus-web logs"
	@echo "  logs-worker    follow Celery worker logs"
	@echo "  logs-db        follow Postgres logs"
	@echo "  shell-api      bash inside colossus-api container"
	@echo "  shell-db       psql inside colossus-db container"
	@echo "  migrate        alembic upgrade head"
	@echo "  migrate-new    create new autogenerate migration (MSG= required)"
	@echo "  migrate-down   alembic downgrade -1"
	@echo "  migrate-history alembic history"
	@echo ""
	@echo "  TUNNEL ─────────────────────────────────────────────────────"
	@echo "  tunnel         SSH port-forward all services to localhost"
	@echo ""
	@echo "  PROXMOX (one-time infrastructure setup) ───────────────────"
	@echo "  create-lxc     create Colossus LXC on Proxmox (COLOSSUS_IP= required)"
	@echo "                   example: make create-lxc COLOSSUS_IP=10.0.0.50"
	@echo "  bootstrap      install Docker + clone repo on the LXC"
	@echo "                   example: make bootstrap COLOSSUS_REPO_URL=git@github.com:you/colossus"
	@echo "  ssh-proxmox    open an interactive SSH session to Proxmox host"
	@echo ""


# ─── Local targets ────────────────────────────────────────────────────────────
.PHONY: install
install:
	pnpm install

.PHONY: types-build
types-build:
	pnpm --filter @colossus/types build

.PHONY: type-check
type-check:
	pnpm turbo run type-check

.PHONY: prebuild
prebuild:
	cd apps/mobile && npx expo prebuild --clean

.PHONY: jwt-secret
jwt-secret:
	@echo "JWT_SECRET_KEY=$$(openssl rand -hex 32)"
	@echo ""
	@echo "  Copy the line above into your .env on the Colossus LXC."


# ─── Remote deploy ────────────────────────────────────────────────────────────
.PHONY: deploy
deploy:
	ssh $(REMOTE) 'cd $(REMOTE_DIR) && git pull && $(COMPOSE) up --build -d'

.PHONY: up
up:
	ssh $(REMOTE) 'cd $(REMOTE_DIR) && $(COMPOSE) up -d'

.PHONY: down
down:
	ssh $(REMOTE) 'cd $(REMOTE_DIR) && $(COMPOSE) down'

.PHONY: restart
restart:
	ssh $(REMOTE) 'cd $(REMOTE_DIR) && $(COMPOSE) restart'

.PHONY: ps
ps:
	ssh $(REMOTE) 'cd $(REMOTE_DIR) && $(COMPOSE) ps'


# ─── Remote logs ──────────────────────────────────────────────────────────────
.PHONY: logs
logs:
	ssh -t $(REMOTE) 'cd $(REMOTE_DIR) && $(COMPOSE) logs -f --tail=100'

.PHONY: logs-api
logs-api:
	ssh -t $(REMOTE) 'docker logs $(API_CONT) -f --tail=100'

.PHONY: logs-web
logs-web:
	ssh -t $(REMOTE) 'docker logs colossus-web -f --tail=100'

.PHONY: logs-worker
logs-worker:
	ssh -t $(REMOTE) 'docker logs $(WORKER_CONT) -f --tail=100'

.PHONY: logs-db
logs-db:
	ssh -t $(REMOTE) 'docker logs colossus-db -f --tail=100'


# ─── Remote shells ────────────────────────────────────────────────────────────
.PHONY: shell-api
shell-api:
	ssh -t $(REMOTE) 'docker exec -it $(API_CONT) bash'

.PHONY: shell-db
shell-db:
	ssh -t $(REMOTE) 'docker exec -it colossus-db psql -U colossus colossus'


# ─── Remote migrations ────────────────────────────────────────────────────────
.PHONY: migrate
migrate:
	ssh $(REMOTE) 'docker exec $(API_CONT) alembic upgrade head'

.PHONY: migrate-new
migrate-new:
ifndef MSG
	$(error MSG is required. Usage: make migrate-new MSG="add users table")
endif
	ssh $(REMOTE) 'docker exec $(API_CONT) alembic revision --autogenerate -m "$(MSG)"'
	@echo ""
	@echo "  Migration created on the LXC. Run the following to pull it back locally:"
	@echo "  scp '$(REMOTE):$(REMOTE_DIR)/apps/api/alembic/versions/*.py' apps/api/alembic/versions/"

.PHONY: migrate-down
migrate-down:
	ssh $(REMOTE) 'docker exec $(API_CONT) alembic downgrade -1'

.PHONY: migrate-history
migrate-history:
	ssh $(REMOTE) 'docker exec $(API_CONT) alembic history --verbose'


# ─── Proxmox infrastructure ──────────────────────────────────────────────────
.PHONY: create-lxc
create-lxc:
ifndef COLOSSUS_IP
	$(error COLOSSUS_IP is required. Usage: make create-lxc COLOSSUS_IP=10.0.0.50)
endif
	@echo "[make] Uploading create-lxc.sh to Proxmox..."
	scp scripts/create-lxc.sh $(PROXMOX):/tmp/colossus-create-lxc.sh
	@echo "[make] Executing on Proxmox..."
	ssh $(PROXMOX) "COLOSSUS_IP=$(COLOSSUS_IP) COLOSSUS_GW=$(COLOSSUS_GW) COLOSSUS_PW=$(COLOSSUS_PW) bash /tmp/colossus-create-lxc.sh"

.PHONY: bootstrap
bootstrap:
ifndef COLOSSUS_REPO_URL
	$(error COLOSSUS_REPO_URL is required. Usage: make bootstrap COLOSSUS_REPO_URL=git@github.com:you/colossus)
endif
	@echo "[make] Uploading bootstrap-lxc.sh to Colossus LXC..."
	scp scripts/bootstrap-lxc.sh $(REMOTE):/tmp/colossus-bootstrap.sh
	@echo "[make] Running bootstrap on LXC..."
	ssh -t $(REMOTE) "COLOSSUS_REPO_URL=$(COLOSSUS_REPO_URL) bash /tmp/colossus-bootstrap.sh"

.PHONY: ssh-proxmox
ssh-proxmox:
	ssh $(PROXMOX)


# ─── Tunnel (all ports → localhost) ───────────────────────────────────────────
.PHONY: tunnel
tunnel:
	@echo "Forwarding:"
	@echo "  localhost:8000  → colossus-api"
	@echo "  localhost:3000  → colossus-web"
	@echo "  localhost:9001  → MinIO console"
	@echo "  localhost:5432  → PostgreSQL"
	@echo ""
	@echo "Press Ctrl-C to close the tunnel."
	ssh -N \
	  -L 8000:localhost:8000 \
	  -L 3000:localhost:3000 \
	  -L 9001:localhost:9001 \
	  -L 5432:localhost:5432 \
	  $(REMOTE)
