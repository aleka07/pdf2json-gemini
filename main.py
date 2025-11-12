#!/usr/bin/env python3
"""
PDF to JSON Processing Tool - Main Script

A universal tool for processing scientific PDF papers using Google's Gemini API
to generate structured JSON data.

This script orchestrates the complete PDF processing workflow:
1. Process PDFs from data/input/<category>/ directories
2. Generate JSON files according to the schema from prompt.md
3. Save results to data/output/<category>/
4. Provide comprehensive logging and progress reporting

Usage:
    python main.py --category ML           # Process specific category
    python main.py --all                   # Process all categories
    python main.py --file path/to/file.pdf # Process single file
    python main.py --list                  # List available categories
    
See USAGE.md for detailed examples and advanced features.
"""

import argparse
import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from pdf_processor import PDFProcessor

# Load environment variables from .env file
load_dotenv()

# API key from environment variable
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ Error: GEMINI_API_KEY environment variable not set!")
    print("💡 Options to fix this:")
    print("   1. Set environment variable: export GEMINI_API_KEY='your-api-key-here'")
    print("   2. Create .env file: cp .env.example .env and edit it")
    print("   3. Get API key from: https://aistudio.google.com/app/apikey")
    sys.exit(1)

def get_category_input_dir(category_code: str) -> Path:
    """Return the input directory path for the given category code."""
    return Path("data/input") / category_code

def find_available_categories():
    """Find all available category directories."""
    input_dir = Path("data/input")
    if not input_dir.exists():
        return []

    categories = []
    for item in sorted(input_dir.iterdir(), key=lambda x: x.name.lower()):
        if not item.is_dir():
            continue

        # Check if directory has PDF files
        pdf_files = list(item.glob("*.pdf"))
        if pdf_files:
            categories.append((item.name, len(pdf_files)))

    return categories

def process_category(processor, category_code, use_resume=False, start_from=1, resume_method="smart", parallel=False, workers=3):
    """Process all PDFs in a specific category."""
    directory_path = str(get_category_input_dir(category_code))

    if not Path(directory_path).exists():
        print(f"❌ Category directory not found: {directory_path}")
        return False

    print(f"\n🔄 Processing Category: {category_code}")
    print(f"📁 Directory: {directory_path}")

    if parallel:
        print(f"🚀 Using PARALLEL processing with {workers} workers")
        print(f"⚡ This will be MUCH faster!")
    elif use_resume:
        print(f"🔄 Using {resume_method} resume functionality")
        if start_from > 1:
            print(f"📍 Starting from sequence {start_from}")

    # Process the directory
    if parallel:
        # Parallel processing (fastest)
        results = processor.process_pdfs_parallel(directory_path, category_code, workers)
    elif use_resume:
        # Resume processing
        if resume_method == "simple":
            results = processor.process_pdfs_in_directory_with_resume(directory_path, category_code, start_from)
        else:  # smart method
            results = processor.process_pdfs_with_resume(directory_path, category_code, start_from)
    else:
        # Sequential processing
        results = processor.process_pdfs_in_directory(directory_path, category_code)

    if results["success"]:
        print(f"\n✅ Category {category_code} completed successfully!")
        print(f"📊 Processed: {results['processed']}/{results['total_files']} files")
        if results['failed'] > 0:
            print(f"⚠️  Failed: {results['failed']} files")
        if results.get('skipped', 0) > 0:
            print(f"⏭️  Skipped: {results['skipped']} files")
        if results.get('parallel_workers'):
            print(f"🚀 Used {results['parallel_workers']} parallel workers")
    else:
        print(f"\n❌ Category {category_code} failed: {results.get('error', 'Unknown error')}")
        return False

    return True

def process_single_file(processor, file_path, category_code=None, sequence_id=None):
    """Process a single PDF file."""
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    if not file_path.suffix.lower() == '.pdf':
        print(f"❌ Not a PDF file: {file_path}")
        return False

    # Auto-detect category if not provided
    if category_code is None:
        try:
            relative = file_path.relative_to(Path("data/input"))
            if relative.parts:
                candidate = relative.parts[0]
                if get_category_input_dir(candidate).exists():
                    category_code = candidate
        except ValueError:
            pass

        if category_code is None:
            # Fall back to scanning path parts for a matching input directory
            for part in file_path.parts:
                if get_category_input_dir(part).exists():
                    category_code = part
                    break

        if category_code is None:
            category_code = "misc"  # Default category

    # Auto-detect sequence ID if not provided
    if sequence_id is None:
        sequence_id = 1

    print(f"\n🔄 Processing single file:")
    print(f"📄 File: {file_path}")
    print(f"🏷️  Category: {category_code}")
    print(f"🔢 Sequence: {sequence_id}")

    success = processor.process_single_pdf(str(file_path), category_code, sequence_id)

    if success:
        paper_id = f"{category_code}-{sequence_id:03d}"
        print(f"✅ File processed successfully!")
        print(f"📋 Output: data/output/{category_code}/{paper_id}.json")
    else:
        print(f"❌ File processing failed")
        return False

    return True

def main():
    parser = argparse.ArgumentParser(
        description="Process PDF papers to generate structured JSON data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py --list                                # List available categories
    python main.py --list-files ML                       # List files in category 'ML' with numbers and status
    python main.py --category ML --parallel              # Process category 'ML' in PARALLEL (3x faster!)
    python main.py --category IoT --parallel --workers 5 # Use 5 parallel workers (max speed)
    python main.py --category security --use-resume      # Process category 'security' with smart resume
    python main.py --resume ML --start-from 26           # Resume category 'ML' from sequence 26
    python main.py --all --parallel                      # Process all categories in parallel (fastest)
    python main.py --file paper.pdf                      # Process a single PDF file
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--category", type=str, help="Process specific category (e.g., ML, IoT, security)")
    group.add_argument("--all", action="store_true", help="Process all available categories")
    group.add_argument("--file", type=str, help="Process single PDF file")
    group.add_argument("--list", action="store_true", help="List available categories")
    group.add_argument("--list-files", type=str, help="List files in a specific category with numbers")
    group.add_argument("--resume", type=str, help="Resume processing from a specific category")

    parser.add_argument("--sequence-id", type=int, help="Sequence ID for single file processing")
    parser.add_argument("--start-from", type=int, help="Start processing from specific sequence number (for resume)")
    parser.add_argument("--use-resume", action="store_true", help="Use smart resume functionality that skips already processed files")
    parser.add_argument("--resume-method", choices=["smart", "simple"], default="smart", help="Resume method: 'smart' (sequence-based) or 'simple' (filename-based)")
    parser.add_argument("--parallel", action="store_true", help="Use parallel processing for faster execution")
    parser.add_argument("--workers", type=int, default=3, help="Number of parallel workers (default: 3, max recommended: 5)")

    args = parser.parse_args()

    # List available categories
    if args.list:
        available_categories = find_available_categories()

        if not available_categories:
            print("❌ No categories with PDF files found in data/input/")
            return 1

        print("📋 Available categories:")
        for category, count in available_categories:
            print(f"   {category} ({count} PDFs)")

        return 0

    # List files in specific category
    if args.list_files:
        directory = get_category_input_dir(args.list_files)
        directory_path = str(directory)

        if not directory.exists():
            print(f"❌ Category directory not found: {directory_path}")
            available_categories = find_available_categories()
            if available_categories:
                print("📋 Available categories:")
                print(", ".join(category for category, _ in available_categories))
            return 1

        pdf_files = sorted(list(directory.glob("*.pdf")), key=lambda x: x.name.lower())

        if not pdf_files:
            print(f"❌ No PDF files found in category {args.list_files}")
            return 1

        print(f"📋 Files in category {args.list_files}:")
        print(f"📁 Directory: {directory_path}")
        print(f"🔢 Total files: {len(pdf_files)}")
        print()

        for idx, pdf_file in enumerate(pdf_files, 1):
            paper_id = f"{args.list_files}-{idx:03d}"

            # Check if already processed
            output_file = Path(f"data/output/{args.list_files}/{paper_id}.json")
            status = "✅ Processed" if output_file.exists() else "⏳ Pending"

            print(f"  {idx:2d}. {pdf_file.name}")
            print(f"      📋 Paper ID: {paper_id}")
            print(f"      📊 Status: {status}")
            print()

        return 0

    # Initialize processor
    print("🚀 Initializing PDF processor...")
    try:
        processor = PDFProcessor(API_KEY)
        print("✅ PDF processor initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize PDF processor: {str(e)}")
        return 1

    success = True

    # Process single file
    if args.file:
        success = process_single_file(processor, args.file, sequence_id=args.sequence_id)

    # Process specific category
    elif args.category:
        start_from = args.start_from or 1
        success = process_category(processor, args.category, args.use_resume, start_from, args.resume_method, args.parallel, args.workers)

    # Resume processing from a specific category
    elif args.resume:
        start_from = args.start_from or 1
        print(f"🔄 Resuming processing for category {args.resume}")
        success = process_category(processor, args.resume, True, start_from, args.resume_method, args.parallel, args.workers)

    # Process all categories
    elif args.all:
        available_categories = find_available_categories()

        if not available_categories:
            print("❌ No categories with PDF files found in data/input/")
            return 1

        print(f"🔄 Processing {len(available_categories)} categories...")

        all_success = True
        for category, count in available_categories:
            category_success = process_category(processor, category, args.use_resume, 1, args.resume_method, args.parallel, args.workers)
            if not category_success:
                all_success = False

        success = all_success

        if success:
            print("\n🎉 All categories processed successfully!")
        else:
            print("\n⚠️  Some categories failed to process completely")

    if success:
        print("\n✅ Processing completed successfully!")
        return 0
    else:
        print("\n❌ Processing failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
