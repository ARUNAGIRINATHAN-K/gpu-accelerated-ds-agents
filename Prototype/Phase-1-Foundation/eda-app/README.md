# DatasetIQ – Exploratory Data Analysis Tool

![DatasetIQ](image/image.png)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-black?style=flat&logo=flask)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-green?style=flat&logo=pandas)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?style=flat&logo=bootstrap)
![DataTables](https://img.shields.io/badge/DataTables-1.13.6-orange?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

## Overview

**DatasetIQ** is a lightweight web-based tool for fast exploratory data analysis (EDA). Upload your CSV or XLSX file, analyze it instantly, and explore column statistics, data types, missing values, and unique counts—all in one intuitive interface.

## Features

- 📊 **Quick Analysis** – Upload CSV/XLSX and get instant insights
- 📈 **Summary Cards** – View dataset shape, row/column counts, missing values, and file size at a glance
- 🔍 **Column Details** – Interactive table with data types, missing values, and unique value counts
- 🎛️ **Smart Filters** – Filter by data type, missing value threshold, and search columns by name
- 📥 **HTML Reports** – Download a formatted analysis report
- 🎨 **Clean UI** – Bootstrap 5 design with responsive layout

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Data Processing**: pandas, NumPy
- **Tables**: DataTables.js

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ARUNAGIRINATHAN-K/Data-Analyst-Agent.git
   cd Phase-1-Foundation/eda-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   python app.py
   ```

4. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

## Usage

1. Select a CSV or XLSX file
2. Click **Analyze**
3. View summary cards and column details
4. Use filters to explore data
5. Download the report (optional)

## File Structure

```
eda-app/
├── app.py                 # Flask application & routes
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── summary.html      # Main app UI
│   └── icon/
│       └── logo.png      # Site favicon
├── static/
│   └── js/
│       ├── summary.js    # Summary page logic
│       └── script.js     # Utility functions
└── uploads/              # User-uploaded files
```

## Supported Formats

- CSV (`.csv`)
- Excel (`.xlsx`)
- Max file size: 10 MB

## License

MIT License

## Author

[ARUNAGIRINATHAN-K](https://github.com/ARUNAGIRINATHAN-K)
