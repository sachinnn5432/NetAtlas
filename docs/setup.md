# NetAtlas Installation, Environment Setup & Deployment Guide

## 1. Prerequisites

- **Python Version:** Python 3.11, 3.12, 3.13, or 3.14 (64-bit).
- **Package Manager:** `pip` (Python package installer).
- **Operating System:** Windows, macOS, or Linux.
- **Optional Tools:** Microsoft Power BI Desktop (for opening `.csv` reports), Jupyter Lab / VS Code (for running `.ipynb` notebooks).

---

## 2. Quickstart Installation

### Step 1: Clone or Navigate to the Repository
```bash
cd final_mini_project
```

### Step 2: Install Required Dependencies
```bash
pip install -r requirements.txt
```

Verified core dependencies pinned in `requirements.txt`:
- `geopandas`, `shapely`, `networkx`, `pandas`, `numpy`, `pyarrow`
- `Flask`, `flask-cors`, `SQLAlchemy`, `requests`, `pydantic`
- `folium`, `plotly`, `matplotlib`, `seaborn`, `pytest`, `python-dotenv`

---

## 3. Data Pipeline & Server Execution

### Step 3: Run the Ingestion & ETL Pipeline
The master ETL pipeline initializes the database, ingests authentic cables, landing stations, IXPs, and facilities, generates spatial GeoJSON files, runs the data quality audit, and exports Power BI star-schema tables:
```bash
python scripts/run_etl.py
```
*Note: Due to local caching in `data/raw/`, subsequent runs are instantaneous.*

### Step 4: Launch the NetAtlas Intelligence Server
```bash
python scripts/run_server.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 4. Running the Automated Test Suite

Execute the 27 comprehensive automated tests covering unit logic, spatial geometry, NetworkX topology, REST API contracts, data integrity, and security headers:
```bash
python -m pytest -v tests/
```

---

## 5. Regenerating Power BI Datasets

To refresh the Star-Schema CSV and Parquet files in `data/reporting/`:
```bash
python scripts/export_powerbi_data.py
```

