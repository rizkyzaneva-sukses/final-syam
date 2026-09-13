#!/bin/sh
set -eu

archive="${1:?Usage: verify_restore.sh BACKUP.dump}"
test -s "$archive"
compose_file="${COMPOSE_FILE:-docker-compose.prod.yml}"
test_db="bos_restore_$(date -u +%s)_$$"
case "$test_db" in bos_restore_[0-9]*) ;; *) echo "Unsafe temporary database name" >&2; exit 1 ;; esac

cleanup() {
  docker compose --env-file .env -f "$compose_file" exec -T db sh -c 'dropdb --if-exists -U "$POSTGRES_USER" "$1"' sh "$test_db" >/dev/null 2>&1 || true
}
trap cleanup EXIT HUP INT TERM
docker compose --env-file .env -f "$compose_file" exec -T db sh -c 'createdb -U "$POSTGRES_USER" "$1"' sh "$test_db"
docker compose --env-file .env -f "$compose_file" exec -T db sh -c 'pg_restore --exit-on-error --no-owner --no-acl -U "$POSTGRES_USER" -d "$1"' sh "$test_db" < "$archive"
docker compose --env-file .env -f "$compose_file" exec -T db sh -c 'test "$(psql -At -U "$POSTGRES_USER" -d "$1" -c "SELECT count(*) FROM alembic_version")" = 1' sh "$test_db"
docker compose --env-file .env -f "$compose_file" exec -T db sh -c 'psql -At -U "$POSTGRES_USER" -d "$1" -c "SELECT count(*) FROM orders"' sh "$test_db" >/dev/null
printf 'Restore verified in isolated database: %s\n' "$test_db"
