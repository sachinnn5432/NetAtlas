"""Unified Search Engine across Global Internet Infrastructure Entities."""

from typing import Dict, Any, List
from sqlalchemy import or_
from backend.models.database import SessionLocal
from backend.models.db_models import (
    CableModel, LandingStationModel, IXPModel, FacilityModel
)

class SearchService:
    """Executes high-speed multi-entity search."""

    @classmethod
    def global_search(cls, query_str: str, limit_per_category: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Searches across Cables, IXPs, Landing Stations, and Facilities."""
        if not query_str or len(query_str.strip()) < 2:
            return {"cables": [], "ixps": [], "landing_stations": [], "facilities": []}

        term = f"%{query_str.strip()}%"
        session = SessionLocal()
        try:
            # 1. Cables
            cables = session.query(CableModel).filter(
                or_(CableModel.name.ilike(term), CableModel.owners.ilike(term))
            ).limit(limit_per_category).all()

            # 2. IXPs
            ixps = session.query(IXPModel).filter(
                or_(IXPModel.name.ilike(term), IXPModel.city.ilike(term), IXPModel.country.ilike(term))
            ).order_by(IXPModel.net_count.desc()).limit(limit_per_category).all()

            # 3. Landing Stations
            lps = session.query(LandingStationModel).filter(
                or_(LandingStationModel.name.ilike(term), LandingStationModel.country.ilike(term))
            ).limit(limit_per_category).all()

            # 4. Facilities
            facs = session.query(FacilityModel).filter(
                or_(FacilityModel.name.ilike(term), FacilityModel.city.ilike(term), FacilityModel.org_name.ilike(term))
            ).order_by(FacilityModel.net_count.desc()).limit(limit_per_category).all()

            return {
                "cables": [{"id": c.id, "name": c.name, "rfs_year": c.rfs_year, "length_km": c.length_km, "type": "Submarine Cable"} for c in cables],
                "ixps": [{"id": ix.id, "name": ix.name, "city": ix.city, "country": ix.country, "net_count": ix.net_count, "type": "Internet Exchange"} for ix in ixps],
                "landing_stations": [{"id": lp.id, "name": lp.name, "country": lp.country, "lat": lp.latitude, "lon": lp.longitude, "type": "Landing Station"} for lp in lps],
                "facilities": [{"id": f.id, "name": f.name, "city": f.city, "country": f.country, "lat": f.latitude, "lon": f.longitude, "net_count": f.net_count, "type": "Interconnection Facility"} for f in facs]
            }
        finally:
            session.close()

