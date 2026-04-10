#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

cleanup() {
  echo "=== Tearing down ==="
  docker-compose down
}
trap cleanup EXIT

echo "=== Starting services ==="
docker-compose up -d --build

echo "=== Waiting for services to be running ==="
EXPECTED=3
until [ "$(docker-compose ps --filter status=running --services | wc -l)" -eq "$EXPECTED" ]; do
  sleep 1
done
docker-compose ps

echo "=== Running DNS test via buildctl (BuildKit) ==="
docker exec copilot sh -c '
cd /tmp

cat <<EOF > Dockerfile
FROM nicolaka/netshoot
RUN nslookup google.com
EOF

buildctl build \
  --no-cache \
  --frontend dockerfile.v0 \
  --local context=. \
  --local dockerfile=. \
  --opt build-arg:http_proxy="$http_proxy" \
  --opt build-arg:https_proxy="$https_proxy" \
  --opt build-arg:no_proxy="$no_proxy" \
  --progress=plain
'

echo "=== Running DNS test via docker build (DinD) ==="
docker exec copilot sh -c '
cd /tmp

docker build \
  --no-cache \
  --build-arg http_proxy="$http_proxy" \
  --build-arg https_proxy="$https_proxy" \
  --build-arg no_proxy="$no_proxy" \
  .
'

echo "=== All tests passed ==="
