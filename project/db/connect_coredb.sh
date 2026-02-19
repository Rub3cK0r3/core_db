#!/usr/bin/env bash

# load .env file
export $(grep -v '^#' .env | xargs)

# connect to PostgreSQL.. 
PGPASSWORD="$POSTGRES_PASSWORD" psql -h 127.0.0.1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"

# Author : rub3ck0r3
