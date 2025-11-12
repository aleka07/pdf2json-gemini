# Quick Reference: Migration Changes

## Key Changes

### Command Line Arguments
| Before | After |
|--------|-------|
| `--section 3.1` | `--category ML` |
| `--list-files 3.1` | `--list-files ML` |
| `--resume 3.1` | `--resume ML` |

### Terminology
- **section** → **category**
- **section code** → **category code**
- Specific codes (3.1, 4.2) → Generic names (ML, IoT, security)

### Directory Structure
```
Before:                     After:
data/input/3.1/      →     data/input/ML/
data/input/3.2/      →     data/input/IoT/
data/input/4.2/      →     data/input/security/

data/output/3.1/     →     data/output/ML/
data/output/3.2/     →     data/output/IoT/
data/output/4.2/     →     data/output/security/
```

### Paper IDs
```
Before:  3.1-001, 3.1-002, 4.2-001
After:   ML-001,  ML-002,  security-001
```

### JSON Schema
**Removed:**
- `project_context` field
- `relevance_to_my_project` field

**Kept:**
- `paper_id`
- `metadata`
- `summary`
- `methodology`
- `results_and_evaluation`
- `keywords`

## Usage Examples

### Processing
```bash
# List categories
python main.py --list

# Process a category
python main.py --category ML --parallel

# Process all categories
python main.py --all --parallel

# Process single file
python main.py --file path/to/paper.pdf
```

### Exporting to CSV
```bash
# Merge JSON files per category
python merge_json_outputs.py

# Export all to CSV
python export_to_csv.py

# Export specific category
python export_to_csv.py --category paper1

# Custom output filename
python export_to_csv.py --output results.csv
```

### Complete Workflow
```bash
# 1. Process all PDFs
python main.py --all --parallel

# 2. Merge results (optional)
python merge_json_outputs.py

# 3. Export to CSV
python export_to_csv.py --output final.csv
```

## See Also
- `USAGE.md` - Detailed usage guide
- `EXPORT_GUIDE.md` - Export and CSV conversion guide
- `MIGRATION.md` - Complete migration documentation
- `README.md` - Project overview
