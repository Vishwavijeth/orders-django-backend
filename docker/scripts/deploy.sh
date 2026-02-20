#! /bin/bash

set -e 

echo "Deploying latest build..."

docker compose -f docker/app.yml down
docker compose -f docker/db.yml down

docker compose -f docker/db.yml up -d --build
docker compose -f docker/app.yml up -d --build

echo "Deployment finished."