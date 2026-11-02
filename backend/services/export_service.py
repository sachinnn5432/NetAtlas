"""Power BI Star Schema Export Service for NetAtlas.

Extracts normalized facts and dimensions into high-performance Parquet and CSV files
ready for direct ingestion into Microsoft Power BI reporting models.
"""

from typing import Dict, Any, List
import json
from pathlib import Path
import pandas as pd
from backend.models.database import SessionLocal
from backend.models.db_models import (
    CableModel, LandingStationModel, IXPModel, FacilityModel,
    NetworkModel, NetworkIXRelationshipModel, DataSourceProvenanceModel, CountryReferenceModel
)
from backend.config.settings import REPORTING_DATA_DIR, PROCESSED_DATA_DIR
from backend.config.logging_config import logger

class ExportService:
    """Exports star-schema dimensions and facts for Microsoft Power BI and external BI tools."""

    @classmethod
    def export_powerbi_star_schema(cls) -> Dict[str, int]:
        """Generates all dimension and fact tables as CSV and Parquet files."""
        session = SessionLocal()
        counts = {}
        try:
            logger.info("Extracting DimCountry & DimRegion...")
            # 1. DimCountry & DimRegion
            countries = session.query(CountryReferenceModel).all()
            dim_country = pd.DataFrame([{
                "CountryKey": c.iso2,
                "ISO2": c.iso2,
                "ISO3": c.iso3,
                "CountryName": c.country_name,
                "Region": c.region,
                "Subregion": c.subregion,
                "CentroidLatitude": c.latitude,
                "CentroidLongitude": c.longitude
            } for c in countries])

            dim_region = dim_country[["Region", "Subregion"]].drop_duplicates().reset_index(drop=True)
            dim_region["RegionKey"] = range(1, len(dim_region) + 1)

            # 2. DimDate (Calendar dimension covering commissioning years 1980 - 2035)
            years = list(range(1980, 2036))
            dim_date = pd.DataFrame({
                "DateKey": years,
                "Year": years,
                "Decade": [(y // 10) * 10 for y in years],
                "Era": ["Historical" if y < 2000 else ("Modern" if y <= 2024 else "Projected/Future") for y in years]
            })

            # 3. DimInfrastructureType
            dim_infra_type = pd.DataFrame([
                {"TypeKey": 1, "TypeName": "Submarine Cable", "PhysicalDomain": "Maritime/Subsea", "Layer": "L1 Physical"},
                {"TypeKey": 2, "TypeName": "Cable Landing Station", "PhysicalDomain": "Terrestrial Coastal", "Layer": "L1/L2 Termination"},
                {"TypeKey": 3, "TypeName": "Internet Exchange Point", "PhysicalDomain": "Terrestrial Facility", "Layer": "L2 Peering Fabric"},
                {"TypeKey": 4, "TypeName": "Colocation Facility", "PhysicalDomain": "Terrestrial Data Centre", "Layer": "L1/L2 Interconnection"}
            ])

            # 4. DimDataSource
            provs = session.query(DataSourceProvenanceModel).all()
            dim_source = pd.DataFrame([{
                "SourceKey": p.id,
                "SourceName": p.name,
                "SourceURL": p.url,
                "License": p.license,
                "GeographicCoverage": p.geographic_coverage,
                "TemporalCoverage": p.temporal_coverage
            } for p in provs])

            # 5. FactCable
            cables = session.query(CableModel).all()
            fact_cable = pd.DataFrame([{
                "CableID": c.id,
                "CableName": c.name,
                "RFS_Year": c.rfs_year,
                "LengthKM": c.length_km,
                "IsPlanned": 1 if c.is_planned else 0,
                "LandingPointsCount": c.landing_points_count,
                "Owners": c.owners or "Unavailable",
                "Suppliers": c.suppliers or "Unavailable",
                "SourceKey": "telegeography_cables",
                "TypeKey": 1
            } for c in cables])

            # 6. FactLandingStation
            lps = session.query(LandingStationModel).all()
            fact_landing = pd.DataFrame([{
                "StationID": lp.id,
                "StationName": lp.name,
                "CountryKey": lp.country_code or "XX",
                "CountryName": lp.country,
                "Latitude": lp.latitude,
                "Longitude": lp.longitude,
                "IsTBD": 1 if lp.is_tbd else 0,
                "CableCount": lp.cable_count,
                "SourceKey": "telegeography_landing_stations",
                "TypeKey": 2
            } for lp in lps])

            # 7. FactIXP
            ixps = session.query(IXPModel).all()
            fact_ixp = pd.DataFrame([{
                "IXPID": ix.id,
                "IXPName": ix.name,
                "City": ix.city or "Unknown",
                "CountryKey": ix.country,
                "RegionContinent": ix.region_continent or "Unknown",
                "Media": ix.media or "Unknown",
                "ConnectedNetworksCount": ix.net_count,
                "FacilityAssociationsCount": ix.fac_count,
                "SupportsIPv6": 1 if ix.proto_ipv6 else 0,
                "SupportsMulticast": 1 if ix.proto_multicast else 0,
                "SourceKey": "peeringdb_ix",
                "TypeKey": 3
            } for ix in ixps])

            # 8. FactFacility
            facs = session.query(FacilityModel).all()
            fact_fac = pd.DataFrame([{
                "FacilityID": f.id,
                "FacilityName": f.name,
                "City": f.city or "Unknown",
                "CountryKey": f.country,
                "RegionContinent": f.region_continent or "Unknown",
                "Latitude": f.latitude,
                "Longitude": f.longitude,
                "ConnectedNetworksCount": f.net_count,
                "IXPCount": f.ix_count,
                "SourceKey": "peeringdb_fac",
                "TypeKey": 4
            } for f in facs])

            # 9. FactNetworkRelationship
            rels = session.query(NetworkIXRelationshipModel).all()
            fact_rel = pd.DataFrame([{
                "RelationshipID": r.id,
                "NetworkID": r.net_id,
                "IXPID": r.ix_id,
                "ASN": r.asn,
                "SpeedMbps": r.speed,
                "IsRouteServerPeer": 1 if r.is_rs_peer else 0,
                "Operational": 1 if r.operational else 0,
                "SourceKey": "peeringdb_netixlan"
            } for r in rels])

            # Save tables to data/reporting/*.csv and data/processed/*.parquet
            tables = {
                "DimCountry": dim_country,
                "DimRegion": dim_region,
                "DimDate": dim_date,
                "DimInfrastructureType": dim_infra_type,
                "DimDataSource": dim_source,
                "FactCable": fact_cable,
                "FactLandingStation": fact_landing,
                "FactIXP": fact_ixp,
                "FactFacility": fact_fac,
                "FactNetworkRelationship": fact_rel
            }

            for name, df in tables.items():
                csv_path = REPORTING_DATA_DIR / f"{name}.csv"
                parquet_path = PROCESSED_DATA_DIR / f"{name}.parquet"
                df.to_csv(csv_path, index=False, encoding="utf-8")
                try:
                    df.to_parquet(parquet_path, index=False)
                except Exception as e:
                    logger.warning("Could not export %s to parquet: %s", name, e)
                counts[name] = len(df)
                logger.info("Exported %s with %d rows to CSV & Parquet.", name, len(df))

            return counts
        finally:
            session.close()

