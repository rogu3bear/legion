#!/usr/bin/env bash
# Initialize Legion memory DB
mkdir -p memory/db
[ -f memory/db/legion.db ] || touch memory/db/legion.db
echo "Initialized Legion memory DB at memory/db/legion.db"
