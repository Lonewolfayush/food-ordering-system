import os
import json
import re
from typing import List, Dict, Any
from datetime import datetime
import pdfplumber
from PyPDF2 import PdfReader
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


def save_outline_to_json(pdf_filename: str, outline: Dict[str, Any]) -> str:
    """
    Save outline data to JSON file in the output folder
    Returns the path to the saved file
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.join(settings.BASE_DIR, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_name = os.path.splitext(pdf_filename)[0]  # Remove .pdf extension
    json_filename = f"{pdf_name}_{timestamp}.json"
    json_file_path = os.path.join(output_dir, json_filename)
    
    # Add metadata to outline
    outline_with_metadata = {
        "source_pdf": pdf_filename,
        "processed_at": datetime.now().isoformat(),
        "title": outline.get("title", ""),
        "outline": outline.get("outline", [])
    }
    
    # Save JSON file
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(outline_with_metadata, f, indent=2, ensure_ascii=False)
    
    # Return relative path for response
    return f"output/{json_filename}"


def get_all_saved_results():
    """Get list of all saved result files"""
    output_dir = os.path.join(settings.BASE_DIR, 'output')
    if not os.path.exists(output_dir):
        return []
    
    json_files = []
    for filename in os.listdir(output_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(output_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    json_files.append({
                        'filename': filename,
                        'source_pdf': data.get('source_pdf', ''),
                        'processed_at': data.get('processed_at', ''),
                        'title': data.get('title', ''),
                        'headings_count': len(data.get('outline', []))
                    })
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    return sorted(json_files, key=lambda x: x['processed_at'], reverse=True)


def index(request):
    """Home page view with saved results"""
    saved_results = get_all_saved_results()
    return render(request, 'extractor/index.html', {'saved_results': saved_results})


def view_results(request):
    """View all saved results"""
    saved_results = get_all_saved_results()
    return JsonResponse({'results': saved_results})


def download_result(request, filename):
    """Download a specific result file"""
    output_dir = os.path.join(settings.BASE_DIR, 'output')
    file_path = os.path.join(output_dir, filename)
    
    if not os.path.exists(file_path) or not filename.endswith('.json'):
        return JsonResponse({'error': 'File not found'}, status=404)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': f'Error reading file: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def extract_outline(request):
    """Extract PDF outline and return JSON"""
    if 'pdf_file' not in request.FILES:
        return JsonResponse({'error': 'No PDF file provided'}, status=400)
    
    pdf_file = request.FILES['pdf_file']
    
    # Validate file type
    if not pdf_file.name.endswith('.pdf'):
        return JsonResponse({'error': 'File must be a PDF'}, status=400)
    
    # Validate file size (50MB limit)
    if pdf_file.size > 50 * 1024 * 1024:
        return JsonResponse({'error': 'File size exceeds 50MB limit'}, status=400)
    
    try:
        # Save file temporarily
        file_path = default_storage.save(f'temp_{pdf_file.name}', ContentFile(pdf_file.read()))
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        # Extract outline
        outline = extract_pdf_outline(full_path)
        
        # Save result to JSON file
        json_file_path = save_outline_to_json(pdf_file.name, outline)
        
        # Clean up temp file
        default_storage.delete(file_path)
        
        # Add file path to response
        response_data = outline.copy()
        response_data['saved_to'] = json_file_path
        
        return JsonResponse(response_data, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': f'Error processing PDF: {str(e)}'}, status=500)


def extract_pdf_outline(pdf_path: str) -> Dict[str, Any]:
    """
    Extract PDF outline including title and headings (H1, H2, H3)
    """
    try:
        # Try pdfplumber first for better text extraction
        with pdfplumber.open(pdf_path) as pdf:
            outline = {
                "title": "",
                "outline": []
            }
            
            # Extract title from first page
            if pdf.pages:
                first_page = pdf.pages[0]
                title = extract_title_from_page(first_page)
                outline["title"] = title
            
            # Extract headings from all pages
            for page_num, page in enumerate(pdf.pages, 1):
                headings = extract_headings_from_page(page, page_num)
                outline["outline"].extend(headings)
            
            return outline
    
    except Exception as e:
        # Fallback to PyPDF2
        return extract_with_pypdf2(pdf_path)


def extract_title_from_page(page) -> str:
    """Extract title from the first page"""
    text = page.extract_text()
    if not text:
        return ""
    
    lines = text.split('\n')
    # Look for title patterns (usually the first significant line)
    for line in lines:
        line = line.strip()
        if line and len(line) > 3:  # Skip very short lines
            # Basic title detection - first substantial line
            return line
    
    return ""


def extract_headings_from_page(page, page_num: int) -> List[Dict[str, Any]]:
    """Extract headings from a single page"""
    headings = []
    
    try:
        # Get text with formatting information
        text = page.extract_text()
        if not text:
            return headings
        
        # Get character-level information for font size analysis
        chars = page.chars
        
        # Analyze font sizes to determine heading levels
        font_sizes = {}
        for char in chars:
            if 'size' in char:
                size = char['size']
                font_sizes[size] = font_sizes.get(size, 0) + 1
        
        # Sort font sizes to determine hierarchy
        sorted_sizes = sorted(font_sizes.keys(), reverse=True)
        
        # Extract text lines and analyze
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Simple heading detection patterns
            heading_level = detect_heading_level(line, chars, sorted_sizes)
            
            if heading_level:
                headings.append({
                    "level": heading_level,
                    "text": line,
                    "page": page_num
                })
    
    except Exception as e:
        # Fallback to simple text pattern matching
        headings.extend(extract_headings_fallback(page, page_num))
    
    return headings


def detect_heading_level(line: str, chars: List[Dict], sorted_sizes: List[float]) -> str:
    """Detect heading level based on various criteria"""
    
    # Pattern-based detection
    # 1. Check for numbered sections (1., 1.1, 1.1.1, etc.)
    if re.match(r'^\d+\.\s+', line):
        return "H1"
    elif re.match(r'^\d+\.\d+\s+', line):
        return "H2"
    elif re.match(r'^\d+\.\d+\.\d+\s+', line):
        return "H3"
    
    # 2. Check for all caps (common heading pattern)
    if line.isupper() and len(line) > 3:
        return "H1"
    
    # 3. Check for title case and length
    if line.istitle() and 10 <= len(line) <= 100:
        return "H2"
    
    # 4. Check for specific keywords
    heading_keywords = ['chapter', 'section', 'introduction', 'conclusion', 'overview', 'summary']
    if any(keyword in line.lower() for keyword in heading_keywords):
        return "H2"
    
    # 5. Font size analysis (if available)
    if sorted_sizes and len(sorted_sizes) > 2:
        # This is a simplified font size analysis
        # In a real implementation, you'd need to match line text to character positions
        pass
    
    return None


def extract_headings_fallback(page, page_num: int) -> List[Dict[str, Any]]:
    """Fallback heading extraction using simple patterns"""
    headings = []
    text = page.extract_text()
    
    if not text:
        return headings
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Simple pattern matching
        if re.match(r'^[A-Z][A-Z\s]+[A-Z]$', line) and len(line) > 3:  # ALL CAPS
            headings.append({
                "level": "H1",
                "text": line,
                "page": page_num
            })
        elif re.match(r'^\d+\.\s+[A-Z]', line):  # Numbered sections
            headings.append({
                "level": "H1",
                "text": line,
                "page": page_num
            })
        elif re.match(r'^\d+\.\d+\s+[A-Z]', line):  # Subsections
            headings.append({
                "level": "H2",
                "text": line,
                "page": page_num
            })
        elif re.match(r'^\d+\.\d+\.\d+\s+[A-Z]', line):  # Sub-subsections
            headings.append({
                "level": "H3",
                "text": line,
                "page": page_num
            })
    
    return headings


def extract_with_pypdf2(pdf_path: str) -> Dict[str, Any]:
    """Fallback extraction using PyPDF2"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            
            outline = {
                "title": "",
                "outline": []
            }
            
            # Extract title from metadata or first page
            if pdf_reader.metadata and '/Title' in pdf_reader.metadata:
                outline["title"] = pdf_reader.metadata['/Title']
            elif pdf_reader.pages:
                first_page_text = pdf_reader.pages[0].extract_text()
                if first_page_text:
                    lines = first_page_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and len(line) > 3:
                            outline["title"] = line
                            break
            
            # Extract headings from all pages
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text:
                    headings = extract_headings_from_text(text, page_num)
                    outline["outline"].extend(headings)
            
            return outline
    
    except Exception as e:
        return {
            "title": "Error extracting title",
            "outline": []
        }


def extract_headings_from_text(text: str, page_num: int) -> List[Dict[str, Any]]:
    """Extract headings from plain text"""
    headings = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Pattern matching for headings
        if re.match(r'^[A-Z][A-Z\s]+[A-Z]$', line) and len(line) > 3:
            headings.append({
                "level": "H1",
                "text": line,
                "page": page_num
            })
        elif re.match(r'^\d+\.\s+[A-Z]', line):
            headings.append({
                "level": "H1",
                "text": line,
                "page": page_num
            })
        elif re.match(r'^\d+\.\d+\s+[A-Z]', line):
            headings.append({
                "level": "H2",
                "text": line,
                "page": page_num
            })
        elif re.match(r'^\d+\.\d+\.\d+\s+[A-Z]', line):
            headings.append({
                "level": "H3",
                "text": line,
                "page": page_num
            })
    
    return headings
