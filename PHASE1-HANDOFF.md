# Phase 1 Handoff Prompt — Exercise Library

Copy everything below into a new chat to kick off Phase 1.

---

## Prompt

I'm building **Colossus**, a self-hosted fitness tracker (FastAPI + Next.js + Celery + Postgres + Redis + MinIO). Phase 0 is complete — the full stack is deployed and running in a Proxmox LXC. I'm ready to start **Phase 1: Exercise Library**.

### What exists now

**Infrastructure (all healthy, deployed on Colossus LXC at `10.0.0.50`):**
- 6 Docker containers: `colossus-api`, `colossus-web`, `colossus-worker`, `colossus-db` (Postgres 16), `colossus-redis`, `colossus-minio`
- `https://colossus.french75.org` → Next.js (HTTP 200)
- `https://colossus-api.french75.org` → FastAPI (behind Cloudflare Access)
- Deploy workflow: edit locally → `git push` → `make deploy` (runs `git pull && docker compose up --build -d` on LXC via SSH)

**API scaffolding (`apps/api/`):**
- FastAPI app at `app/main.py` with a `/health` endpoint
- SQLAlchemy async engine + `Base` declarative base in `app/database.py`
- Pydantic settings in `app/config.py` (reads `POSTGRES_URL`, `REDIS_URL`, `MINIO_*`, `JWT_*` from env)
- Alembic configured for async migrations in `alembic/env.py`
- Celery worker in `app/worker.py` (no tasks yet)
- Empty `app/models/` and `app/routers/` packages

**Web scaffolding (`apps/web/`):**
- Next.js 14 (App Router) + Tailwind + React Query
- Placeholder landing page

**Shared types (`packages/types/`):**
- TypeScript interfaces: `User`, `Exercise`, `MuscleGroup`, `EquipmentType`, `HealthResponse`, `TokenPair`

### Phase 1 goal

Full exercise library with filtering, search, media support, and seed data.

### Phase 1 steps (from roadmap)

1. **Database:** Create `exercises` and `exercise_media` tables + Alembic migration.
2. **Seed data:** Import ~200-300 exercises from the `wger` open-source dataset covering all body parts and categories.
3. **API endpoints:**
   - `GET /exercises` — list with filter/search (`body_part`, `category`, `q`)
   - `GET /exercises/{id}` — detail + media
   - `POST /exercises` — create custom exercise (auth required)
   - `PATCH /exercises/{id}` — update custom exercise (owner only)
   - `POST /exercises/{id}/media` — upload media to MinIO
   - `PATCH /exercises/{id}/media/{media_id}` — set `demo_start_seconds` / `demo_end_seconds`
4. **Web:** Exercise library browser with filter sidebar, exercise detail page.
5. **Mobile:** Exercise list screen with search/filter, exercise detail sheet.

### Data model (from roadmap)

```
Exercise
├── id (uuid)
├── name
├── description
├── instructions (text)
├── body_part  ENUM: chest | back | shoulders | arms | legs | core | full_body | cardio
├── category   ENUM: barbell | dumbbell | machine | weighted_bodyweight |
│              assisted_bodyweight | reps_only | cardio | duration
├── is_custom (bool)
├── created_by (FK → User, null = built-in)
└── created_at

ExerciseMedia
├── id
├── exercise_id (FK → Exercise)
├── media_type: 'gif' | 'video' | 'image'
├── storage_path (MinIO object key)
├── source_url (original import URL, nullable)
├── is_primary (bool)
├── demo_start_seconds (float, nullable)
├── demo_end_seconds (float, nullable)
└── created_at
```

### TypeScript types already defined (packages/types/src/index.ts)

```typescript
export type MuscleGroup =
  | "chest" | "back" | "shoulders" | "biceps" | "triceps"
  | "forearms" | "core" | "quads" | "hamstrings" | "glutes" | "calves";

export type EquipmentType =
  | "barbell" | "dumbbell" | "cable" | "machine"
  | "bodyweight" | "kettlebell" | "band" | "other";

export interface Exercise {
  id: string;
  name: string;
  primaryMuscle: MuscleGroup;
  secondaryMuscles: MuscleGroup[];
  equipment: EquipmentType;
  instructions?: string;
  videoUrl?: string;
  thumbnailUrl?: string;
  isCustom: boolean;
  createdAt: string;
  updatedAt: string;
}
```

> **Note:** The roadmap data model uses `body_part` + `category` enums while the TypeScript types use `primaryMuscle` / `secondaryMuscles` + `equipment`. Reconcile these during implementation — the TypeScript types are more granular and should be the source of truth. Update the Python model to match.

### Key files to reference

- `@ROADMAP.md` — full project roadmap with data model and all phase details
- `@CONNECTION.md` — SSH aliases, deploy workflow, Makefile targets
- `apps/api/app/config.py` — all env var settings
- `apps/api/app/database.py` — SQLAlchemy engine + Base
- `apps/api/app/main.py` — FastAPI app
- `packages/types/src/index.ts` — shared TypeScript interfaces

### Deliverables

- [ ] Exercise + ExerciseMedia tables migrated via Alembic
- [ ] ~200+ exercises seeded from wger or similar open dataset
- [ ] Filter and search work across all fields
- [ ] Media upload stores to MinIO and URL resolves correctly
- [ ] Web exercise browser with filter sidebar is functional
- [ ] Mobile exercise list with search/filter is usable on iPhone

Please read `@ROADMAP.md` and `@CONNECTION.md`, then start implementing Phase 1. Begin with the database models and migration, then the API endpoints, then seed data, then the web UI.
