"""Standalone script to regenerate all Power BI Star-Schema CSV and Parquet reporting files."""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.export_service import ExportService
from backend.geospatial.geo_converter import GeoConverter
from backend.config.logging_config import logger

def main():
    logger.info("Executing Power BI data export...")
    counts = ExportService.export_powerbi_star_schema()
    GeoConverter.export_all_to_parquet()
    logger.info("Successfully exported %d tables to data/reporting/ and data/processed/.", len(counts))
    for tbl, cnt in counts.items():
        print(f"  {tbl:26}: {cnt:,} rows")

if __name__ == "__main__":
    main()

