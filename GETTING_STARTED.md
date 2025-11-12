# Getting Started

Welcome! This guide will help you quickly set up and start processing PDF papers.

## Step 1: Setup API Key

Get your Gemini API key from: https://aistudio.google.com/app/apikey

Then set it up:

```bash
# Quick setup (temporary)
export GEMINI_API_KEY='your-api-key-here'

# Or create .env file (persistent, recommended)
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

## Step 2: Organize Your PDFs

Create folders for your paper categories:

```bash
# Example: Machine Learning research
mkdir -p data/input/ML

# Example: IoT papers
mkdir -p data/input/IoT

# Example: Security papers  
mkdir -p data/input/security
```

Place your PDF files in the appropriate folders.

## Step 3: Process Papers

### Option A: Process Everything (Fast & Easy)

```bash
# Process all categories with parallel processing (fastest)
python main.py --all --parallel
```

### Option B: Process One Category

```bash
# List available categories first
python main.py --list

# Process a specific category
python main.py --category ML --parallel
```

### Option C: Test with Single File

```bash
# Test with one file first
python main.py --file data/input/ML/some-paper.pdf
```

## Step 4: Check Results

Your JSON files will be in:
```
data/output/ML/ML-001.json
data/output/ML/ML-002.json
data/output/IoT/IoT-001.json
...
```

## Common Commands

```bash
# List all categories
python main.py --list

# List files in a category with status
python main.py --list-files ML

# Process with maximum speed (5 parallel workers)
python main.py --category ML --parallel --workers 5

# Resume if interrupted
python main.py --resume ML --start-from 10
```

## Troubleshooting

### "API key not set" error
```bash
# Verify API key is set
echo $GEMINI_API_KEY

# Or check .env file
cat .env
```

### "No categories found" error
```bash
# Create a category folder and add PDFs
mkdir -p data/input/test
cp your-paper.pdf data/input/test/

# Then list again
python main.py --list
```

### Processing is slow
```bash
# Use parallel processing for speed
python main.py --category ML --parallel --workers 5
```

## Next Steps

- Read [USAGE.md](USAGE.md) for advanced features
- See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for command cheat sheet
- Check [prompt.md](prompt.md) to customize JSON schema
- Review logs in `logs/` folder for detailed information

## Example Workflow

```bash
# 1. Setup
export GEMINI_API_KEY='your-key'

# 2. Organize papers
mkdir -p data/input/ML
cp *.pdf data/input/ML/

# 3. Check what you have
python main.py --list
python main.py --list-files ML

# 4. Process everything
python main.py --all --parallel

# 5. Check results
ls data/output/ML/
cat data/output/ML/ML-001.json
```

That's it! You're ready to process your papers. 🚀
