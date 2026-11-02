"""Data Source Provenance and Transparency Registry for NetAtlas.

Records provenance, license terms, geographic and temporal coverage,
and explicit data limitations for every integrated public infrastructure dataset.
"""

from typing import Dict, Any, List
from datetime import datetime
from backend.models.database import SessionLocal
from backend.models.db_models import DataSourceProvenanceModel
from backend.config.logging_config import logger

PROVENANCE_METADATA: List[Dict[str, Any]] = [
    {
        "id": "peeringdb_ix",
        "name": "PeeringDB Internet Exchange Points",
        "url": "https://www.peeringdb.com/api/ix",
        "license": "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
        "geographic_coverage": "Global (200+ countries and territories)",
        "temporal_coverage": "2004 - Present (Continuously community updated)",
        "known_limitations": "PeeringDB is a community-driven database. Participation is voluntary; not all IXPs or networks globally are registered. Membership does not imply direct physical peering between all listed members."
    },
    {
        "id": "peeringdb_fac",
        "name": "PeeringDB Interconnection Facilities & Data Centres",
        "url": "https://www.peeringdb.com/api/fac",
        "license": "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
        "geographic_coverage": "Global",
        "temporal_coverage": "2004 - Present",
        "known_limitations": "Facilities represent colocation and interconnection sites. High facility density reflects commercial peering activity rather than confirmed hyperscale server counts. Coordinates are provided by operators."
    },
    {
        "id": "peeringdb_net",
        "name": "PeeringDB Networks and Autonomous Systems",
        "url": "https://www.peeringdb.com/api/net",
        "license": "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
        "geographic_coverage": "Global",
        "temporal_coverage": "2004 - Present",
        "known_limitations": "Covers autonomous systems that actively register peering policies. Does not capture internal or non-peering enterprise networks."
    },
    {
        "id": "peeringdb_netixlan",
        "name": "PeeringDB Network-to-IX Interconnections",
        "url": "https://www.peeringdb.com/api/netixlan",
        "license": "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
        "geographic_coverage": "Global",
        "temporal_coverage": "2004 - Present",
        "known_limitations": "Represents presence on an IXP shared switching fabric. Does not prove bilateral BGP peering or traffic exchange volume."
    },
    {
        "id": "telegeography_cables",
        "name": "TeleGeography Submarine Cable Geometries",
        "url": "https://www.submarinecablemap.com/api/v3/cable/cable-geo.json",
        "license": "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
        "geographic_coverage": "Global oceans and coastal corridors",
        "temporal_coverage": "1989 - 2028 (Operational and announced systems)",
        "known_limitations": "Cable routes are stylized depictions based on public landing points and bathymetric waypoints; exact maritime subsea paths are proprietary to cable operators and defense authorities."
    },
    {
        "id": "telegeography_landing_stations",
        "name": "TeleGeography Cable Landing Points",
        "url": "https://www.submarinecablemap.com/api/v3/landing-point/landing-point-geo.json",
        "license": "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
        "geographic_coverage": "Global coastal landing locations",
        "temporal_coverage": "Historical to current",
        "known_limitations": "Represents the municipality/landing area rather than the exact physical security perimeter of the landing shelter or beach manhole."
    },
    {
        "id": "world_bank_ict",
        "name": "World Bank Digital Development Infrastructure Indicators",
        "url": "https://datacatalog.worldbank.org/",
        "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "geographic_coverage": "Global sovereign nations (217 economies)",
        "temporal_coverage": "1990 - 2024",
        "known_limitations": "Country-level reported statistical indicators. Reporting lags vary by national statistical office."
    },
    {
        "id": "osm_reference",
        "name": "OpenStreetMap Geographic Reference & Boundaries",
        "url": "https://www.openstreetmap.org/",
        "license": "Open Database License (ODbL) 1.0",
        "geographic_coverage": "Global",
        "temporal_coverage": "Current",
        "known_limitations": "Used for boundary resolution, country names, and geographic context. Maritime borders may differ by geopolitical recognition."
    }
]

def register_provenance_records(record_counts: Dict[str, int] = None):
    """Inserts or updates data source provenance entries in the database."""
    session = SessionLocal()
    record_counts = record_counts or {}
    try:
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        for meta in PROVENANCE_METADATA:
            source_id = meta["id"]
            count = record_counts.get(source_id, 0)
            existing = session.query(DataSourceProvenanceModel).filter_by(id=source_id).first()
            if existing:
                existing.download_date = now_str
                if count > 0:
                    existing.record_count = count
            else:
                prov = DataSourceProvenanceModel(
                    id=source_id,
                    name=meta["name"],
                    url=meta["url"],
                    license=meta["license"],
                    download_date=now_str,
                    record_count=count,
                    geographic_coverage=meta["geographic_coverage"],
                    temporal_coverage=meta["temporal_coverage"],
                    known_limitations=meta["known_limitations"],
                    status="active"
                )
                session.add(prov)
        session.commit()
        logger.info("Registered %d dataset provenance records successfully.", len(PROVENANCE_METADATA))
    except Exception as exc:
        session.rollback()
        logger.error("Failed to register provenance records: %s", exc)
        raise
    finally:
        session.close()

def get_all_provenance() -> List[Dict[str, Any]]:
    """Retrieves all registered provenance records."""
    session = SessionLocal()
    try:
        records = session.query(DataSourceProvenanceModel).all()
        return [
            {
                "id": r.id,
                "name": r.name,
                "url": r.url,
                "license": r.license,
                "download_date": r.download_date,
                "record_count": r.record_count,
                "geographic_coverage": r.geographic_coverage,
                "temporal_coverage": r.temporal_coverage,
                "known_limitations": r.known_limitations,
                "status": r.status
            }
            for r in records
        ]
    finally:
        session.close()

