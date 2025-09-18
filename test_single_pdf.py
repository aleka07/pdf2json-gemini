#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from pdf_processor import PDFProcessor

def main():
    # API key from the existing test file
    API_KEY = "AIzaSyAiGsczDRLUgQirKq0sJ2Zyp2P507pvc90"

    # Initialize processor
    processor = PDFProcessor(API_KEY)

    # Test with first PDF from data/input/3.1/
    input_dir = Path("data/input/3.1")
    if not input_dir.exists():
        print(f"Input directory not found: {input_dir}")
        return

    # Get first PDF file
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in input directory")
        return

    test_pdf = pdf_files[0]
    print(f"Testing with PDF: {test_pdf}")

    # Process the PDF
    section_code = "3.1"
    sequence_id = 1

    print(f"Processing PDF: {test_pdf}")
    print(f"Section: {section_code}, Sequence ID: {sequence_id}")

    success = processor.process_single_pdf(str(test_pdf), section_code, sequence_id)

    if success:
        print("✅ PDF processed successfully!")
        print("Check data/output/3.1-001.json for the result")
    else:
        print("❌ PDF processing failed")

if __name__ == "__main__":
    main()