# Export Guide - JSON to CSV

После обработки PDF файлов вы можете экспортировать результаты в удобные форматы.

## Шаг 1: Объединение JSON файлов (опционально)

Если вы хотите объединить все JSON файлы каждой категории в один файл:

```bash
# Объединить все категории
python merge_json_outputs.py

# Результат: data/output/<category>/<category>_merged.json
```

**Пример вывода:**
```
✅ Merged paper1 → data/output/paper1/paper1_merged.json
✅ All available categories merged successfully
```

## Шаг 2: Экспорт в CSV

### Вариант A: Экспорт всех категорий в один CSV

```bash
# Экспорт всех категорий в один файл
python export_to_csv.py

# Результат: papers_export.csv
```

### Вариант B: Экспорт конкретной категории

```bash
# Экспорт только категории paper1
python export_to_csv.py --category paper1

# Результат: paper1_export.csv
```

### Вариант C: Экспорт из объединённых JSON файлов

```bash
# Сначала объединяем
python merge_json_outputs.py

# Затем экспортируем из объединённых файлов
python export_to_csv.py --merged

# Результат: papers_export.csv
```

### Вариант D: Пользовательское имя файла

```bash
# Экспорт с пользовательским именем
python export_to_csv.py --output my_results.csv

# Результат: my_results.csv
```

## Полный рабочий процесс

```bash
# 1. Обработка PDF файлов
python main.py --all --parallel

# 2. Объединение результатов (опционально)
python merge_json_outputs.py

# 3. Экспорт в CSV
python export_to_csv.py --output final_results.csv
```

## Структура CSV файла

CSV файл будет содержать следующие столбцы:

- `paper_id` - ID статьи (например, paper1-001)
- `metadata_title` - Название статьи
- `metadata_authors` - Авторы (разделены точкой с запятой)
- `metadata_year` - Год публикации
- `metadata_publication_venue` - Место публикации
- `metadata_doi` - DOI
- `summary_problem_statement` - Описание проблемы
- `summary_objective` - Цель статьи
- `summary_key_contribution` - Ключевой вклад
- `methodology_approach_type` - Тип подхода
- `methodology_technologies_and_protocols` - Технологии и протоколы
- `methodology_method_summary` - Краткое описание методов
- `results_and_evaluation_key_findings` - Основные результаты
- `results_and_evaluation_evaluation_metrics` - Метрики оценки
- `keywords` - Ключевые слова

## Открытие CSV файлов

### В Excel
1. Откройте Excel
2. Файл → Открыть → выберите CSV файл
3. Убедитесь, что кодировка установлена на UTF-8

### В Google Sheets
1. Откройте Google Sheets
2. Файл → Импорт → Загрузка → выберите CSV файл
3. Выберите "Автоматическое определение" для разделителя

### В Python (для анализа)
```python
import pandas as pd

# Загрузка CSV
df = pd.read_csv('papers_export.csv')

# Просмотр первых строк
print(df.head())

# Статистика
print(df['metadata_year'].value_counts())
print(df['methodology_approach_type'].value_counts())
```

## Фильтрация данных

Если вам нужны только определённые столбцы, используйте pandas:

```python
import pandas as pd

df = pd.read_csv('papers_export.csv')

# Выбрать только основные столбцы
essential_columns = [
    'paper_id',
    'metadata_title',
    'metadata_year',
    'summary_problem_statement',
    'keywords'
]

df_filtered = df[essential_columns]
df_filtered.to_csv('papers_essential.csv', index=False)
```

## Примеры использования

### Экспорт по категориям отдельно

```bash
# Экспорт каждой категории в отдельный файл
for category in data/output/*/; do
    category_name=$(basename "$category")
    python export_to_csv.py --category "$category_name"
done
```

### Быстрый анализ в командной строке

```bash
# Подсчёт количества статей по годам
cut -d',' -f4 papers_export.csv | sort | uniq -c

# Просмотр всех технологий
cut -d',' -f11 papers_export.csv | sort | uniq
```

## Troubleshooting

### Проблема: Неправильная кодировка в Excel
**Решение:** Откройте файл в текстовом редакторе, сохраните как UTF-8 BOM.

### Проблема: Слишком много столбцов
**Решение:** Используйте pandas для выбора нужных столбцов (см. пример выше).

### Проблема: Списки в ячейках выглядят странно
**Решение:** Элементы списков автоматически объединяются через точку с запятой (;).

## Дополнительные команды

```bash
# Посмотреть, сколько JSON файлов в категории
ls -l data/output/paper1/*.json | wc -l

# Проверить размер CSV файла
ls -lh papers_export.csv

# Посмотреть первые несколько строк CSV
head -n 5 papers_export.csv
```
