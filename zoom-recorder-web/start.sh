#!/bin/bash
set -e
cd zoom-recorder-web/backend
export PORT=${PORT:-8000}
exec python main.py
