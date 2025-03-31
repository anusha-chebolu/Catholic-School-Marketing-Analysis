# Catholic School Marketing Analysis

## Project Overview
This project analyzes marketing materials from Catholic high schools in the Archdiocese of Indianapolis to understand representation and diversity in their promotional content. The analysis focuses on:
- Demographics and racial representation
- Gender representation
- Religious iconography and symbolism
- Marketing strategies and branding

## Project Structure
```
catholic-school-marketing-analysis/
├── config/                 # Configuration files for project settings
├── data/                  # Data directory
│   ├── raw/              # Original, immutable data (school image URLs)
│   ├── interim/          # Intermediate data (cropped faces, processed images)
│   └── processed/        # Final, canonical data sets (analysis results)
├── docs/                 # Project documentation
├── notebooks/            # Jupyter notebooks for interactive analysis
│   ├── sacred-symbols-detection.ipynb
│   └── race-detection.ipynb
├── src/                  # Source code
│   ├── data_collection/  # Scripts for scraping school websites
│   ├── image_analysis/   # Scripts for analyzing images
│   └── data_cleaning/    # Scripts for preprocessing data
├── tests/               # Unit tests
├── requirements.txt     # Project dependencies
└── README.md           # This file
```

## Analysis Components

### 1. Data Collection
- Web scraping scripts to collect image URLs from school websites
- Focuses on 11 Catholic high schools in the Archdiocese of Indianapolis
- Stores raw data in CSV format with school-specific image URLs

### 2. Image Analysis
- Face detection and demographic analysis
- Sacred symbols detection in images
- Analysis of religious iconography
- Gender representation analysis

### 3. Data Cleaning
- Preprocessing of collected images
- Face cropping and standardization
- Data validation and quality checks
- Preparation for analysis

## Setup and Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

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

## Analysis Notebooks
- `sacred-symbols-detection.ipynb`: Interactive analysis of religious symbols
- `race-detection.ipynb`: Analysis of racial representation in images

## Data Privacy and Ethics
- All analysis is performed on publicly available marketing materials
- Personal information is not collected or analyzed
- Focus is on aggregate patterns and representations
- Results are used for research purposes only
