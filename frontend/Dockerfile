# The web app: a static build served by unprivileged nginx, which also forwards /api/ to the API.

FROM node:25-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY index.html vite.config.ts tsconfig.json tsconfig.app.json tsconfig.node.json ./
COPY public ./public
COPY nginx ./nginx
COPY src ./src
# The app is type-checked here; the tests and their configuration are checked in CI.
RUN npx tsc -p tsconfig.app.json && npx vite build

FROM nginxinc/nginx-unprivileged:1.28-alpine-slim
# Filled into the template at start by the base image's entrypoint; an origin, no path.
ENV API_UPSTREAM=http://api:8000 \
    NGINX_ENTRYPOINT_LOCAL_RESOLVERS=1
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY nginx/security-headers.conf /etc/nginx/snippets/security-headers.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
