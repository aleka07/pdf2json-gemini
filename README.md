# PDF to JSON Processing Tool

A universal tool for processing scientific PDF papers using Google's Gemini API to generate structured JSON data.

> 📚 **New user?** Start with **[GETTING_STARTED.md](GETTING_STARTED.md)** for a step-by-step guide!

## Quick Start

```bash
# 1. Set up API key
export GEMINI_API_KEY='your-api-key-here'

# 2. Activate environment (if using virtual environment)
source .venv/bin/activate

# 3. List available categories
python main.py --list

# Process a specific category
python main.py --category ML

# Process a single file
python main.py --file path/to/paper.pdf

# Process all categories
python main.py --all
```

## Project Structure

```
pdf2json-gemini/
├── data/
│   ├── input/
│   │   ├── ML/            # PDF papers for Machine Learning category
│   │   ├── IoT/           # PDF papers for IoT category
│   │   └── security/      # PDF papers for Security category
│   └── output/
│       ├── ML/            # Generated JSON files for ML category
│       ├── IoT/           # Generated JSON files for IoT category
│       └── security/      # Generated JSON files for Security category
├── main.py                # Main orchestration script
├── pdf_processor.py       # Core PDF processing class
├── test_single_pdf.py     # Single file testing script
├── prompt.md              # JSON schema and AI instructions
└── testing-gemini.py      # API connectivity test
```

## Core Components

### 1. PDFProcessor Class (`pdf_processor.py`)
- Handles PDF upload to Gemini API
- Processes PDFs with Gemini 2.5 Flash model
- Generates structured JSON according to schema
- Automatically cleans up cloud files after processing
- Supports both single file and batch processing

### 2. Main Script (`main.py`)
- Command-line interface for all operations
- Supports processing single files, categories, or all categories
- Comprehensive logging and progress reporting
- Automatic category detection from file paths

### 3. JSON Schema (`prompt.md`)
Each generated JSON includes:
- `paper_id`: Format "category-sequence" (e.g., "ML-001", "IoT-005")
- `metadata`: Title, authors, year, venue, DOI
- `summary`: Problem statement, objective, key contribution
- `methodology`: Approach type, technologies, method summary
- `results_and_evaluation`: Key findings and evaluation metrics
- `keywords`: 5-7 most important keywords

## How to Organize Your Papers

Create subdirectories under `data/input/` for different categories:

```bash
mkdir -p data/input/ML        # Machine Learning papers
mkdir -p data/input/IoT       # IoT papers
mkdir -p data/input/security  # Security papers
mkdir -p data/input/blockchain # Blockchain papers
# ... or any category name you want
```

Place your PDF files in the appropriate category folders. The tool will automatically:
- Detect all categories with PDF files
- Generate sequential IDs for papers in each category
- Create corresponding output folders with JSON files

## Features

- ✅ **Universal & Flexible**: Works with any research domain or topic
- ✅ **Individual Processing**: Each PDF processed separately with own API request
- ✅ **Automatic Cleanup**: Files deleted from cloud immediately after processing
- ✅ **Parallel Processing**: Process multiple PDFs simultaneously for speed
- ✅ **Structured Output**: JSON files follow customizable schema
- ✅ **Category Organization**: Flexible folder-based organization
- ✅ **Comprehensive Logging**: Full audit trail of all operations
- ✅ **Error Handling**: Robust error handling prevents single failures from stopping process
- ✅ **Progress Reporting**: Real-time status and completion statistics
- ✅ **Resume Capability**: Continue interrupted processing from where you left off

## Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - 🚀 Start here! Quick setup guide for new users
- **[USAGE.md](USAGE.md)** - Comprehensive usage guide with examples
- **[EXPORT_GUIDE.md](EXPORT_GUIDE.md)** - 📊 How to merge JSON and export to CSV
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick command reference
- **[MIGRATION.md](MIGRATION.md)** - Details about changes from previous version
- **[prompt.md](prompt.md)** - JSON schema and AI instructions (customizable)

## Setup

### 1. API Key Configuration

**Option 1: Environment Variable**
```bash
export GEMINI_API_KEY='your-actual-api-key-here'
```

**Option 2: .env File (Recommended)**
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your API key:
# GEMINI_API_KEY=your-actual-api-key-here
```

**Get API Key:**
- Visit: https://aistudio.google.com/app/apikey
- Create new API key
- Copy and use in your configuration

### 2. Dependencies
- **Python 3.12**
- **google-generativeai**: Main package for Gemini API integration
- **python-dotenv**: For .env file support
- **Virtual environment**: Pre-configured in `.venv/`

## Performance

- **Sequential mode**: ~45 seconds per PDF
- **Parallel mode** (recommended): ~15 seconds per PDF with 3 workers
- **Max speed**: Use `--parallel --workers 5` for fastest processing

## Command Examples

### Processing PDFs
```bash
# List all available categories
python main.py --list

# Process all categories in parallel (fastest)
python main.py --all --parallel

# Process specific category
python main.py --category paper1 --parallel
```

### Exporting Results
```bash
# Merge JSON files (optional)
python merge_json_outputs.py

# Export all to CSV
python export_to_csv.py

# Export specific category
python export_to_csv.py --category paper1 --output results.csv
```

### Complete Workflow
```bash
# 1. Process PDFs
python main.py --all --parallel

# 2. Merge results (optional)
python merge_json_outputs.py

# 3. Export to CSV
python export_to_csv.py --output final_results.csv
```

## Security Notes

- ✅ API key uses environment variables (secure)
- ✅ Files automatically deleted from Gemini cloud storage after processing
- ✅ No sensitive data committed to repository
- ✅ Generic schema - adaptable to any research domain