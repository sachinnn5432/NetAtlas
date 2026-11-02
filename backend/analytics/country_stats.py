"""Country-Level Infrastructure Aggregation and Comparison Analytics for NetAtlas."""

from typing import Dict, Any, List, Optional
import json
import pandas as pd
from sqlalchemy import func
from backend.models.database import SessionLocal
from backend.models.db_models import (
    IXPModel, FacilityModel, LandingStationModel, CableModel, CountryReferenceModel
)
from backend.ingestion.osm_loader import get_country_info
from backend.config.logging_config import logger

class CountryAnalytics:
    """Computes country-level infrastructure summaries and comparative metrics."""

    @classmethod
    def get_all_country_summaries(cls) -> List[Dict[str, Any]]:
        """Aggregates IXPs, Facilities, Landing Stations, and Cables per country."""
        session = SessionLocal()
        try:
            # 1. IXPs by country
            ixp_counts = dict(
                session.query(IXPModel.country, func.count(IXPModel.id))
                .group_by(IXPModel.country)
                .all()
            )

            # 2. Facilities by country
            fac_counts = dict(
                session.query(FacilityModel.country, func.count(FacilityModel.id))
                .group_by(FacilityModel.country)
                .all()
            )

            # 3. Landing stations by country
            lp_records = session.query(LandingStationModel.country, LandingStationModel.country_code).all()
            lp_counts = {}
            for country_name, country_code in lp_records:
                key = country_code or country_name
                lp_counts[key] = lp_counts.get(key, 0) + 1

            # 4. Cables by connected country
            cables = session.query(CableModel.countries_connected).all()
            cable_counts = {}
            for (c_list_json,) in cables:
                if c_list_json:
                    try:
                        c_list = json.loads(c_list_json)
                        for c_name in c_list:
                            cable_counts[c_name] = cable_counts.get(c_name, 0) + 1
                    except Exception:
                        pass

            # Query country references
            country_refs = session.query(CountryReferenceModel).all()
            summaries = []

            for ref in country_refs:
                iso2 = ref.iso2
                c_name = ref.country_name
                region = ref.region

                n_ixp = ixp_counts.get(iso2, 0)
                n_fac = fac_counts.get(iso2, 0)
                n_lp = lp_counts.get(iso2, 0) or lp_counts.get(c_name, 0)
                n_cable = cable_counts.get(c_name, 0)

                # Density composite score: weighted sum of diverse layers
                # (Cable connectivity + Landing capacity + IXP peering + Facility presence)
                density_score = round(
                    (n_ixp * 2.0) + (n_fac * 0.5) + (n_lp * 3.0) + (n_cable * 4.0),
                    2
                )

                summaries.append({
                    "country_code": iso2,
                    "country_name": c_name,
                    "region": region,
                    "subregion": ref.subregion,
                    "latitude": ref.latitude,
                    "longitude": ref.longitude,
                    "ixp_count": n_ixp,
                    "facility_count": n_fac,
                    "landing_station_count": n_lp,
                    "cable_count": n_cable,
                    "infrastructure_density_score": density_score
                })

            # Sort by density score descending
            summaries.sort(key=lambda x: x["infrastructure_density_score"], reverse=True)
            return summaries
        finally:
            session.close()

    @classmethod
    def get_country_detail(cls, country_code: str) -> Optional[Dict[str, Any]]:
        """Retrieves comprehensive infrastructure profile for a single country."""
        summaries = cls.get_all_country_summaries()
        for s in summaries:
            if s["country_code"].upper() == country_code.upper():
                return s
        return None

