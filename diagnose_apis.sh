#!/usr/bin/env bash
set -uo pipefail
cd -- "$(dirname -- "$0")"
# Prints only lab container details; does not change or remove containers.
for name in lab8-api-v1 lab8-api-v2; do
  printf '\nContainer: %s\n' "$name"
  docker inspect --format 'Status={{.State.Status}} ExitCode={{.State.ExitCode}} Error={{.State.Error}}' "$name" 2>&1 || true
  docker port "$name" 2>&1 || true
  docker logs --tail 60 "$name" 2>&1 || true
done
for endpoint in http://127.0.0.1:5000/api/users http://127.0.0.1:3000/get_users; do
  printf '\nHTTP check: %s\n' "$endpoint"
  curl --noproxy '*' --connect-timeout 2 --max-time 5 --include --silent --show-error "$endpoint" 2>&1 || true
  printf '\n'
done
