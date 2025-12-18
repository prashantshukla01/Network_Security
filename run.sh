#!/bin/bash

# Stop on first error
set -e

echo "Starting Deployment Script..."

# 1. Update Code (Optional if run manually, but good practice if in a cron/CI)
# git pull origin main

# 2. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# 3. Install Dependencies
echo "Installing/Updating dependencies..."
pip install -r requirements.txt
pip install python-multipart
pip install uvicorn

# 4. Run Application
echo "Starting Application on Port 8000..."
# Using python app.py as seen in Dockerfile/app.py
python3 app.py
