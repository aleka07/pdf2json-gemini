#!/usr/bin/env python3
"""
Main script for PDF processing workflow.

This script orchestrates the complete PDF processing workflow:
1. Process PDFs from data/input/ directories
2. Generate JSON files according to the schema from prompt.md
3. Save results to data/output/
4. Provide comprehensive logging and progress reporting

Usage:
    python main.py --section 3.1           # Process specific section
    python main.py --all                   # Process all sections
    python main.py --file path/to/file.pdf # Process single file
"""

import argparse
import sys
import json
from pathlib import Path
from pdf_processor import PDFProcessor

# API key from testing file
API_KEY = "AIzaSyAiGsczDRLUgQirKq0sJ2Zyp2P507pvc90"

# Section descriptions from prompt.md
SECTION_DESCRIPTIONS = {
    "3.1": "Определение требований к системе сбора данных.",
    "3.2": "Проведение экспериментальных работ по интеграции датчиков и устройств IIoT.",
    "3.3": "Разработка инфраструктуры для хранения данных.",
    "4.1": "Сбор и подготовка данных.",
    "4.2": "Разработка алгоритмов машинного обучения.",
    "4.3": "Валидация и тестирование моделей, различных сценариев.",
    "4.4": "Анализ и выявление паттернов, обнаружение аномалий.",
    "4.5": "Оптимизация производственных процессов и прогнозирование будущих событий."
}

def find_available_sections():
    """Find all available section directories."""
    input_dir = Path("data/input")
    if not input_dir.exists():
        return []

    sections = []
    for item in input_dir.iterdir():
        if item.is_dir() and item.name in SECTION_DESCRIPTIONS:
            # Check if directory has PDF files
            pdf_files = list(item.glob("*.pdf"))
            if pdf_files:
                sections.append((item.name, len(pdf_files)))

    return sorted(sections)

def process_section(processor, section_code, use_resume=False, start_from=1, resume_method="smart"):
    """Process all PDFs in a specific section."""
    directory_path = f"data/input/{section_code}"

    if not Path(directory_path).exists():
        print(f"❌ Section directory not found: {directory_path}")
        return False

    print(f"\n🔄 Processing Section {section_code}: {SECTION_DESCRIPTIONS.get(section_code, 'Unknown section')}")
    print(f"📁 Directory: {directory_path}")

    if use_resume:
        print(f"🔄 Using {resume_method} resume functionality")
        if start_from > 1:
            print(f"📍 Starting from sequence {start_from}")

    # Process the directory
    if use_resume:
        if resume_method == "simple":
            results = processor.process_pdfs_in_directory_with_resume(directory_path, section_code, start_from)
        else:  # smart method
            results = processor.process_pdfs_with_resume(directory_path, section_code, start_from)
    else:
        results = processor.process_pdfs_in_directory(directory_path, section_code)

    if results["success"]:
        print(f"\n✅ Section {section_code} completed successfully!")
        print(f"📊 Processed: {results['processed']}/{results['total_files']} files")
        if results['failed'] > 0:
            print(f"⚠️  Failed: {results['failed']} files")
        if results.get('skipped', 0) > 0:
            print(f"⏭️  Skipped: {results['skipped']} files")
    else:
        print(f"\n❌ Section {section_code} failed: {results.get('error', 'Unknown error')}")
        return False

    return True

def process_single_file(processor, file_path, section_code=None, sequence_id=None):
    """Process a single PDF file."""
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    if not file_path.suffix.lower() == '.pdf':
        print(f"❌ Not a PDF file: {file_path}")
        return False

    # Auto-detect section if not provided
    if section_code is None:
        # Try to extract from path (e.g., data/input/3.1/file.pdf)
        path_parts = file_path.parts
        for part in path_parts:
            if part in SECTION_DESCRIPTIONS:
                section_code = part
                break

        if section_code is None:
            section_code = "misc"  # Default section

    # Auto-detect sequence ID if not provided
    if sequence_id is None:
        sequence_id = 1

    print(f"\n🔄 Processing single file:")
    print(f"📄 File: {file_path}")
    print(f"🏷️  Section: {section_code}")
    print(f"🔢 Sequence: {sequence_id}")

    success = processor.process_single_pdf(str(file_path), section_code, sequence_id)

    if success:
        paper_id = f"{section_code}-{sequence_id:03d}"
        print(f"✅ File processed successfully!")
        print(f"📋 Output: data/output/{section_code}/{paper_id}.json")
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
    python main.py --list                                 # List available sections
    python main.py --list-files 3.1                      # List files in section 3.1 with numbers and status
    python main.py --section 3.1                         # Process all PDFs in section 3.1
    python main.py --section 3.1 --use-resume           # Process section 3.1 with smart resume (skip already processed)
    python main.py --resume 3.1 --start-from 26         # Resume section 3.1 from sequence 26
    python main.py --all --use-resume                    # Process all sections with smart resume
    python main.py --file paper.pdf                     # Process a single PDF file
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--section", type=str, help="Process specific section (e.g., 3.1)")
    group.add_argument("--all", action="store_true", help="Process all available sections")
    group.add_argument("--file", type=str, help="Process single PDF file")
    group.add_argument("--list", action="store_true", help="List available sections")
    group.add_argument("--list-files", type=str, help="List files in a specific section with numbers")
    group.add_argument("--resume", type=str, help="Resume processing from a specific section")

    parser.add_argument("--sequence-id", type=int, help="Sequence ID for single file processing")
    parser.add_argument("--start-from", type=int, help="Start processing from specific sequence number (for resume)")
    parser.add_argument("--use-resume", action="store_true", help="Use smart resume functionality that skips already processed files")
    parser.add_argument("--resume-method", choices=["smart", "simple"], default="smart", help="Resume method: 'smart' (sequence-based) or 'simple' (filename-based)")

    args = parser.parse_args()

    # List available sections
    if args.list:
        available_sections = find_available_sections()

        if not available_sections:
            print("❌ No sections with PDF files found in data/input/")
            return 1

        print("📋 Available sections:")
        for section, count in available_sections:
            description = SECTION_DESCRIPTIONS.get(section, "Unknown section")
            print(f"   {section}: {description} ({count} PDFs)")

        return 0

    # List files in specific section
    if args.list_files:
        if args.list_files not in SECTION_DESCRIPTIONS:
            print(f"❌ Unknown section: {args.list_files}")
            print(f"Available sections: {', '.join(SECTION_DESCRIPTIONS.keys())}")
            return 1

        directory_path = f"data/input/{args.list_files}"
        directory = Path(directory_path)

        if not directory.exists():
            print(f"❌ Section directory not found: {directory_path}")
            return 1

        pdf_files = sorted(list(directory.glob("*.pdf")), key=lambda x: x.name.lower())

        if not pdf_files:
            print(f"❌ No PDF files found in section {args.list_files}")
            return 1

        print(f"📋 Files in section {args.list_files}:")
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

    # Process specific section
    elif args.section:
        if args.section not in SECTION_DESCRIPTIONS:
            print(f"❌ Unknown section: {args.section}")
            print(f"Available sections: {', '.join(SECTION_DESCRIPTIONS.keys())}")
            return 1

        start_from = args.start_from or 1
        success = process_section(processor, args.section, args.use_resume, start_from, args.resume_method)

    # Resume processing from a specific section
    elif args.resume:
        if args.resume not in SECTION_DESCRIPTIONS:
            print(f"❌ Unknown section: {args.resume}")
            print(f"Available sections: {', '.join(SECTION_DESCRIPTIONS.keys())}")
            return 1

        start_from = args.start_from or 1
        print(f"🔄 Resuming processing for section {args.resume}")
        success = process_section(processor, args.resume, True, start_from, args.resume_method)

    # Process all sections
    elif args.all:
        available_sections = find_available_sections()

        if not available_sections:
            print("❌ No sections with PDF files found in data/input/")
            return 1

        print(f"🔄 Processing {len(available_sections)} sections...")

        all_success = True
        for section, count in available_sections:
            section_success = process_section(processor, section, args.use_resume, 1, args.resume_method)
            if not section_success:
                all_success = False

        success = all_success

        if success:
            print("\n🎉 All sections processed successfully!")
        else:
            print("\n⚠️  Some sections failed to process completely")

    if success:
        print("\n✅ Processing completed successfully!")
        return 0
    else:
        print("\n❌ Processing failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())