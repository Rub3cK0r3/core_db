#!/usr/bin/env bash

# This helper script dumps the data from the db
# to a jsonfile located in the file system
# we avoid hardcoding it by using env variables
# Example for newcomers:
# export DUMP_FILEPATH="/tmp/db_dump/db_dump.json"
# for optional even less hardcoding we added another
# env variables 

psql -U $POSTGRES_USER -d $POSTGRES_DB <<EOF
COPY json_agg(
  SELECT *
  FROM events
)
TO $DUMP_FILEPATH;
EOF

# Author : rub3ck0r3
