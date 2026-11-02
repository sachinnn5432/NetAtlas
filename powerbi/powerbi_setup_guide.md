# NetAtlas Microsoft Power BI Configuration & Dashboard Setup Guide

This guide details the step-by-step procedure for importing NetAtlas reporting tables into Microsoft Power BI Desktop, establishing star-schema relationships, applying the DAX measures library, and configuring the six required analytical dashboard pages.

---

## 1. Data Ingestion into Power BI Desktop

1. Launch **Microsoft Power BI Desktop**.
2. Select **Get Data** -> **Text/CSV** (or **Folder** to import the entire directory).
3. Navigate to `data/reporting/` and import the following 10 CSV tables:
   - `DimCountry.csv`
   - `DimRegion.csv`
   - `DimDate.csv`
   - `DimInfrastructureType.csv`
   - `DimDataSource.csv`
   - `FactCable.csv`
   - `FactLandingStation.csv`
   - `FactIXP.csv`
   - `FactFacility.csv`
   - `FactNetworkRelationship.csv`
4. In the Power Query Editor, verify data types:
   - `DimCountry[CountryKey]` -> Text
   - `FactLandingStation[Latitude]`, `FactLandingStation[Longitude]` -> Decimal Number
   - `FactFacility[Latitude]`, `FactFacility[Longitude]` -> Decimal Number
   - `FactCable[LengthKM]` -> Decimal Number
   - `FactCable[RFS_Year]` -> Whole Number
5. Click **Close & Apply**.

---

## 2. Star Schema Relationship Configuration

In Power BI **Model View**, establish the following 1-to-Many (`1:*`), Single Cross-Filter relationships:

1. **`DimCountry[CountryKey]`** (1) -> **`FactLandingStation[CountryKey]`** (*)
2. **`DimCountry[CountryKey]`** (1) -> **`FactIXP[CountryKey]`** (*)
3. **`DimCountry[CountryKey]`** (1) -> **`FactFacility[CountryKey]`** (*)
4. **`DimDate[Year]`** (1) -> **`FactCable[RFS_Year]`** (*)
5. **`DimInfrastructureType[TypeKey]`** (1) -> **`FactCable[TypeKey]`** (*)
6. **`DimInfrastructureType[TypeKey]`** (1) -> **`FactLandingStation[TypeKey]`** (*)
7. **`DimInfrastructureType[TypeKey]`** (1) -> **`FactIXP[TypeKey]`** (*)
8. **`DimInfrastructureType[TypeKey]`** (1) -> **`FactFacility[TypeKey]`** (*)
9. **`DimDataSource[SourceKey]`** (1) -> **`FactCable[SourceKey]`** (*)
10. **`DimDataSource[SourceKey]`** (1) -> **`FactLandingStation[SourceKey]`** (*)
11. **`DimDataSource[SourceKey]`** (1) -> **`FactIXP[SourceKey]`** (*)
12. **`DimDataSource[SourceKey]`** (1) -> **`FactFacility[SourceKey]`** (*)
13. **`FactIXP[IXPID]`** (1) -> **`FactNetworkRelationship[IXPID]`** (*)

---

## 3. Applying DAX Measures

1. Create a dedicated measure table: **Modeling** -> **New Table**:
   ```dax
   _Measures = ROW("Description", "NetAtlas Central Measures Container")
   ```
2. Open `powerbi/measures.dax`.
3. Copy and paste each measure into the new measure table.
4. Set formatting:
   - `[Total Submarine Cables]`, `[Total Cable Landing Stations]`, `[Total Internet Exchanges]`, `[Total Colocation Facilities]`: Whole Number with 1000 separator (`,`).
   - `[Total Subsea Fiber Length (KM)]`: Whole Number, comma formatted.
   - `[Average Port Speed (Gbps)]`: Decimal (2 decimal places).
   - Ratios (`[Planned Subsea Cable Ratio]`, `[IPv6 Enabled Exchange Ratio]`, `[Route Server Peer Adoption %]`): Percentage (`%`).

---

## 4. Building the 6 Analytical Pages

### PAGE 1: Global Infrastructure Overview
- **Visual 1 (Top Cards):** Multi-row card displaying `[Total Submarine Cables]`, `[Total Cable Landing Stations]`, `[Total Internet Exchanges]`, `[Total Colocation Facilities]`.
- **Visual 2 (Map):** Bubble Map visual with `FactLandingStation[Latitude]` and `FactLandingStation[Longitude]`. Size bubbles by `[Total Cable Landing Stations]`.
- **Visual 3 (Donut Chart):** Legend `DimInfrastructureType[TypeName]`, Values `[Total Assets]`.
- **Visual 4 (Table):** `DimCountry[CountryName]`, `[Total Internet Exchanges]`, `[Total Colocation Facilities]`, `[Total Cable Landing Stations]`.

### PAGE 2: Submarine Cable Intelligence
- **Visual 1 (Clustered Column Chart):** Axis `DimDate[Decade]`, Values `[Total Submarine Cables]`, Legend `FactCable[IsPlanned]`.
- **Visual 2 (Bar Chart):** Axis `FactCable[Owners]` (Top 10), Values `[Total Submarine Cables]`.
- **Visual 3 (Histogram/Bar):** Cable length distribution bins.
- **Visual 4 (Card/Gauge):** `[Total Subsea Fiber Length (KM)]` and `[Average Cable Length (KM)]`.

### PAGE 3: Internet Exchange Analytics
- **Visual 1 (Bar Chart):** Top 15 IXPs by `[Average Networks Per Exchange]`.
- **Visual 2 (Tree Map):** Category `DimCountry[Region]`, Sub-category `DimCountry[CountryName]`, Values `[Total Internet Exchanges]`.
- **Visual 3 (Gauges):** `[IPv6 Enabled Exchange Ratio]` and `[Multicast Enabled Exchange Ratio]`.

### PAGE 4: Data Centre and Facility Analytics
- **Visual 1 (Clustered Bar Chart):** Axis `DimCountry[Region]`, Values `[Total Colocation Facilities]`.
- **Visual 2 (Scatter Plot):** X-Axis `[Average Networks Per Facility]`, Y-Axis `FactFacility[IXPCount]`.
- **Visual 3 (Matrix):** Rows `DimCountry[CountryName]`, Values `[Total Colocation Facilities]`, `[Facilities With IXP Presence]`.

### PAGE 5: Global Network Connectivity
- **Visual 1 (Card):** `[Total Network Operators]`, `[Total Peering Interconnections]`.
- **Visual 2 (Donut Chart):** Legend `FactNetworkRelationship[IsRouteServerPeer]`, Values `[Total Peering Interconnections]`.
- **Visual 3 (Bar Chart):** Distribution of port speeds (`FactNetworkRelationship[SpeedMbps]`).

### PAGE 6: Data Quality and Methodology
- **Visual 1 (Cards/Gauges):** `[Landing Station Geocode Completeness %]`, `[Facility Geocode Completeness %]`, `[Cable Length Completeness %]`.
- **Visual 2 (Table):** `DimDataSource[SourceName]`, `DimDataSource[License]`, `DimDataSource[GeographicCoverage]`.
- **Visual 3 (Text Box):** Methodological caveats regarding voluntary participation in community registries.

