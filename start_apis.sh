#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
IMAGE="awa34/lab8-ali_rida_awad"
# Use after stopping the introductory container if it occupies port 5000.
for version in v1 v2; do
  name="lab8-api-$version"
  if docker container inspect "$name" >/dev/null 2>&1; then
    if [ "$(docker inspect --format '{{.State.Running}}' "$name")" != true ]; then
      docker start "$name"
    fi
  elif [ "$version" = v1 ]; then
    docker run -d --name "$name" -p 5000:5000 \
      --mount "type=bind,src=$(pwd)/activity2/lab5_api/database.db,dst=/app/database.db" "$IMAGE:0.0.1.RELEASE"
  else
    docker run -d --name "$name" -p 3000:3000 \
      --volumes-from lab8-api-v1 "$IMAGE:0.0.2.RELEASE"
  fi
done
for endpoint in http://127.0.0.1:5000/api/users http://127.0.0.1:3000/get_users; do
  ready=false
  for attempt in {1..20}; do
    if curl --noproxy '*' --connect-timeout 1 --max-time 2 --fail --silent --show-error "$endpoint" >/dev/null 2>&1; then
      ready=true
      break
    fi
    sleep 1
  done
  if [ "$ready" != true ]; then
    echo "API did not become ready: $endpoint. Diagnostic output follows." >&2
    bash diagnose_apis.sh
    exit 1
  fi
  echo "Ready: $endpoint"
done
