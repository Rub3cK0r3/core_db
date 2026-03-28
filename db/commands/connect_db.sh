#!/usr/bin/env bash

# connect to mock db with the postgres "superuser".. 
sudo -u postgres psql -h 127.0.0.1 -d "$POSTGRES_DB"

# Author : rub3ck0r3
