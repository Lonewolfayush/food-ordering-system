#!/usr/bin/env python3
"""
PDF Outline Extractor for Adobe India Hackathon Round 1A
Processes PDFs from /app/input and outputs JSON to /app/output
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any
import pdfplumber
from PyPDF2 import PdfReader


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
        print(f"Error with pdfplumber, trying PyPDF2: {e}")
        # Fallback to PyPDF2
        return extract_with_pypdf2(pdf_path)


def extract_title_from_page(page) -> str:
    """Extract title from the first page"""
    try:
        text = page.extract_text()
        if not text:
            return ""
        
        lines = text.split('\n')
        # Look for title patterns (usually the first significant line)
        for line in lines:
            line = line.strip()
            if line and len(line) > 3 and not line.isdigit():
                # Skip page numbers and very short lines
                if not re.match(r'^\d+$', line):
                    return line
        
        return ""
    except Exception:
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
            if not line or len(line) < 3:
                continue
            
            # Simple heading detection patterns
            heading_level = detect_heading_level(line, sorted_sizes)
            
            if heading_level:
                headings.append({
                    "level": heading_level,
                    "text": line,
                    "page": page_num
                })
    
    except Exception as e:
        print(f"Error extracting headings from page {page_num}: {e}")
        # Fallback to simple text pattern matching
        headings.extend(extract_headings_fallback(page, page_num))
    
    return headings


def detect_heading_level(line: str, sorted_sizes: List[float]) -> str:
    """Detect heading level based on various criteria"""
    
    # Pattern-based detection
    # 1. Check for numbered sections (1., 1.1, 1.1.1, etc.)
    if re.match(r'^\d+\.\s+[A-Z]', line):
        return "H1"
    elif re.match(r'^\d+\.\d+\s+[A-Z]', line):
        return "H2"
    elif re.match(r'^\d+\.\d+\.\d+\s+[A-Z]', line):
        return "H3"
    
    # 2. Check for chapter/section keywords
    chapter_pattern = re.match(r'^(Chapter|Section|Part)\s+\d+', line, re.IGNORECASE)
    if chapter_pattern:
        return "H1"
    
    # 3. Check for all caps (common heading pattern)
    if line.isupper() and 4 <= len(line) <= 100:
        return "H1"
    
    # 4. Check for title case and reasonable length
    if line.istitle() and 5 <= len(line) <= 100:
        # Look for heading indicators
        if any(word in line.lower() for word in ['introduction', 'conclusion', 'overview', 'summary', 'abstract']):
            return "H1"
        elif any(word in line.lower() for word in ['method', 'result', 'discussion', 'analysis']):
            return "H2"
        else:
            return "H2"
    
    # 5. Check for Roman numerals
    if re.match(r'^[IVX]+\.\s+[A-Z]', line):
        return "H1"
    
    # 6. Check for alphabetic sections
    if re.match(r'^[A-Z]\.\s+[A-Z]', line):
        return "H2"
    
    return None


def extract_headings_fallback(page, page_num: int) -> List[Dict[str, Any]]:
    """Fallback heading extraction using simple patterns"""
    headings = []
    
    try:
        text = page.extract_text()
        if not text:
            return headings
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Simple pattern matching
            if re.match(r'^[A-Z][A-Z\s]+[A-Z]$', line) and 4 <= len(line) <= 100:  # ALL CAPS
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
    except Exception as e:
        print(f"Error in fallback extraction: {e}")
    
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
                outline["title"] = str(pdf_reader.metadata['/Title'])
            elif pdf_reader.pages:
                first_page_text = pdf_reader.pages[0].extract_text()
                if first_page_text:
                    lines = first_page_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and len(line) > 3 and not line.isdigit():
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
        print(f"Error with PyPDF2: {e}")
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
        if not line or len(line) < 3:
            continue
        
        # Pattern matching for headings
        if re.match(r'^[A-Z][A-Z\s]+[A-Z]$', line) and 4 <= len(line) <= 100:
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


def process_pdf_files():
    """Process all PDF files from input directory"""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        print("Error: Input directory /app/input does not exist")
        return
    
    # Process all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in input directory")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        try:
            print(f"Processing: {pdf_file.name}")
            
            # Extract outline
            outline = extract_pdf_outline(str(pdf_file))
            
            # Create output filename
            output_filename = pdf_file.stem + ".json"
            output_path = output_dir / output_filename
            
            # Save JSON output
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(outline, f, indent=2, ensure_ascii=False)
            
            print(f"Saved: {output_filename}")
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")
            # Create error output
            error_output = {
                "title": "Error processing PDF",
                "outline": [],
                "error": str(e)
            }
            output_filename = pdf_file.stem + ".json"
            output_path = output_dir / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(error_output, f, indent=2, ensure_ascii=False)
    
    print("Processing complete!")


if __name__ == "__main__":
    process_pdf_files()
