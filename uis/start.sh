#!/bin/sh
# One container, two Next.js processes.
# website -> uis/portal on port 3000 (the Next.js app this fork already ships).
# backoffice -> uis/backoffice on port 3001.
set -eu

# A bind mount hides the image node_modules. Copy the image copy when the
# mounted tree is missing or its TypeScript bundle was truncated.
sync_modules() {
  dest="$1"
  src="$2"
  if [ ! -d "$src" ]; then
    echo "missing module source $src" >&2
    exit 1
  fi
  if [ -f "$src/typescript/lib/typescript.js" ]; then
    src_size=$(wc -c < "$src/typescript/lib/typescript.js")
    dest_size=0
    if [ -f "$dest/typescript/lib/typescript.js" ]; then
      dest_size=$(wc -c < "$dest/typescript/lib/typescript.js")
    fi
    if [ "$dest_size" -lt "$src_size" ]; then
      find "$dest" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
      cp -a "$src"/. "$dest"/
    fi
  elif [ ! -d "$dest/next" ]; then
    mkdir -p "$dest"
    find "$dest" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
    cp -a "$src"/. "$dest"/
  fi
}

sync_modules /app/website/node_modules /opt/modules/website
sync_modules /app/portal/node_modules /opt/modules/portal
sync_modules /app/backoffice/node_modules /opt/modules/backoffice

cd /app/website
npm run dev &
website_pid=$!

cd /app/backoffice
npm run dev &
backoffice_pid=$!

trap 'kill "$website_pid" "$backoffice_pid" 2>/dev/null || true' INT TERM

while kill -0 "$website_pid" 2>/dev/null && kill -0 "$backoffice_pid" 2>/dev/null; do
  sleep 2
done

kill "$website_pid" "$backoffice_pid" 2>/dev/null || true
wait "$website_pid" 2>/dev/null || true
wait "$backoffice_pid" 2>/dev/null || true
exit 1
