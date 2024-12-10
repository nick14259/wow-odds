#!/bin/bash
# start.sh

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Start the application
uvicorn api.app.main:app --host 0.0.0.0 --port 8000 --reload

# To make this script executable:
# chmod +x start.sh
