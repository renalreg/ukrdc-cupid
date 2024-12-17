#!/bin/bash

psql -U postgres -d postgres <<-EOSQL
    CREATE DATABASE ukrdc4;
    CREATE USER ukrdc WITH LOGIN PASSWORD 'password123';
EOSQL



# resore database using sql files
if [[ -f .dump/schema_dump.sql ]]; then
    psql -U postgres -d ukrdc4 -f .dump/schema_dump.sql
else
    echo "schema_dump.sql not found!"
    exit 1
fi

if [[ -f .dump/data_dump.sql ]]; then
    psql -U postgres -d ukrdc4 -f .dump/data_dump.sql
else
    echo "data_dump.sql not found!"
    exit 1
fi

# alembic is a pointless waste of life 

# initialise alembic
#psql -U postgres -d ukrdc4 <<-EOSQL
#    CREATE TABLE IF NOT EXISTS alembic_version (
#        version_num VARCHAR(32) NOT NULL
#    );
#    INSERT INTO alembic_version (version_num) VALUES ('a1a7539b1a57');
#EOSQL

#psql -U postgres -d ukrdc4 <<-EOSQL
#    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA extract TO ukrdc;
#EOSQL
#""

# migrate with sql instead
if [[ -f scripts/v5_migration.sql ]]; then
    psql -U postgres -d ukrdc4 -f scripts/v5_migration.sql
else
    echo "data_dump.sql not found!"
    exit 1
fi