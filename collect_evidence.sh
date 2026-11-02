#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
mkdir -p evidence
# Run after build_and_run.sh. Also take a real terminal screenshot after each command.
docker ps -a | tee evidence/01-docker-ps-a.txt
docker stop lab8-hello | tee evidence/02-docker-stop.txt
docker logs lab8-hello 2>&1 | tee evidence/03-docker-logs.txt
docker image ls awa34/lab8-ali_rida_awad | tee evidence/04-images.txt
# Explain missing API containers before attempting HTTP requests.
for name in lab8-api-v1 lab8-api-v2; do
  if ! docker container inspect "$name" >/dev/null 2>&1 || \
     [ "$(docker inspect --format '{{.State.Running}}' "$name" 2>/dev/null)" != true ]; then
    echo "Activity 1 output saved. Required API container $name is not running." >&2
    echo "Run: bash start_apis.sh, then rerun: bash collect_evidence.sh" >&2
    exit 1
  fi
done
for entry in '5000/api/users 05-lab5-api.json' '3000/get_users 06-get-users.json'; do
  read -r endpoint filename <<< "$entry"
  # Flask can take a moment to become ready after container startup.
  ready=false
  for attempt in {1..20}; do
    if curl --noproxy '*' --connect-timeout 1 --max-time 2 --fail --silent --show-error "http://127.0.0.1:$endpoint" >"evidence/$filename.tmp" 2>/dev/null; then
      mv "evidence/$filename.tmp" "evidence/$filename"
      cat "evidence/$filename"
      printf '\n'
      ready=true
      break
    fi
    sleep 1
  done
  if [ "$ready" != true ]; then
    rm -f "evidence/$filename.tmp"
    echo "API unavailable on $endpoint. Check docker logs lab8-api-v1 and docker logs lab8-api-v2." >&2
    exit 1
  fi
done
