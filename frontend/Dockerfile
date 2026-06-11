FROM node:22-alpine AS builder
WORKDIR /app
# Copy the lockfile and use `npm ci` so the image build is reproducible
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# Unprivileged nginx runs as uid 101 and listens on 8080 — no root in the runtime image
FROM nginxinc/nginx-unprivileged:alpine
# Pick up OS security patches that the base image hasn't rebuilt with yet
USER root
RUN apk upgrade --no-cache
USER nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["wget", "-qO-", "http://127.0.0.1:8080/"]
