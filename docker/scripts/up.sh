#! /bin/bash

set -e 

echo "Starting services..."

docker compose -f docker/db.yml up -d
docker compose -f docker/app.yml up -d

