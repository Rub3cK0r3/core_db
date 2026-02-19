#!/usr/bin/env bash

export PGPASSWORD="${DB_PASSWORD}"
psql -h 127.0.0.1 -p 5432 -U "$DB_USER" -d "$DB_NAME"

# Author : rub3ck0r3
