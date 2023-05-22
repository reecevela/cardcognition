#!/bin/bash
set -e

sudo apt-get install dos2unix
dos2unix /db.dump

psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < /db.dump
