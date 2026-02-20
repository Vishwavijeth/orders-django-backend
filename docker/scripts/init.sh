#! /bin/bash

set -e

echo "Initializing containers.."

docker compose -f docker/db.yml up -d --build
docker compose -f docker/app.yml up -d --build

echo "Initialization complete."