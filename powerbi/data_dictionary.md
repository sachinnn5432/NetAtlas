# NetAtlas Data Dictionary

## Dimension Tables

### 1. `DimCountry`
- **File:** `data/reporting/DimCountry.csv` / `data/processed/DimCountry.parquet`
- **Grain:** One record per sovereign economy / country.

| Column | Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `CountryKey` | String (PK) | No | ISO 3166-1 alpha-2 standard country code | `"US"` |
| `ISO2` | String | No | ISO 3166-1 alpha-2 code | `"US"` |
| `ISO3` | String | No | ISO 3166-1 alpha-3 code | `"USA"` |
| `CountryName` | String | No | Standard English country name | `"United States"` |
| `Region` | String | No | UN macro-continental region | `"North America"` |
| `Subregion` | String | Yes | UN geographic subregion | `"Northern America"` |
| `CentroidLatitude` | Float | Yes | Geographic centroid latitude (WGS84) | `37.0902` |
| `CentroidLongitude`| Float | Yes | Geographic centroid longitude (WGS84) | `-95.7129` |

---

### 2. `DimRegion`
- **File:** `data/reporting/DimRegion.csv`
- **Grain:** One record per continental macro-region and subregion.

| Column | Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `RegionKey` | Integer (PK) | No | Synthetic surrogate key | `1` |
| `Region` | String | No | UN macro-continental region | `"Europe"` |
| `Subregion` | String | Yes | Geographic subregion | `"Western Europe"` |

---

### 3. `DimDate`
- **File:** `data/reporting/DimDate.csv`
- **Grain:** One record per calendar year (1980–2035).

| Column | Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `DateKey` | Integer (PK) | No | Four-digit calendar year | `2024` |
| `Year` | Integer | No | Year integer | `2024` |
| `Decade` | Integer | No | Starting year of decade | `2020` |
| `Era` | String | No | Classification era (`Historical`, `Modern`, `Projected`) | `"Modern"` |

---

### 4. `DimInfrastructureType`
- **File:** `data/reporting/DimInfrastructureType.csv`
- **Grain:** One record per infrastructure category.

| Column | Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `TypeKey` | Integer (PK) | No | Type identifier | `1` |
| `TypeName` | String | No | Entity category name | `"Submarine Cable"` |
| `PhysicalDomain` | String | No | Environment domain | `"Maritime/Subsea"` |
| `Layer` | String | No | OSI / Interconnection layer | `"L1 Physical"` |

---

### 5. `DimDataSource`
- **File:** `data/reporting/DimDataSource.csv`
- **Grain:** One record per registered open dataset.

| Column | Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `SourceKey` | String (PK) | No | Source identifier | `"telegeography_cables"` |
| `SourceName` | String | No | Official source title | `"TeleGeography Submarine Cable Geometries"` |
| `SourceURL` | String | No | Origin URL | `"https://www.submarinecablemap.com"` |
| `License` | String | No | Legal license terms | `"CC BY-SA 4.0"` |
| `GeographicCoverage` | String | No | Spatial coverage description | `"Global oceans and coastal corridors"` |
| `TemporalCoverage` | String | No | Historical/operational scope | `"1989 - 2028"` |

---

## Fact Tables

### 6. `FactCable`
- **File:** `data/reporting/FactCable.csv` / `data/processed/FactCable.parquet`
- **Grain:** One record per authentic submarine cable route system.

| Column | Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `CableID` | String (PK) | No | Cable slug identifier | `"2africa"` |
| `CableName` | String | No | Official cable system name | `"2Africa"` |
| `RFS_Year` | Integer (FK) | Yes | Ready-for-service commissioning year | `2024` |
| `LengthKM` | Float | Yes | Official length in kilometers | `45000.0` |
| `IsPlanned` | Integer | No | Binary flag: 0=Operational, 1=Planned | `0` |
| `LandingPointsCount` | Integer | No | Total connected landing points | `46` |
| `Owners` | String | Yes | Operating consortium / owners | `"Meta, China Mobile, Vodafone, Orange..."` |
| `Suppliers` | String | Yes | Cable manufacturing / laying suppliers | `"SubCom, ASN"` |
| `SourceKey` | String (FK) | No | Provenance foreign key | `"telegeography_cables"` |
| `TypeKey` | Integer (FK) | No | Infrastructure type key | `1` |

---

### 7. `FactLandingStation`
- **File:** `data/reporting/FactLandingStation.csv` / `data/processed/FactLandingStation.parquet`
- **Grain:** One record per verified coastal submarine cable landing point.

| Column | Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `StationID` | String (PK) | No | Landing station unique slug | `"mumbai-india"` |
| `StationName` | String | No | Station name / city | `"Mumbai, India"` |
| `CountryKey` | String (FK) | No | ISO2 country code | `"IN"` |
| `CountryName` | String | No | Country name | `"India"` |
| `Latitude` | Float | No | WGS84 Latitude coordinate | `18.9220` |
| `Longitude` | Float | No | WGS84 Longitude coordinate | `72.8346` |
| `IsTBD` | Integer | No | Binary flag: 0=Confirmed, 1=To Be Determined | `0` |
| `CableCount` | Integer | No | Count of terminating cables | `5` |
| `SourceKey` | String (FK) | No | Provenance key | `"telegeography_landing_stations"` |
| `TypeKey` | Integer (FK) | No | Infrastructure type key | `2` |

---

### 8. `FactIXP`
- **File:** `data/reporting/FactIXP.csv` / `data/processed/FactIXP.parquet`
- **Grain:** One record per authentic Internet Exchange Point.

| Column | Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `IXPID` | Integer (PK)| No | PeeringDB IX ID | `31` |
| `IXPName` | String | No | Exchange name | `"DE-CIX Frankfurt"` |
| `City` | String | Yes | Municipal location | `"Frankfurt"` |
| `CountryKey` | String (FK) | No | ISO2 country code | `"DE"` |
| `RegionContinent`| String | Yes | Continental grouping | `"Europe"` |
| `Media` | String | Yes | Switching fabric technology | `"Ethernet"` |
| `ConnectedNetworksCount` | Integer | No | Participant network ASNs | `237` |
| `FacilityAssociationsCount` | Integer | No | Associated data center sites | `35` |
| `SupportsIPv6`| Integer | No | IPv6 unicast support flag | `1` |
| `SupportsMulticast` | Integer | No | Multicast peering flag | `0` |
| `SourceKey` | String (FK) | No | Provenance key | `"peeringdb_ix"` |
| `TypeKey` | Integer (FK) | No | Infrastructure type key | `3` |

---

### 9. `FactFacility`
- **File:** `data/reporting/FactFacility.csv` / `data/processed/FactFacility.parquet`
- **Grain:** One record per verified interconnection & colocation facility.

| Column | Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `FacilityID` | Integer (PK)| No | PeeringDB Facility ID | `1` |
| `FacilityName`| String | No | Facility name | `"Equinix DC1-DC15 - Ashburn"` |
| `City` | String | Yes | Municipal location | `"Ashburn"` |
| `CountryKey` | String (FK) | No | ISO2 country code | `"US"` |
| `RegionContinent` | String | Yes | Continental region | `"North America"` |
| `Latitude` | Float | Yes | WGS84 Latitude coordinate | `39.016363` |
| `Longitude` | Float | Yes | WGS84 Longitude coordinate | `-77.459023` |
| `ConnectedNetworksCount`| Integer | No | Colocated network ASNs | `480` |
| `IXPCount` | Integer | No | Intersecting exchange points | `4` |
| `SourceKey` | String (FK) | No | Provenance key | `"peeringdb_fac"` |
| `TypeKey` | Integer (FK) | No | Infrastructure type key | `4` |

---

### 10. `FactNetworkRelationship`
- **File:** `data/reporting/FactNetworkRelationship.csv` / `data/processed/FactNetworkRelationship.parquet`
- **Grain:** One record per network presence on an IXP switching fabric (`netixlan`).

| Column | Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `RelationshipID` | Integer (PK)| No | PeeringDB netixlan ID | `1145` |
| `NetworkID` | Integer | No | Network ID | `286` |
| `IXPID` | Integer (FK)| No | Exchange point ID | `31` |
| `ASN` | Integer | No | Autonomous System Number | `3856` |
| `SpeedMbps` | Integer | No | Port speed in Mbps | `10000` |
| `IsRouteServerPeer` | Integer | No | Route server peering flag | `1` |
| `Operational` | Integer | No | Operational status flag | `1` |
| `SourceKey` | String (FK) | No | Provenance key | `"peeringdb_netixlan"` |

