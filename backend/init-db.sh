#!/bin/bash
set -e

pg_restore -U postgres -d commander_db /docker-entrypoint-initdb.d/db.dump
