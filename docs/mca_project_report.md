# NETATLAS: Global Internet Infrastructure Intelligence & Geospatial Analytics Platform
## University MCA Mini Project Report — Data Visualization Lab

**Candidate Degree:** Master of Computer Applications (MCA)  
**Course:** Data Visualization Laboratory & Advanced Software Engineering  
**Project Title:** NETATLAS — Global Internet Infrastructure Intelligence Platform  
**System Architecture:** Python 3.14 / Flask / GeoPandas / NetworkX / Leaflet / Power BI  
**Evaluation Standard:** Production Geospatial Analytics & Data Visualization Project  

---

### Abstract

Modern global society relies on an intricate, capital-intensive matrix of physical and logical communication infrastructure. Over 98% of international internet traffic traverses submarine fiber-optic cables resting on ocean seabeds, terminating at coastal landing stations, routing through carrier-neutral colocation facilities, and interconnecting via Internet Exchange Points (IXPs). Despite this critical importance, existing visualizations frequently rely on simplified schematic diagrams, synthetic datasets, or proprietary paywalled portals.

This project delivers **NETATLAS**, an open, independently engineered geospatial intelligence and network analytics platform built entirely on authentic, verifiable public infrastructure records. NetAtlas ingests, validates, and visualizes 713 verified submarine cable route geometries (MultiLineStrings), 1,928 coastal landing points, 1,337 Internet Exchange Points, and 3,000 colocation facilities sourced from TeleGeography, PeeringDB, and the World Bank. The platform integrates a reproducible Python ETL pipeline, an EPSG:4326 spatial engine, a NetworkX bipartite graph topology engine, a responsive cartographic web GIS, and a 6-page Microsoft Power BI Star-Schema reporting architecture. NetAtlas strictly enforces authentic data integrity, rejecting synthetic data fabrication, while providing comprehensive data quality audits.

---

### 1. Introduction & Problem Statement

#### 1.1 Background
The global internet is often conceptualized as an ethereal "cloud"; in physical reality, it is a concrete, highly vulnerable terrestrial and maritime infrastructure. Long-distance intercontinental data packets traverse subsea glass strands thinner than human hair, landing at specialized beach manholes, and converging into high-density colocation facilities where Autonomous Systems (ASNs) exchange traffic over shared switching fabrics (IXPs).

#### 1.2 Problem Statement
Existing academic and public visualization tools exhibit critical shortcomings:
1. **Geometric Inaccuracy:** Many tools connect landing points with straight chords or bezier curves, misrepresenting actual subsea bathymetric routes.
2. **Data Fabrication:** Demonstrations often utilize synthetic or randomized network topologies rather than authentic BGP peering records.
3. **Siloed Domains:** Submarine cable routes, IXPs, and colocation facilities are rarely synthesized into a single relational analytical model.
4. **Lack of Transparency:** Many platforms obscure data provenance, licensing constraints, and missing-attribute rates.

#### 1.3 Project Objectives
- Construct an end-to-end reproducible Python data ingestion pipeline with rate-limiting, exponential backoff, and local caching.
- Enforce strict WGS84 coordinate boundary checks and topological geometry sanitization using GeoPandas and Shapely.
- Model the global peering ecosystem as a bipartite NetworkX graph, calculating degree distributions and giant component metrics.
- Deliver an original, professional GIS web interface avoiding generic SaaS templates.
- Engineer a star-schema dimensional model and DAX library for Microsoft Power BI.

---

### 2. Technology Stack & Architecture

| Tier | Technologies | Strategic Rationale |
| :--- | :--- | :--- |
| **Backend & Analytics** | Python 3.14, Pandas, NumPy, GeoPandas, Shapely, NetworkX, SQLAlchemy, Pydantic | High-performance spatial vector math, graph analysis, and clean ORM modeling. |
| **Data Storage** | SQLite 3, Apache Parquet, GeoJSON, CSV | Multi-tier storage: OLTP querying (SQLite), analytical column storage (Parquet), GIS streaming (GeoJSON), and BI ingestion (CSV). |
| **REST API** | Flask 3.1, Flask-CORS | Lightweight, secure RESTful microservice with security headers and blueprint routing. |
| **Frontend GIS** | HTML5, CSS3, JavaScript (ES6+), Leaflet 1.9, Leaflet MarkerCluster, Plotly.js | Client-side vector rendering, responsive layout, cartographic styling, and zero external framework lock-in. |
| **Business Intelligence** | Microsoft Power BI Desktop, DAX | Dimensional star-schema reporting, interactive slicing, and executive dashboards. |
| **Testing & QA** | Pytest, flake8 | Automated unit, integration, spatial, data quality, and security testing. |

---

### 3. Data Ingestion & Preprocessing Pipeline

#### 3.1 Provenance and Acquisition
1. **TeleGeography Submarine Cable Data (CC BY-SA 4.0):** Ingested MultiLineString routes representing active and planned fiber lines, landing point coordinates, RFS commissioning dates, and owners.
2. **PeeringDB (CC BY-SA 4.0):** Ingested 1,337 IXPs, 3,000 interconnection facilities, 2,500 network operators, and 4,172 network-to-IX presence edges.
3. **World Bank Open Data (CC BY 4.0):** Integrated national digital adoption indicators.
4. **OpenStreetMap (ODbL 1.0):** Country boundaries and ISO 3166-1 reconciliation.

#### 3.2 Preprocessing & Data Sanitization
- **Coordinate Boundary Checks:** Enforced $-180^\circ \le \lambda \le 180^\circ$ and $-90^\circ \le \phi \le 90^\circ$.
- **Null Island Elimination:** Pruned geocoding artifacts defaulting to $(0.0, 0.0)$.
- **MultiLineString Topological Unification:** Merged segmented routes crossing the antimeridian into unified entities.
- **Completeness Reporting:** Automated calculation of null percentages for every column.

---

### 4. Network Graph Analytics (NetworkX)

The peering ecosystem is modeled as an undirected bipartite graph $G = (V_{net} \cup V_{ix}, E)$:
- **Nodes ($|V| = 1,596$):** 1,316 Network Operators (ASNs) and 280 active IXP hubs.
- **Edges ($|E| = 3,806$):** Observed presences on shared switching fabrics.
- **Giant Connected Component (GCC):** 1,548 nodes ($96.99\%$ of the network), verifying that global peering forms a unified, resilient scale-free mesh.
- **Degree Distribution:** Follows a heavy-tailed power-law distribution. A small elite of Tier-1 transit providers (Hurricane Electric, Cloudflare, Microsoft) maintain presence across 75–105 exchanges, while the median network peers at 2 exchanges.

---

### 5. Microsoft Power BI Reporting Model

The analytical model implements a Kimball Star-Schema:
- **Dimensions:** `DimCountry`, `DimRegion`, `DimDate`, `DimInfrastructureType`, `DimDataSource`.
- **Fact Tables:** `FactCable`, `FactLandingStation`, `FactIXP`, `FactFacility`, `FactNetworkRelationship`.
- **DAX Library:** 25 structured measures computing entity totals, length aggregations, IPv6 adoption rates, and route server peer ratios.

---

### 6. Verification & Quality Assurance

NetAtlas includes a comprehensive 27-test automated Pytest suite:
- **Unit Tests:** Geometry repair, Haversine distance, bounding box queries, coordinate cleaners.
- **Integration Tests:** REST API status codes, pagination, GeoJSON streaming, 404 handlers.
- **Data Quality Tests:** Table record counts, coordinate bound compliance, CSV export verification.
- **Security Tests:** Injection payload defense, Content-Security-Policy headers, X-Content-Type-Options: nosniff.

**Test Execution Result:** 27 passed in 2.06 seconds (100% pass rate).

---

### 7. Conclusion & Future Scope

NetAtlas successfully demonstrates an end-to-end, research-grade infrastructure intelligence platform. By bridging physical subsea geography with logical BGP peering graphs, the platform delivers actionable insights into planetary digital connectivity.

#### Future Enhancements
- Integration of real-time BGP routing tables from RIPE RIS and RouteViews.
- Bathymetric depth profile rendering along subsea cable paths.
- Automated terrestrial fiber route mapping along rail and pipeline rights-of-way.

