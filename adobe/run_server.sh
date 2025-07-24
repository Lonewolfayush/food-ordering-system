#!/bin/bash

echo "PDF Outline Extractor - Adobe India Hackathon Round 1A"
echo "======================================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Create output directory if it doesn't exist
mkdir -p output

echo ""
echo "Starting Django development server..."
echo "Visit: http://localhost:8000"
echo ""
echo "The server will automatically save JSON files to the 'output' directory"
echo "Press Ctrl+C to stop the server"
echo ""

# Run Django server
python manage.py runserver
