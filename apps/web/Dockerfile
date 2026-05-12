# ── Stage 1 — install deps ────────────────────────────────────────────────────
# Build context is the monorepo root so pnpm can resolve workspace:* packages.
FROM node:20-alpine AS deps
RUN corepack enable && corepack prepare pnpm@9 --activate
WORKDIR /app

# Copy only the files pnpm needs to resolve + install
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./
COPY apps/web/package.json ./apps/web/
COPY packages/types/package.json ./packages/types/

RUN pnpm install --frozen-lockfile --filter @colossus/web...

# ── Stage 2 — build ──────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
RUN corepack enable && corepack prepare pnpm@9 --activate
WORKDIR /app

COPY --from=deps /app/ ./
COPY packages/types/ ./packages/types/
COPY apps/web/ ./apps/web/

# Build the shared types package first (web depends on it)
RUN pnpm --filter @colossus/types build
RUN pnpm --filter @colossus/web build

# ── Stage 3 — production runner ──────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# standalone output mirrors the monorepo directory structure
COPY --from=builder /app/apps/web/.next/standalone ./
COPY --from=builder /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder /app/apps/web/public ./apps/web/public

EXPOSE 3000
ENV PORT=3000
CMD ["node", "apps/web/server.js"]
