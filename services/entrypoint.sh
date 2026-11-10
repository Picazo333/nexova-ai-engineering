#!/bin/sh
# Fails closed when the signing secret is absent. The value stays in .env.
set -eu
if [ -z "${JWT_SECRET:-}" ]; then
  echo "Falta JWT_SECRET. Defínela en el .env de la raíz. La imagen no trae un secreto." >&2
  exit 1
fi
exec "$@"
