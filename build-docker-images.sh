#!/bin/sh

docker build -t ghcr.io/90victor09/ahri/base:latest -f base.Dockerfile .
docker build -t ghcr.io/90victor09/ahri/rest:latest -f app.Dockerfile .

if [ "$1" = "true" ]; then
  docker push ghcr.io/90victor09/ahri/base:latest
  docker push ghcr.io/90victor09/ahri/rest:latest
fi
