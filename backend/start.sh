#!/bin/sh
# Runs on every container start (local docker-compose and Railway alike).
# - Applies any pending Alembic migrations before the app starts serving traffic.
# - Binds to $PORT when the platform provides one (Railway assigns this dynamically and
#   routes its public URL to whatever port the container actually listens on); falls back
#   to 8000 for docker-compose / plain `docker run`, where the port is fixed by the compose
#   file's port mapping instead.
set -e

alembic upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
