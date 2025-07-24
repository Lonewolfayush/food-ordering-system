# Quick Start Guide - Testing JSON Storage

## 1. Start the Django Development Server

```bash
cd /Users/ASUS/Desktop/adobe
source .venv/bin/activate
python manage.py runserver
```

## 2. Test the Web Interface

1. Open your browser and go to `http://localhost:8000`
2. Upload a PDF file using the web interface
3. The extracted outline will be saved as a JSON file in `output/`
4. You'll see the saved results displayed on the homepage

## 3. Test JSON Storage Functionality

```bash
# Test the JSON storage functions
python test_json_storage.py
```

## 4. View Saved Results

- **Web Interface**: Visit `http://localhost:8000` to see all saved results
- **API Endpoint**: Visit `http://localhost:8000/results/` for JSON API
- **File System**: Check `output/` directory for JSON files

## 5. Download Results

- Click "Download JSON" button on any saved result card
- Or use the API: `http://localhost:8000/download/filename.json/`

## 6. Clean Up Old Results

```bash
# Show what files would be deleted (dry run)
python manage.py cleanup_results --days 30 --dry-run

# Actually delete files older than 30 days
python manage.py cleanup_results --days 30
```

## 7. Test with Sample PDF

```bash
# If you have a PDF file, place it in the project directory
# Then test the extraction
python test_extractor.py
```

## File Structure

```
output/
├── sample_document_20250716_143022.json
├── research_paper_20250716_143045.json
└── ...
```

## JSON File Format

Each saved JSON file contains:
```json
{
  "source_pdf": "sample.pdf",
  "processed_at": "2025-07-16T14:30:22.123456",
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Introduction",
      "page": 1
    }
  ]
}
```

## API Endpoints

- `POST /extract/` - Extract outline from uploaded PDF
- `GET /results/` - Get list of all saved results
- `GET /download/<filename>/` - Download specific result file
- `GET /` - Web interface with saved results display
