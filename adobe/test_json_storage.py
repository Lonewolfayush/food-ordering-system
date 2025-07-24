#!/usr/bin/env python3
"""
Test script for JSON saving functionality
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pdf_extractor.settings')
django.setup()

from extractor.views import save_outline_to_json, get_all_saved_results


def test_json_saving():
    """Test the JSON saving functionality"""
    print("Testing JSON saving functionality...")
    
    # Test data
    test_outline = {
        "title": "Test Document",
        "outline": [
            {"level": "H1", "text": "Introduction", "page": 1},
            {"level": "H2", "text": "Background", "page": 2},
            {"level": "H3", "text": "Related Work", "page": 3}
        ]
    }
    
    # Test saving
    try:
        saved_path = save_outline_to_json("test_document.pdf", test_outline)
        print(f"✓ Successfully saved to: {saved_path}")
        
        # Verify file exists in output directory
        output_dir = project_root / "output"
        json_files = list(output_dir.glob("*.json"))
        print(f"✓ Found {len(json_files)} JSON files in output directory")
        
    except Exception as e:
        print(f"✗ Error saving: {e}")
        return False
    
    # Test retrieving saved results
    try:
        saved_results = get_all_saved_results()
        print(f"✓ Retrieved {len(saved_results)} saved results")
        
        if saved_results:
            latest = saved_results[0]
            print(f"  Latest: {latest['filename']}")
            print(f"  Source: {latest['source_pdf']}")
            print(f"  Title: {latest['title']}")
            print(f"  Headings: {latest['headings_count']}")
    except Exception as e:
        print(f"✗ Error retrieving results: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("PDF Outline Extractor - JSON Storage Test")
    print("=" * 45)
    
    if test_json_saving():
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)
