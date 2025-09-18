# Digital Twin PDF Processing Project

This project processes scientific PDF papers using Google's Gemini API to generate structured JSON data for Digital Twin research analysis.

## Quick Start

```bash
# Activate environment
source .venv/bin/activate

# List available sections
python main.py --list

# Process a specific section
python main.py --section 3.1

# Process a single file
python main.py --file path/to/paper.pdf

# Process all sections
python main.py --all
```

## Project Structure

```
dt-report-2025/
├── data/
│   ├── input/
│   │   ├── 3.1/           # PDF papers for section 3.1
│   │   └── 3.2/           # PDF papers for section 3.2
│   └── output/
│       ├── 3.1/           # Generated JSON files for section 3.1
│       └── 3.2/           # Generated JSON files for section 3.2
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
- Supports processing single files, sections, or all sections
- Comprehensive logging and progress reporting
- Automatic section detection from file paths

### 3. JSON Schema (`prompt.md`)
Each generated JSON includes:
- `paper_id`: Format "section-sequence" (e.g., "3.1-001")
- `project_context`: Section code and Russian description
- `metadata`: Title, authors, year, venue, DOI
- `summary`: Problem statement, objective, key contribution
- `methodology`: Approach type, technologies, method summary
- `results_and_evaluation`: Key findings and evaluation metrics
- `relevance_to_my_project`: Direct applicability, relevance score (1-5), cited ideas
- `keywords`: 5-7 most important keywords

## Project Sections

- **3.1**: Определение требований к системе сбора данных
- **3.2**: Проведение экспериментальных работ по интеграции датчиков и устройств IIoT
- **3.3**: Разработка инфраструктуры для хранения данных
- **4.1**: Сбор и подготовка данных
- **4.2**: Разработка алгоритмов машинного обучения
- **4.3**: Валидация и тестирование моделей, различных сценариев
- **4.4**: Анализ и выявление паттернов, обнаружение аномалий
- **4.5**: Оптимизация производственных процессов и прогнозирование будущих событий

## Digital Twin Context

This research focuses on an industrial Digital Twin system:
- **Hardware**: Saiman brand meters in Kazakhstan
- **Edge**: ESP32 microcontrollers → Raspberry Pi 5 gateway
- **Communication**: MQTT over Wi-Fi
- **Cloud Stack**: Mosquitto (MQTT) → Telegraf → InfluxDB
- **Goal**: Machine Learning for anomaly detection, process optimization, prediction

## Features

- ✅ **Individual Processing**: Each PDF processed separately with own API request
- ✅ **Automatic Cleanup**: Files deleted from cloud immediately after processing
- ✅ **Sequential Processing**: One PDF at a time to avoid API overload
- ✅ **Structured Output**: JSON files follow exact schema requirements
- ✅ **Section Organization**: Output mirrors input directory structure
- ✅ **Comprehensive Logging**: Full audit trail of all operations
- ✅ **Error Handling**: Robust error handling prevents single failures from stopping process
- ✅ **Progress Reporting**: Real-time status and completion statistics

## Dependencies

- **Python 3.12**
- **google-generativeai**: Main package for Gemini API integration
- **Virtual environment**: Pre-configured in `.venv/`

## Notes

- API key currently hardcoded for development (should be moved to environment variable for production)
- Each PDF takes ~30-45 seconds to process due to Gemini API processing time
- Files are automatically deleted from Gemini cloud storage after processing
- JSON output includes relevance scoring and direct applicability analysis for the Digital Twin project