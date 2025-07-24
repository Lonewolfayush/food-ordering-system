#!/bin/bash

# Sample usage script for PDF Outline Extractor

echo "PDF Outline Extractor - Adobe India Hackathon Round 1A"
echo "========================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Create input and output directories
mkdir -p input output

echo "Setup complete!"
echo ""
echo "Usage Instructions:"
echo "1. Place your PDF files in the 'input' directory"
echo "2. Run the following commands:"
echo ""
echo "   # Build the Docker image"
echo "   docker build --platform linux/amd64 -t pdf-extractor:latest ."
echo ""
echo "   # Run the extractor"
echo "   docker run --rm -v \$(pwd)/input:/app/input -v \$(pwd)/output:/app/output --network none pdf-extractor:latest"
echo ""
echo "3. Check the 'output' directory for JSON results"
echo ""
echo "For local development:"
echo "   python manage.py runserver"
echo "   # Then visit http://localhost:8000"
echo ""

# Check if there are any PDF files in input
if ls input/*.pdf 1> /dev/null 2>&1; then
    echo "PDF files found in input directory:"
    ls -la input/*.pdf
    echo ""
    echo "Ready to process! Run the Docker commands above."
else
    echo "No PDF files found in input directory."
    echo "Please add some PDF files to the input directory before running."
fi
