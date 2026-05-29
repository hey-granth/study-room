#!/bin/bash
# scripts/backup-db.sh
# Dump PostgreSQL to a gzipped file and upload to S3.
# Schedule via crontab: 0 2 * * * /home/ubuntu/studyroom/scripts/backup-db.sh >> /var/log/db-backup.log 2>&1
set -euo pipefail

# Load env vars for POSTGRES_USER, POSTGRES_DB, S3_BUCKET
set -a
# shellcheck disable=SC1090
source /home/ubuntu/studyroom/.env
set +a

S3_BUCKET="${S3_BUCKET:-your-backup-bucket}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="studyroom_backup_${TIMESTAMP}.sql.gz"
TMP_PATH="/tmp/${BACKUP_FILE}"

echo "[backup] Starting database dump at ${TIMESTAMP}..."

docker compose -f /home/ubuntu/studyroom/docker-compose.yml exec -T db pg_dump \
  -U "${POSTGRES_USER}" \
  "${POSTGRES_DB}" | gzip > "${TMP_PATH}"

echo "[backup] Uploading to s3://${S3_BUCKET}/backups/${BACKUP_FILE}..."
aws s3 cp "${TMP_PATH}" "s3://${S3_BUCKET}/backups/${BACKUP_FILE}"
rm -f "${TMP_PATH}"

echo "[backup] Complete: s3://${S3_BUCKET}/backups/${BACKUP_FILE}"
