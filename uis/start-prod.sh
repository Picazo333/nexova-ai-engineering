#!/bin/sh
# Production processes. No file watcher. The image already ran next build.
set -eu

cd /app/website
npm run start &
website_pid=$!

cd /app/backoffice
npm run start &
backoffice_pid=$!

trap 'kill "$website_pid" "$backoffice_pid" 2>/dev/null || true' INT TERM

while kill -0 "$website_pid" 2>/dev/null && kill -0 "$backoffice_pid" 2>/dev/null; do
  sleep 2
done

kill "$website_pid" "$backoffice_pid" 2>/dev/null || true
wait "$website_pid" 2>/dev/null || true
wait "$backoffice_pid" 2>/dev/null || true
exit 1
