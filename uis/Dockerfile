# syntax=docker/dockerfile:1

FROM node:22-alpine AS website-deps
WORKDIR /src
COPY website/package.json website/package-lock.json ./
RUN npm ci

FROM node:22-alpine AS portal-deps
WORKDIR /src
COPY portal/package.json portal/package-lock.json ./
RUN npm ci

FROM node:22-alpine AS backoffice-deps
WORKDIR /src
COPY backoffice/package.json backoffice/package-lock.json ./
RUN npm ci \
    && node -e "const fs=require('fs'); const n=fs.statSync('node_modules/typescript/lib/typescript.js').size; if(n<8000000){console.error('typescript.js truncated', n); process.exit(1)}"

FROM node:22-alpine AS dev
RUN apk add --no-cache wget
WORKDIR /app
COPY website /app/website
COPY portal /app/portal
COPY backoffice /app/backoffice
COPY --from=website-deps /src/node_modules /opt/modules/website
COPY --from=portal-deps /src/node_modules /opt/modules/portal
COPY --from=backoffice-deps /src/node_modules /opt/modules/backoffice
COPY --from=website-deps /src/node_modules /app/website/node_modules
COPY --from=portal-deps /src/node_modules /app/portal/node_modules
COPY --from=backoffice-deps /src/node_modules /app/backoffice/node_modules
COPY start.sh start-prod.sh /app/
RUN chmod 755 /app/start.sh /app/start-prod.sh \
    && chown -R node:node /app /opt/modules
USER node
EXPOSE 3000 3001
CMD ["sh", "/app/start.sh"]

FROM dev AS prod
USER root
RUN cd /app/portal && npm run build \
    && cd /app/backoffice && npm run build \
    && chown -R node:node /app
USER node
CMD ["sh", "/app/start-prod.sh"]
