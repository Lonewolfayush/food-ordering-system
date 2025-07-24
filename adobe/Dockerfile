FROM --platform=linux/amd64 python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Create directories
RUN mkdir -p /app/input /app/output

# Ensure output directory has proper permissions
RUN chmod 755 /app/output

# Make the processing script executable
RUN chmod +x process_pdfs.py

# Set environment variables
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=pdf_extractor.settings

# Run the PDF processing script
CMD ["python", "process_pdfs.py"]
