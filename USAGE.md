# Usage Guide

This guide shows how to use the PDF to JSON processing tool for any research domain.

## Setup

1. **Get your Gemini API key**
   - Visit: https://aistudio.google.com/app/apikey
   - Create a new API key
   - Copy it for next step

2. **Configure API key**
   ```bash
   # Option 1: Environment variable
   export GEMINI_API_KEY='your-api-key-here'
   
   # Option 2: .env file (recommended)
   echo "GEMINI_API_KEY=your-api-key-here" > .env
   ```

3. **Install dependencies** (if needed)
   ```bash
   pip install google-generativeai python-dotenv
   ```

## Organizing Your Papers

Create category folders under `data/input/`:

```bash
# Example categories
mkdir -p data/input/ML              # Machine Learning
mkdir -p data/input/IoT             # Internet of Things
mkdir -p data/input/security        # Security
mkdir -p data/input/blockchain      # Blockchain
mkdir -p data/input/computer-vision # Computer Vision
mkdir -p data/input/NLP             # Natural Language Processing

# Or use your own categories
mkdir -p data/input/physics
mkdir -p data/input/chemistry
mkdir -p data/input/biology
```

Place your PDF files in the appropriate folders. The tool will automatically detect and process them.

## Basic Commands

### List available categories
```bash
python main.py --list
```

Output example:
```
📋 Available categories:
   ML (15 PDFs)
   IoT (8 PDFs)
   security (12 PDFs)
```

### List files in a category
```bash
python main.py --list-files ML
```

Output shows each file with its sequence number and processing status.

### Process a single category
```bash
# Sequential processing (default)
python main.py --category ML

# Parallel processing (3x faster, recommended)
python main.py --category ML --parallel

# Maximum speed with 5 workers
python main.py --category IoT --parallel --workers 5
```

### Process all categories
```bash
# Process all categories sequentially
python main.py --all

# Process all categories in parallel (fastest)
python main.py --all --parallel
```

### Process a single file
```bash
python main.py --file data/input/ML/some-paper.pdf
```

## Advanced Features

### Resume Processing

If processing was interrupted, you can resume from where you left off:

```bash
# Resume from a specific sequence number
python main.py --resume ML --start-from 10

# Use smart resume (automatically skips processed files)
python main.py --category security --use-resume
```

### Performance Options

- **Sequential mode**: Processes one file at a time (~45 seconds per PDF)
- **Parallel mode**: Processes multiple files simultaneously (~15 seconds per PDF with 3 workers)

```bash
# Use 3 parallel workers (default)
python main.py --category ML --parallel

# Use 5 parallel workers (maximum recommended)
python main.py --category ML --parallel --workers 5
```

## Output Structure

Generated JSON files follow this structure:

```json
{
  "paper_id": "ML-001",
  "metadata": {
    "title": "Paper Title",
    "authors": ["Author 1", "Author 2"],
    "year": 2023,
    "publication_venue": "Conference Name",
    "doi": "10.1234/example"
  },
  "summary": {
    "problem_statement": "One-sentence problem description",
    "objective": "Main goal of the paper",
    "key_contribution": "Most important finding"
  },
  "methodology": {
    "approach_type": "System Architecture",
    "technologies_and_protocols": ["TensorFlow", "PyTorch"],
    "method_summary": "Brief description of methods"
  },
  "results_and_evaluation": {
    "key_findings": [
      "Finding 1",
      "Finding 2"
    ],
    "evaluation_metrics": ["Accuracy (%)", "F1-Score"]
  },
  "keywords": ["keyword1", "keyword2", "keyword3"]
}
```

## Customizing the Schema

To customize the JSON schema for your needs, edit `prompt.md`:

1. Open `prompt.md`
2. Modify the JSON schema section
3. Add or remove fields as needed
4. Update field descriptions
5. Save and process your PDFs

The Gemini AI will generate JSON according to your custom schema.

## Logs and Monitoring

All processing activities are logged:

- **Location**: `logs/` directory
- **Format**: `processing_<category>_<timestamp>.log`
- **Contents**: Detailed progress, errors, and completion statistics

Check logs if you encounter issues or want to review processing history.

## Best Practices

1. **Organize by topic**: Create clear, descriptive category names
2. **Use parallel processing**: Much faster for large batches
3. **Check logs**: Review logs after processing to catch any errors
4. **Backup outputs**: Keep backups of generated JSON files
5. **Resume on failure**: Use `--use-resume` to continue interrupted processing

## Troubleshooting

### API Key Issues
```bash
# Verify API key is set
echo $GEMINI_API_KEY

# Or check .env file
cat .env
```

### No PDFs Found
- Ensure PDFs are in `data/input/<category>/` folders
- Check file extensions are `.pdf` (lowercase)
- Use `--list` to see detected categories

### Processing Fails
- Check internet connection (API requires network)
- Verify API key is valid
- Review logs in `logs/` directory
- Try processing a single file first with `--file`

### Slow Processing
- Use `--parallel` flag for faster processing
- Increase workers: `--workers 5`
- Check internet speed (uploads PDFs to Gemini API)

## Examples by Use Case

### Academic Research Literature Review
```bash
mkdir -p data/input/related-work
# Add papers to the folder
python main.py --category related-work --parallel
```

### Conference Paper Analysis
```bash
mkdir -p data/input/ICML-2024
mkdir -p data/input/NeurIPS-2024
python main.py --all --parallel
```

### Technology Survey
```bash
mkdir -p data/input/edge-computing
mkdir -p data/input/5G-networks
mkdir -p data/input/quantum-computing
python main.py --all --parallel --workers 5
```

### Systematic Review
```bash
mkdir -p data/input/phase1-screening
mkdir -p data/input/phase2-analysis
python main.py --category phase1-screening --parallel
python main.py --category phase2-analysis --parallel
```
