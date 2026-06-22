#!/usr/bin/env bash
set -e
export SMARTQC_API_URL=${SMARTQC_API_URL:-http://127.0.0.1:8000/api}
python -m desktop.main
