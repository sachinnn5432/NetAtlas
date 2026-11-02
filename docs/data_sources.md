# NetAtlas Data Sources Specification & Provenance

NetAtlas utilizes strictly authentic, publicly verifiable, and properly licensed datasets. Synthetic, fabricated, or simulated infrastructure locations are explicitly prohibited.

---

## 1. Primary Ingested Datasets

### A. PeeringDB Public Database
- **Provider:** PeeringDB Inc.
- **Authority URL:** `https://www.peeringdb.com/apidocs/`
- **License:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
- **Ingested Endpoints:**
  - `/api/ix`: Internet Exchange Points (name, country, city, protocols, network count).
  - `/api/fac`: Colocation facilities (operator name, coordinates, address, network count).
  - `/api/net`: Autonomous Systems / Network operators (name, ASN, info type).
  - `/api/netixlan`: Network-to-IX interconnection edges (speed, operational status, route server participation).
- **Known Limitations:** PeeringDB is an operator-maintained registry. While comprehensive for commercial peering in North America, Europe, and Asia, it reflects voluntary participation rather than mandatory regulatory reporting. Membership represents presence on a shared exchange fabric, not point-to-point private peering.

### B. TeleGeography Submarine Cable Map Data
- **Provider:** TeleGeography (PriMetrica, Inc.)
- **Authority URL:** `https://www.submarinecablemap.com/`
- **License:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
- **Ingested Endpoints:**
  - `cable-geo.json`: 713 unique cable systems represented as MultiLineString route geometries.
  - `landing-point-geo.json`: 1,928 verified coastal cable landing points.
  - `cable/{id}.json`: System metadata including Ready-For-Service (RFS) commissioning year, total length in kilometers, operating consortium, and suppliers.
- **Known Limitations:** Subsea cable routes represent stylized cartographic paths based on public landing stations and bathymetric waypoints. The exact tactical seabed coordinates are classified for national security and maritime safety reasons.

### C. World Bank Digital Development Indicators
- **Provider:** The World Bank Group
- **Authority URL:** `https://datacatalog.worldbank.org/`
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Indicators:**
  - `IT.NET.USER.ZS`: Individuals using the Internet (% of population).
  - `IT.NET.SECR.P6`: Secure Internet servers (per 1 million people).
- **Known Limitations:** National reporting intervals lag by 12–24 months depending on national statistical agencies.

### D. OpenStreetMap & Natural Earth Reference Data
- **Provider:** OpenStreetMap Contributors / Natural Earth
- **Authority URL:** `https://www.openstreetmap.org/`
- **License:** Open Database License (ODbL) 1.0
- **Purpose:** Sovereign country name mapping, ISO 3166-1 alpha-2 / alpha-3 reconciliation, UN regional classifications, and geographic centroid fallbacks.

---

## 2. Ingestion & Provenance Audit Table

| Source ID | Ingestion Method | Refresh Cadence | Raw Storage | Output Model |
| :--- | :--- | :--- | :--- | :--- |
| `peeringdb_ix` | REST API (Paginated) | Daily / On-Demand | `data/raw/peeringdb_ix.json` | `IXPModel`, `FactIXP` |
| `peeringdb_fac` | REST API (Paginated) | Daily / On-Demand | `data/raw/peeringdb_fac.json` | `FacilityModel`, `FactFacility` |
| `peeringdb_net` | REST API (Paginated) | Daily / On-Demand | `data/raw/peeringdb_net.json` | `NetworkModel` |
| `peeringdb_netixlan` | REST API (Paginated) | Daily / On-Demand | `data/raw/peeringdb_netixlan.json` | `NetworkIXRelationshipModel` |
| `telegeography_cables`| GeoJSON Stream | Weekly / On-Demand | `data/raw/cable_geo.json` | `CableModel`, `FactCable` |
| `telegeography_landings`| GeoJSON Stream | Weekly / On-Demand | `data/raw/landing_point_geo.json`| `LandingStationModel`, `FactLandingStation` |

