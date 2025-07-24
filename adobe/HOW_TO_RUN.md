# How to Run the PDF Outline Extractor

## 🚀 **Quick Start**

### **Option 1: Simple Start Script**
```bash
# Run the automated start script
./run_server.sh
```

### **Option 2: Manual Start**
```bash
# Navigate to project directory
cd /Users/ASUS/Desktop/adobe

# Activate virtual environment
source .venv/bin/activate

# Start Django server
python manage.py runserver
```

### **Option 3: Docker (Production)**
```bash
# Build Docker image
docker build --platform linux/amd64 -t pdf-extractor:latest .

# Run container (for hackathon submission)
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-extractor:latest
```

## 📁 **Project Structure**

```
adobe/
├── input/                    # Place PDF files here for Docker processing
├── output/                   # JSON results saved here automatically
├── manage.py                 # Django management
├── run_server.sh            # Quick start script
├── process_pdfs.py          # Docker processing script
├── Dockerfile               # Container configuration
├── requirements.txt         # Dependencies
└── extractor/               # Django app
    ├── views.py            # Main processing logic
    └── urls.py             # URL routing
```

## 🎯 **Usage**

### **Web Interface**
1. Run: `./run_server.sh` or `python manage.py runserver`
2. Open: `http://localhost:8000`
3. Upload PDF files
4. View results and download JSON files
5. **JSON files automatically saved to `output/` directory**

### **Docker Processing**
1. Place PDF files in `input/` directory
2. Run Docker container
3. Check `output/` directory for JSON results

## 📊 **Output Files**

All JSON files are automatically saved to the `output/` directory with format:
```
output/
├── document_name_20250716_143022.json
├── research_paper_20250716_143045.json
└── ...
```

## 🔧 **Testing**

```bash
# Test JSON storage functionality
python test_json_storage.py

# Test PDF extraction with sample files
python test_extractor.py

# Clean up old results
python manage.py cleanup_results --days 30
```

## 📋 **Requirements**

- Python 3.9+
- Django 4.2.0
- PyPDF2 3.0.1
- pdfplumber 0.9.0
- Virtual environment (recommended)

## 🎉 **Features**

✅ **Automatic JSON saving** to `output/` directory  
✅ **Timestamped filenames** for easy tracking  
✅ **Web interface** with upload and download  
✅ **Docker support** for hackathon submission  
✅ **Offline processing** - no internet required  
✅ **AMD64 compatible** Docker container  

## 📝 **Notes**

- JSON files are saved with metadata including source PDF name and processing timestamp
- The `output/` directory is created automatically if it doesn't exist
- Web interface shows previously processed files with download links
- Docker container saves results to `/app/output` which maps to local `output/` directory
