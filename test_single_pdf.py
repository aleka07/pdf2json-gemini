#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pdf_processor import PDFProcessor

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get API key from environment variable
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        print("❌ Error: GEMINI_API_KEY environment variable not set!")
        print("💡 Options to fix this:")
        print("   1. Set environment variable: export GEMINI_API_KEY='your-api-key-here'")
        print("   2. Create .env file: cp .env.example .env and edit it")
        print("   3. Get API key from: https://aistudio.google.com/app/apikey")
        return

    # Initialize processor
    processor = PDFProcessor(API_KEY)

    # Test with first PDF from data/input/ (any category)
    input_base = Path("data/input")
    if not input_base.exists():
        print(f"Input directory not found: {input_base}")
        return

    # Find first category with PDF files
    test_category = None
    test_pdf = None
    
    for category_dir in sorted(input_base.iterdir()):
        if category_dir.is_dir():
            pdf_files = list(category_dir.glob("*.pdf"))
            if pdf_files:
                test_category = category_dir.name
                test_pdf = pdf_files[0]
                break
    
    if not test_pdf:
        print("No PDF files found in any input directory")
        print(f"Please create a category folder (e.g., 'data/input/test') and add PDF files")
        return

    print(f"Testing with PDF: {test_pdf}")
    print(f"Category: {test_category}")

    # Process the PDF
    sequence_id = 1

    success = processor.process_single_pdf(str(test_pdf), test_category, sequence_id)

    if success:
        print("✅ PDF processed successfully!")
        print(f"Check data/output/{test_category}/{test_category}-001.json for the result")
    else:
        print("❌ PDF processing failed")

if __name__ == "__main__":
    main()