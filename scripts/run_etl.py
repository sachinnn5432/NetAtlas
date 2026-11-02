"""Master ETL Execution Pipeline for NetAtlas.

Orchestrates authentic data ingestion, schema validation, geospatial processing,
quality audits, and Power BI reporting exports.
"""

import sys
import time
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config.logging_config import logger
from backend.models.database import init_db
from backend.ingestion.osm_loader import populate_country_reference
from backend.ingestion.submarine_cable_loader import SubmarineCableLoader
from backend.ingestion.peeringdb_client import PeeringDBClient
from backend.ingestion.data_source_registry import register_provenance_records
from backend.preprocessing.quality_reporter import QualityReporter
from backend.services.export_service import ExportService

def run_pipeline():
    """Executes the complete NetAtlas ETL pipeline."""
    start_time = time.time()
    logger.info("==================================================")
    logger.info("STARTING NETATLAS INFRASTRUCTURE INGESTION PIPELINE")
    logger.info("==================================================")

    # 1. Database Initialization
    logger.info("[Step 1/8] Initializing database schema...")
    init_db()

    # 2. Country Reference Loading
    logger.info("[Step 2/8] Populating standard ISO country references...")
    populate_country_reference()

    # 3. Submarine Cable & Landing Station Ingestion
    logger.info("[Step 3/8] Ingesting authentic submarine cables and landing stations...")
    cable_loader = SubmarineCableLoader()
    lp_count = cable_loader.ingest_landing_stations()
    cable_count = cable_loader.ingest_cables(fetch_details_sample=120)

    # 4. PeeringDB Public Data Ingestion
    logger.info("[Step 4/8] Ingesting PeeringDB IXPs, Facilities, and Networks...")
    pdb_client = PeeringDBClient()
    ixp_count = pdb_client.ingest_ixps()
    fac_count = pdb_client.ingest_facilities()
    net_count = pdb_client.ingest_networks(limit=2500)
    rel_count = pdb_client.ingest_network_ix_relationships(limit=8000)

    # 5. Provenance Registration
    logger.info("[Step 5/8] Registering dataset provenance and licensing metadata...")
    register_provenance_records({
        "telegeography_cables": cable_count,
        "telegeography_landing_stations": lp_count,
        "peeringdb_ix": ixp_count,
        "peeringdb_fac": fac_count,
        "peeringdb_net": net_count,
        "peeringdb_netixlan": rel_count
    })

    # 6. Data Quality Audit
    logger.info("[Step 6/8] Executing automated data quality and integrity audit...")
    audit = QualityReporter.generate_full_audit()

    # 7. Power BI Star Schema Export
    logger.info("[Step 7/8] Generating Power BI Star-Schema analytical exports...")
    table_counts = ExportService.export_powerbi_star_schema()

    # 8. Pipeline Summary
    elapsed = round(time.time() - start_time, 2)
    logger.info("==================================================")
    logger.info("ETL PIPELINE COMPLETED SUCCESSFULLY IN %.2f SECONDS", elapsed)
    logger.info("  Submarine Cables:    %d", cable_count)
    logger.info("  Landing Stations:    %d", lp_count)
    logger.info("  Internet Exchanges:  %d", ixp_count)
    logger.info("  Data Facilities:     %d", fac_count)
    logger.info("  Network Operators:   %d", net_count)
    logger.info("  Interconnections:    %d", rel_count)
    logger.info("==================================================")

if __name__ == "__main__":
    run_pipeline()

