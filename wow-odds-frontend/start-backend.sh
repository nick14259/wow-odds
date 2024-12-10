#!/bin/bash
# start-backend.sh

# Change to the project root directory
cd ~/wow-odds || exit 1

# Activate virtual environment
source venv/bin/activate

# Export environment variables from .env file
set -a
source .env
set +a

# Start the application
cd api
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
