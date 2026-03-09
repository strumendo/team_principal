# TeamPrincipal Frontend Dockerfile
# Multi-stage: deps, dev, builder, prod
# Dockerfile do Frontend TeamPrincipal
# Multi-stage: deps, dev, builder, prod

# ---- Dependencies ----
FROM node:20-alpine AS deps

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

# ---- Development ----
FROM deps AS dev

WORKDIR /app

COPY . .

CMD ["npm", "run", "dev"]

# ---- Builder ----
FROM deps AS builder

WORKDIR /app

COPY . .

# Build arg for API URL (injected at build time)
# Argumento de build para URL da API (injetado no build)
ARG NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# ---- Production ----
FROM node:20-alpine AS prod

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=30s \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
