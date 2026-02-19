#!/usr/bin/env bash
# Este script conecta a la DB usando el .env

export PGPASSWORD="${DB_PASSWORD}"
psql -h 127.0.0.1 -p 5432 -U "$DB_USER" -d "$DB_NAME"

