#!/bin/bash -e
# With WAIT_FOR_DB=true, waits until Postgres accepts TCP connections before starting the command.
# With MIGRATE_DB=true, then applies the database migrations (alembic upgrade head); a failure stops the container.
if [[ "${WAIT_FOR_DB:-}" =~ ^([Tt]rue|1)$ ]]; then
  timeout="${DB_WAIT_TIMEOUT:-60}"
  deadline=$((SECONDS + timeout))
  until (exec 3<>"/dev/tcp/${DB_HOST}/${DB_PORT}") 2>/dev/null; do
    if ((SECONDS >= deadline)); then
      echo "Database ${DB_HOST}:${DB_PORT} not reachable after ${timeout}s" >&2
      exit 1
    fi
    sleep 1
  done
fi
if [[ "${MIGRATE_DB:-}" =~ ^([Tt]rue|1)$ ]]; then
  alembic upgrade head
fi
exec "$@"
