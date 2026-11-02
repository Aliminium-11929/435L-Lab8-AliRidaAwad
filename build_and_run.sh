#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
IMAGE="awa34/lab8-ali_rida_awad"
docker info >/dev/null
# The screenshot in the handout uses dot-separated RELEASE tags.
docker build -t flask_docker activity1/hello
docker build -t "$IMAGE:0.0.1.RELEASE" activity2/lab5_api
docker build -t "$IMAGE:0.0.2.RELEASE" activity2/users_api
# Preserve an existing introductory container and its evidence.
if ! docker container inspect lab8-hello >/dev/null 2>&1; then
  docker run -d --name lab8-hello -p 5001:5000 flask_docker
else
  echo "Keeping existing lab8-hello. If it uses port 5000, stop it before starting the APIs."
fi
bash start_apis.sh
echo "New Hello containers use http://localhost:5001/; existing containers retain their port mapping."
echo "Lab 5 API: http://localhost:5000/api/users"
echo "Names API: http://localhost:3000/get_users"
