#!/bin/sh
set -eu

python wait_for_db.py
exec uvicorn main:app --host 0.0.0.0 --port "${APP_PORT:-8000}"