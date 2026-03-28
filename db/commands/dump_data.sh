#!/usr/bin/env bash

# This helper script dumps the data from the db
# to a jsonfile located in the file system
# we avoid hardcoding it by using env variables
# Example for newcomers:
# export DUMP_FILEPATH="/tmp/db_dump/db_dump.json"
# for optional even less hardcoding we added another
# env variables 

sudo -u postgres psql -d $DB_NAME -t -A -c \
"SELECT jsonb_pretty(jsonb_agg(to_jsonb(t))) FROM (SELECT * FROM events) t;"\
> $DUMP_FILEPATH  

# Author : rub3ck0r3
