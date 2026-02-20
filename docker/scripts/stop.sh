#! /bin/bash

set -e

echo "Stopping services.."

docker compsoe -f docker/app.yml down
docker compose -f docker/db.yml down

