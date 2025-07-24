# PDF Outline Extractor - Adobe India Hackathon Round 1A

This project extracts structured outlines from PDF documents, identifying titles and headings (H1, H2, H3) with their page numbers. The application provides both a web interface and Docker-based processing for production use.

## 🎯 Features

### Core Functionality
✅ **Automatic JSON saving** to `output/` directory  
✅ **Timestamped filenames** for easy tracking  
✅ **Web interface** with upload and download capabilities  
✅ **Docker support** for hackathon submission  
✅ **Offline processing** - no internet required  
✅ **AMD64 compatible** Docker container  
✅ **Result management** with view and download options  
✅ **Management commands** for cleanup and maintenance  

### Processing Capabilities
- Multiple PDF format support
- Robust error handling and fallback mechanisms
- Font-based heading detection
- Pattern-based text analysis
- Page number tracking
- Metadata preservation

## Approach

### Core Strategy
1. **Multi-library approach**: Uses `pdfplumber` for primary extraction with `PyPDF2` as fallback
2. **Pattern-based detection**: Identifies headings using multiple criteria:
   - Numbered sections (1., 1.1, 1.1.1)
   - ALL CAPS text
   - Title case with specific keywords
   - Font size analysis (when available)
   - Roman numerals and alphabetic sections

### Architecture
- **Django Framework**: Provides web interface and API endpoints
- **Modular Design**: Separate extraction logic for easy testing and maintenance
- **Error Handling**: Robust fallback mechanisms for various PDF formats
- **JSON Storage**: Automatic saving with metadata and timestamps

## Models and Libraries Used

### Primary Libraries
- **pdfplumber** (0.9.0): Advanced PDF text extraction with character-level formatting
- **PyPDF2** (3.0.1): Fallback PDF processing and metadata extraction
- **Django** (4.2.0): Web framework for API and interface

### Detection Algorithms
1. **Title Extraction**: First significant line from page 1
2. **Heading Classification**:
   - H1: Numbered sections (1.), ALL CAPS, chapters
   - H2: Subsections (1.1), title case with keywords
   - H3: Sub-subsections (1.1.1), specific patterns

## How to Build and Run

### 🚀 Quick Start Options

#### **Option 1: Automated Script (Recommended for Development)**
```bash
# Run the automated start script
./run_server.sh
```

#### **Option 2: Manual Setup**
```bash
# Navigate to project directory
cd /path/to/adobe

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start Django server
python manage.py runserver

# Access web interface at http://localhost:8000
```

#### **Option 3: Docker Execution (Production/Hackathon Submission)**
```bash
# Build the Docker image
docker build --platform linux/amd64 -t pdf-extractor:latest .

# Run the container (offline processing)
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-extractor:latest
```

### 📁 Project Structure

```
adobe/
├── .gitignore               # Git ignore patterns
├── .venv/                   # Virtual environment (not tracked)
├── Dockerfile               # Container configuration
├── HOW_TO_RUN.md           # Detailed setup instructions
├── QUICKSTART.md           # Quick testing guide
├── README.md               # This file
├── db.sqlite3              # Django database (not tracked)
├── requirements.txt        # Python dependencies
├── manage.py               # Django management
├── run_server.sh           # Quick start script
├── process_pdfs.py         # Docker processing script
├── test_*.py               # Test scripts
├── input/                  # PDF files for Docker processing (not tracked)
├── output/                 # JSON results (not tracked)
├── media/                  # Django media files (not tracked)
├── static/                 # Static files
├── templates/              # HTML templates
│   └── extractor/
│       └── index.html      # Web interface
├── pdf_extractor/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── extractor/              # Main Django app
    ├── views.py            # PDF processing logic
    ├── urls.py             # URL routing
    ├── models.py           # Django models
    ├── admin.py            # Admin interface
    ├── apps.py             # App configuration
    ├── tests.py            # Unit tests
    └── management/         # Management commands
        └── commands/
            └── cleanup_results.py
```

### 🎯 Usage Examples

#### **Web Interface**
1. Start the server: `./run_server.sh`
2. Open browser: `http://localhost:8000`
3. Upload PDF file
4. Download JSON results
5. View processing history

#### **Docker Processing**
```bash
# Place PDF files in input directory
mkdir input
cp document.pdf input/

# Run Docker container
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-extractor:latest

# Check results
ls output/
cat output/document_YYYYMMDD_HHMMSS.json
```

#### **Management Commands**
```bash
# Clean up old result files
python manage.py cleanup_results --days 30

# Dry run to see what would be deleted
python manage.py cleanup_results --days 7 --dry-run
```

## API Endpoints

The Django application provides several API endpoints:

- **`GET /`** - Web interface homepage with saved results
- **`POST /extract/`** - Upload PDF and extract outline
- **`GET /results/`** - JSON API for all saved results
- **`GET /download/<filename>/`** - Download specific result file

### Example API Usage
```bash
# Upload PDF via API
curl -X POST -F "pdf_file=@document.pdf" http://localhost:8000/extract/

# Get all results
curl http://localhost:8000/results/

# Download specific result
curl http://localhost:8000/download/document_20250724_123456.json
```

## Features

### Input Validation
- File type validation (PDF only)
- Size limit enforcement (50MB max)
- Page count validation (50 pages max)

### Output Format
```json
{
  "title": "Document Title",
  "metadata": {
    "source_file": "document.pdf",
    "processed_at": "2025-07-24T12:34:56.789Z",
    "processing_time_seconds": 2.45,
    "total_pages": 25
  },
  "outline": [
    {
      "level": "H1",
      "text": "Introduction", 
      "page": 1
    },
    {
      "level": "H2",
      "text": "Background",
      "page": 2
    },
    {
      "level": "H3",
      "text": "Literature Review",
      "page": 3
    }
  ]
}
```

### Error Handling
- Graceful fallbacks between libraries
- Detailed error reporting  
- Continues processing even with individual page errors
- Comprehensive logging for debugging

## Performance Considerations

- **Execution Time**: Optimized for <10 seconds per 50-page PDF
- **Memory Usage**: Efficient processing with minimal memory footprint
- **CPU Only**: No GPU dependencies, runs on standard CPU architecture
- **Model Size**: Lightweight approach without heavy ML models

## Constraints Compliance

✅ **Execution Time**: ≤10 seconds for 50-page PDF  
✅ **Model Size**: No models used (pattern-based approach)  
✅ **Network**: No internet access required (offline processing)  
✅ **Runtime**: CPU-only, compatible with 8 CPUs/16GB RAM  
✅ **Architecture**: AMD64 compatible Docker container  
✅ **File Handling**: Supports PDFs up to 50MB and 50 pages  
✅ **Output Format**: JSON with structured outline data  

## Troubleshooting

### Common Issues

#### **Virtual Environment Issues**
```bash
# If virtual environment creation fails
python3 -m venv .venv --clear
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### **Permission Issues**
```bash
# Make scripts executable
chmod +x run_server.sh
chmod +x process_pdfs.py
```

#### **Docker Issues**
```bash
# Clear Docker cache if build fails
docker system prune
docker build --no-cache --platform linux/amd64 -t pdf-extractor:latest .
```

#### **Port Already in Use**
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
python manage.py runserver 8001
```

### Log Files
- Django logs: Check console output
- Processing logs: Included in JSON response
- Error logs: Displayed in web interface

## Contributing

### Code Structure
- **Backend Logic**: `extractor/views.py`
- **URL Routing**: `extractor/urls.py`
- **Templates**: `templates/extractor/`
- **Static Files**: `static/`
- **Settings**: `pdf_extractor/settings.py`

### Adding New Extraction Patterns
1. Modify `detect_heading_level()` function
2. Add patterns to heading detection logic
3. Test with various PDF formats
4. Update documentation

## Support Files

- **`HOW_TO_RUN.md`** - Detailed setup and execution instructions
- **`QUICKSTART.md`** - Quick testing guide for JSON storage
- **`requirements.txt`** - Python package dependencies
- **`Dockerfile`** - Container configuration for production
- **`.gitignore`** - Git ignore patterns for clean repository

---

**Note**: This solution prioritizes reliability and accuracy over complexity, using proven pattern-matching techniques rather than experimental ML approaches to ensure consistent results within the hackathon constraints. The modular Django architecture allows for easy extension and maintenance while providing both web interface and API access for different use cases.
