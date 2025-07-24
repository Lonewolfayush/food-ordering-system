#!/usr/bin/env python3
"""
Test script for PDF outline extractor
"""

import json
import sys
from pathlib import Path
from process_pdfs import extract_pdf_outline


def test_sample_pdf():
    """Test with a sample PDF if available"""
    # Look for sample PDFs in current directory
    sample_pdfs = list(Path('.').glob('*.pdf'))
    
    if not sample_pdfs:
        print("No PDF files found in current directory for testing")
        return
    
    for pdf_file in sample_pdfs:
        print(f"\nTesting with: {pdf_file.name}")
        
        try:
            # Extract outline
            outline = extract_pdf_outline(str(pdf_file))
            
            # Print results
            print(f"Title: {outline['title']}")
            print(f"Headings found: {len(outline['outline'])}")
            
            for heading in outline['outline']:
                print(f"  {heading['level']}: {heading['text']} (Page {heading['page']})")
            
            # Save test output
            output_file = pdf_file.stem + "_test.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(outline, f, indent=2, ensure_ascii=False)
            
            print(f"Test output saved to: {output_file}")
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")


def validate_json_format(json_data):
    """Validate JSON output format"""
    required_keys = ['title', 'outline']
    
    for key in required_keys:
        if key not in json_data:
            return False, f"Missing required key: {key}"
    
    if not isinstance(json_data['title'], str):
        return False, "Title must be a string"
    
    if not isinstance(json_data['outline'], list):
        return False, "Outline must be a list"
    
    for item in json_data['outline']:
        if not isinstance(item, dict):
            return False, "Outline items must be dictionaries"
        
        required_item_keys = ['level', 'text', 'page']
        for key in required_item_keys:
            if key not in item:
                return False, f"Missing required key in outline item: {key}"
        
        if item['level'] not in ['H1', 'H2', 'H3']:
            return False, f"Invalid heading level: {item['level']}"
        
        if not isinstance(item['text'], str):
            return False, "Heading text must be a string"
        
        if not isinstance(item['page'], int) or item['page'] < 1:
            return False, "Page number must be a positive integer"
    
    return True, "JSON format is valid"


if __name__ == "__main__":
    print("PDF Outline Extractor - Test Script")
    print("=" * 40)
    
    test_sample_pdf()
    
    # Test JSON validation
    print("\nTesting JSON validation...")
    
    # Valid JSON
    valid_json = {
        "title": "Test Document",
        "outline": [
            {"level": "H1", "text": "Introduction", "page": 1},
            {"level": "H2", "text": "Background", "page": 2}
        ]
    }
    
    is_valid, message = validate_json_format(valid_json)
    print(f"Valid JSON test: {is_valid} - {message}")
    
    # Invalid JSON
    invalid_json = {
        "title": "Test Document",
        "outline": [
            {"level": "H4", "text": "Invalid Level", "page": 1}
        ]
    }
    
    is_valid, message = validate_json_format(invalid_json)
    print(f"Invalid JSON test: {is_valid} - {message}")
    
    print("\nTest completed!")
