#!/bin/bash
set -e

psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < /db.dump
