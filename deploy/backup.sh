#!/bin/sh
set -eu
mkdir -p backups
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "backups/bos_$(date +%Y%m%d_%H%M%S).sql.gz"
find backups -type f -mtime +14 -delete
