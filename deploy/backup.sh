#!/bin/sh
set -eu
umask 077
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
BACKUP_DIR="${BACKUP_DIR:-backups}"
mkdir -p "$BACKUP_DIR"
temp_file=$(mktemp "$BACKUP_DIR/.bos_backup.XXXXXX")
trap 'rm -f "$temp_file"' EXIT HUP INT TERM
# Custom-format pg_dump is compressed already. A separate command preserves its exit status.
docker compose --env-file .env -f "$COMPOSE_FILE" exec -T db sh -c 'exec pg_dump -Fc -U "$POSTGRES_USER" "$POSTGRES_DB"' > "$temp_file"
test -s "$temp_file"
# Verify archive structure before publishing a successful backup.
docker compose --env-file .env -f "$COMPOSE_FILE" exec -T db pg_restore --list < "$temp_file" > /dev/null
backup_file="$BACKUP_DIR/bos_$(date -u +%Y%m%d_%H%M%S)_$$.dump"
mv "$temp_file" "$backup_file"
trap - EXIT HUP INT TERM
"$(dirname "$0")/verify_restore.sh" "$backup_file"
if [ -n "${OFFSITE_REMOTE:-}" ]; then
    command -v rclone >/dev/null 2>&1 || { echo "rclone is required for offsite backup" >&2; exit 1; }
    rclone copyto "$backup_file" "${OFFSITE_REMOTE%/}/$(basename "$backup_file")"
    if [ -n "${BACKUP_RETENTION_DAYS:-}" ]; then
        case "$BACKUP_RETENTION_DAYS" in *[!0-9]*|'') echo "BACKUP_RETENTION_DAYS must be a positive integer" >&2; exit 1 ;; esac
        test "$BACKUP_RETENTION_DAYS" -gt 0
        find "$BACKUP_DIR" -maxdepth 1 -type f -name 'bos_*.dump' -mtime "+$BACKUP_RETENTION_DAYS" -delete
    fi
else
    echo "Local restore verified. OFFSITE_REMOTE is unset; configure it before relying on this as production backup." >&2
fi
printf 'Backup verified: %s\n' "$backup_file"
