# Catholic School Marketing Analysis

This project analyzes marketing materials from Catholic schools to understand representation and diversity in their promotional content.

## Project Structure

```
catholic-school-marketing-analysis/
├── config/                 # Configuration files
├── data/                  # Data directory
│   ├── raw/              # Original, immutable data
│   ├── interim/          # Intermediate data that has been transformed
│   └── processed/        # Final, canonical data sets
├── docs/                 # Documentation
├── notebooks/            # Jupyter notebooks for analysis
├── src/                  # Source code
│   ├── data_collection/  # Data collection scripts
│   ├── image_analysis/   # Image analysis scripts
│   └── data_cleaning/    # Data cleaning scripts
└── tests/               # Unit tests
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Components

### Data Collection
- Scripts for scraping school websites and collecting image URLs
- Located in `src/data_collection/`

### Image Analysis
- Scripts for analyzing images for sacred symbols and racial diversity
- Located in `src/image_analysis/`
- Jupyter notebooks for interactive analysis in `notebooks/`

### Data Cleaning
- Scripts for cleaning and preprocessing the collected data
- Located in `src/data_cleaning/`

## Usage

1. Data Collection:
```bash
python src/data_collection/image-scrapping-1.py
python src/data_collection/image-scrapping-2.py
```

2. Data Cleaning:
```bash
python src/data_cleaning/data-cleaning.py
```

3. Image Analysis:
```bash
python src/image_analysis/image-analysis.py
```
