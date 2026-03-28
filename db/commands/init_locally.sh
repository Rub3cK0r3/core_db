#!/usr/bin/env bash

# This script loads the mock db 
# locally for testing and practice
# purposes, it creates everything 
# within the `V1_schema_dev` sql
# file..

cd ../init/

sudo -u postgres psql -d $DB_NAME --file V1_schema_dev.sql

# Author : Rub3ck0r3
