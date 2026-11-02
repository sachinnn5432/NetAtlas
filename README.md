# NETATLAS — Global Internet Infrastructure Intelligence Platform
### Geospatial Analytics, Interconnection Topologies & Business Intelligence

![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)
![Tests](https://img.shields.io/badge/Pytest-27%2F27%20Passing-brightgreen.svg)
![Data Integrity](https://img.shields.io/badge/Data%20Integrity-100%25%20Verified%20Public%20Sources-success.svg)
![Architecture](https://img.shields.io/badge/Architecture-Flask%20%7C%20GeoPandas%20%7C%20NetworkX%20%7C%20Power%20BI-orange.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

---

## 1. Project Overview

**NETATLAS** is an independently engineered global internet infrastructure intelligence and geospatial analytics platform. Built to production standards for university MCA Data Visualization evaluation and professional portfolio presentation, NetAtlas visualizes the physical and logical fabric supporting global internet connectivity.

Unlike generic dashboards or schematic prototypes that rely on synthetic points or straight lines, NetAtlas renders **100% authentic, verifiable infrastructure records**:
- **713 Submarine Fiber-Optic Cables:** Complete MultiLineString seabed route geometries from TeleGeography.
- **1,928 Coastal Landing Stations:** Verified geographic coordinates across global maritime corridors.
- **1,337 Internet Exchange Points (IXPs):** Active Layer-2 exchange fabrics cataloged by PeeringDB.
- **3,000 Colocation & Interconnection Facilities:** Carrier-neutral data centers with verified operator attribution.
- **2,500 Network Operators (ASNs) & 4,172 Peering Edges:** NetworkX-powered bipartite graph topology modeling.

---

## 2. Key Product Features

1. **Global GIS Map Experience:** Full-screen responsive Leaflet canvas with clean OpenStreetMap cartography, vector cable rendering, marker clustering, and interactive hover inspection.
2. **Submarine Cable Explorer:** Interactive route inspector displaying ready-for-service (RFS) dates, cable lengths in km, operational status, and consortium owners.
3. **Internet Exchange (IXP) Explorer:** Sovereign and regional peering analysis with connected network counts, switching fabrics, and IPv6 dual-stack adoption.
4. **Data Centre & Facility Explorer:** Carrier hotel and interconnection campus mapping with operator tracking.
5. **NetworkX Interconnection Graph Analysis:** Bipartite graph modeling ($|V|=1,596, |E|=3,806$) demonstrating a 97% giant connected component and scale-free power-law degree distributions.
6. **Macro-Regional Density Scoring:** Composite Infrastructure Density Index ($IDI$) ranking sovereign economies.
7. **Automated Data Quality & Provenance Audit:** Live metrics validating coordinate bounds (EPSG:4326), Null Island filtering, and legal dataset licensing.
8. **Microsoft Power BI Reporting Layer:** Exported Star-Schema dimensional model (`data/reporting/*.csv`) with a 25-measure DAX library.

---

## 3. Technology Stack

- **Backend & Geospatial:** Python 3.11+, Pandas, NumPy, GeoPandas, Shapely, NetworkX, Requests, SQLAlchemy, Pydantic.
- **Storage:** SQLite 3 (`data/netatlas.db`), Apache Parquet (`data/processed/*.parquet`), GeoJSON (`data/geojson/`), CSV (`data/reporting/`).
- **REST API:** Flask 3.1 with Blueprint routing, CORS, and strict security headers (`X-Content-Type-Options`, `X-Frame-Options`, `CSP`).
- **Frontend UI:** HTML5, CSS3, JavaScript (ES6+), Leaflet 1.9, Leaflet MarkerCluster, Plotly.js, Inter & IBM Plex Mono typography.
- **Reporting:** Microsoft Power BI Star-Schema Dimensional Model & DAX measures.
- **Testing:** Pytest (27 automated unit, integration, data quality, and security tests).

---

## 4. System Architecture

```
NetAtlas/
├── backend/
│   ├── api/                  # Flask REST API endpoints and app factory
│   ├── ingestion/            # PeeringDB, Submarine Cable, OSM, GeoJSON loaders
│   ├── preprocessing/        # Cleaners, anomaly validators, quality reporter
│   ├── geospatial/           # Spatial indexing, BBox, GeoPandas converters
│   ├── analytics/            # Country rankings, regional density, data stories
│   ├── network_analysis/     # NetworkX bipartite graph & degree distributions
│   ├── services/             # Catalog query, search, and Power BI export services
│   ├── models/               # SQLAlchemy ORM database models
│   ├── schemas/              # Pydantic data validation schemas
│   └── config/               # Settings, directory paths, and logging
├── frontend/
│   └── public/               # Cartographic UI (HTML5, CSS3, JavaScript)
├── data/
│   ├── raw/                  # Cached raw API responses for offline resilience
│   ├── processed/            # High-performance Parquet datasets
│   ├── reporting/            # Star-Schema CSVs for Microsoft Power BI
│   └── geojson/              # Validated WGS84 GeoJSON spatial layers
├── powerbi/
│   ├── measures.dax          # 25 production DAX measures
│   ├── reporting_model.md    # Star-Schema architecture & 6-page dashboard guide
│   ├── data_dictionary.md    # Full table and column schema dictionary
│   └── powerbi_setup_guide.md# Step-by-step Power BI Desktop setup instructions
├── notebooks/                # 4 Exploratory Jupyter notebooks
├── tests/                    # 27 automated unit, integration, and security tests
├── docs/                     # Architecture, methodology, licensing, user guide
├── scripts/                  # Master ETL pipeline, server runner, export utilities
├── requirements.txt
└── README.md
```

---

## 5. Quickstart & Installation

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Execute Master ETL Pipeline
```bash
python scripts/run_etl.py
```
*Initializes database schema, ingests public datasets, validates coordinates, generates GeoJSON, and exports Power BI star-schema tables in ~35 seconds.*

### Step 3: Launch the NetAtlas Intelligence Server
```bash
python scripts/run_server.py
```
Open **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)** in your browser.

### Step 4: Run the Automated Test Suite
```bash
python -m pytest -v tests/
```
```
============================= 27 passed in 2.06s ==============================
```

---

## 6. Microsoft Power BI Reporting Model

NetAtlas provides complete analytical exports ready for direct import into Microsoft Power BI Desktop:
- **Dimensions:** `DimCountry`, `DimRegion`, `DimDate`, `DimInfrastructureType`, `DimDataSource`.
- **Fact Tables:** `FactCable`, `FactLandingStation`, `FactIXP`, `FactFacility`, `FactNetworkRelationship`.
- **DAX Library (`powerbi/measures.dax`):** Includes key business logic:
  - `[Total Submarine Cables]`, `[Total Cable Landing Stations]`, `[Total Internet Exchanges]`, `[Total Colocation Facilities]`
  - `[Average Networks Per Exchange]`, `[IPv6 Enabled Exchange Ratio]`, `[Route Server Peer Adoption %]`
  - `[Total Subsea Fiber Length (KM)]`, `[Cable Length Completeness %]`

---

## 7. Data Provenance & Legal Licensing

NetAtlas honors open data licensing standards:
- **PeeringDB:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).
- **TeleGeography Submarine Cable Map:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).
- **World Bank Open Data:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **OpenStreetMap:** Open Database License (ODbL) 1.0.

*Strict Policy: NetAtlas never invents infrastructure coordinates, fabricates cable geometries, or generates dummy data.*

---

## 8. Academic Project Evaluation

- **Candidate:** MCA Third Semester, Data Visualization Laboratory
- **Evaluation Criteria Met:** Complete software design, authentic public data ingestion, reproducible ETL pipeline, spatial vector processing, graph network topology, responsive UI/UX cartography, Power BI Star-Schema, 27/27 passing tests, and comprehensive documentation.

