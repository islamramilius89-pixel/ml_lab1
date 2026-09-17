#!/bin/sh
set -eu

export VAULT_ADDR="http://127.0.0.1:8200"
ROOT_TOKEN="${VAULT_TOKEN:-root-token}"
SECRET_PATH="${VAULT_SECRET_PATH:-ml-lab3/db}"
KV_MOUNT="${VAULT_KV_MOUNT:-secret}"

vault server -dev -dev-root-token-id="$ROOT_TOKEN" -dev-listen-address="0.0.0.0:8200" &
VAULT_PID=$!

for _ in $(seq 1 30); do
  if VAULT_TOKEN="$ROOT_TOKEN" vault status >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

VAULT_TOKEN="$ROOT_TOKEN" vault kv put -mount="$KV_MOUNT" "$SECRET_PATH" \
  DB_USER="${POSTGRES_USER:-vault_user}" \
  DB_PASSWORD="${POSTGRES_PASSWORD:-vault_password}" \
  DB_NAME="${POSTGRES_DB:-predictions_db}"

wait "$VAULT_PID"
