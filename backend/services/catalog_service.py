"""Catalog Service for NetAtlas Infrastructure Entities."""

from typing import Dict, Any, List, Optional
import json
from sqlalchemy import or_
from backend.models.database import SessionLocal
from backend.models.db_models import (
    CableModel, LandingStationModel, IXPModel, FacilityModel, NetworkModel
)
from backend.geospatial.spatial_index import SpatialBBox

class CatalogService:
    """Provides querying, filtering, and spatial slicing for all infrastructure types."""

    @staticmethod
    def get_cables(
        search: Optional[str] = None,
        rfs_year: Optional[int] = None,
        is_planned: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Queries submarine cables with filtering."""
        session = SessionLocal()
        try:
            q = session.query(CableModel)
            if search:
                term = f"%{search.strip()}%"
                q = q.filter(or_(CableModel.name.ilike(term), CableModel.owners.ilike(term)))
            if rfs_year:
                q = q.filter(CableModel.rfs_year == rfs_year)
            if is_planned is not None:
                q = q.filter(CableModel.is_planned == is_planned)

            total = q.count()
            cables = q.offset(offset).limit(limit).all()

            results = []
            for c in cables:
                countries = json.loads(c.countries_connected) if c.countries_connected else []
                results.append({
                    "id": c.id,
                    "name": c.name,
                    "rfs_year": c.rfs_year,
                    "length_km": c.length_km,
                    "owners": c.owners,
                    "suppliers": c.suppliers,
                    "is_planned": c.is_planned,
                    "landing_points_count": c.landing_points_count,
                    "countries_connected": countries,
                    "source": c.source
                })
            return results
        finally:
            session.close()

    @staticmethod
    def get_cable_detail(cable_id: str) -> Optional[Dict[str, Any]]:
        """Gets full record for a submarine cable including geometry."""
        session = SessionLocal()
        try:
            c = session.query(CableModel).filter_by(id=cable_id).first()
            if not c:
                return None
            countries = json.loads(c.countries_connected) if c.countries_connected else []
            geom = json.loads(c.geometry_geojson) if c.geometry_geojson else None
            return {
                "id": c.id,
                "name": c.name,
                "rfs_year": c.rfs_year,
                "length_km": c.length_km,
                "owners": c.owners,
                "suppliers": c.suppliers,
                "is_planned": c.is_planned,
                "url": c.url,
                "landing_points_count": c.landing_points_count,
                "countries_connected": countries,
                "geometry": geom,
                "source": c.source
            }
        finally:
            session.close()

    @staticmethod
    def get_ixps(
        country: Optional[str] = None,
        city: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Queries IXPs with filtering."""
        session = SessionLocal()
        try:
            q = session.query(IXPModel)
            if country:
                q = q.filter(IXPModel.country == country.upper().strip())
            if city:
                q = q.filter(IXPModel.city.ilike(f"%{city.strip()}%"))
            if search:
                term = f"%{search.strip()}%"
                q = q.filter(or_(IXPModel.name.ilike(term), IXPModel.name_long.ilike(term), IXPModel.city.ilike(term)))

            ixps = q.order_by(IXPModel.net_count.desc()).offset(offset).limit(limit).all()
            return [{
                "id": ix.id,
                "name": ix.name,
                "name_long": ix.name_long,
                "city": ix.city,
                "country": ix.country,
                "region_continent": ix.region_continent,
                "media": ix.media,
                "proto_unicast": ix.proto_unicast,
                "proto_multicast": ix.proto_multicast,
                "proto_ipv6": ix.proto_ipv6,
                "net_count": ix.net_count,
                "fac_count": ix.fac_count,
                "website": ix.website,
                "status": ix.status,
                "source": ix.source
            } for ix in ixps]
        finally:
            session.close()

    @staticmethod
    def get_facilities(
        country: Optional[str] = None,
        city: Optional[str] = None,
        bbox: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Queries interconnection facilities."""
        session = SessionLocal()
        try:
            q = session.query(FacilityModel)
            if country:
                q = q.filter(FacilityModel.country == country.upper().strip())
            if city:
                q = q.filter(FacilityModel.city.ilike(f"%{city.strip()}%"))
            if search:
                term = f"%{search.strip()}%"
                q = q.filter(or_(FacilityModel.name.ilike(term), FacilityModel.org_name.ilike(term), FacilityModel.city.ilike(term)))

            if bbox:
                box = SpatialBBox.from_string(bbox)
                if box:
                    q = q.filter(
                        FacilityModel.longitude >= box.min_lon,
                        FacilityModel.longitude <= box.max_lon,
                        FacilityModel.latitude >= box.min_lat,
                        FacilityModel.latitude <= box.max_lat
                    )

            facs = q.order_by(FacilityModel.net_count.desc()).offset(offset).limit(limit).all()
            return [{
                "id": f.id,
                "name": f.name,
                "org_name": f.org_name,
                "city": f.city,
                "country": f.country,
                "latitude": f.latitude,
                "longitude": f.longitude,
                "net_count": f.net_count,
                "ix_count": f.ix_count,
                "status": f.status,
                "source": f.source
            } for f in facs]
        finally:
            session.close()

    @staticmethod
    def get_landing_stations(
        country: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 200,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Queries landing stations."""
        session = SessionLocal()
        try:
            q = session.query(LandingStationModel)
            if country:
                q = q.filter(or_(
                    LandingStationModel.country_code == country.upper().strip(),
                    LandingStationModel.country.ilike(f"%{country.strip()}%")
                ))
            if search:
                term = f"%{search.strip()}%"
                q = q.filter(or_(LandingStationModel.name.ilike(term), LandingStationModel.country.ilike(term)))

            lps = q.offset(offset).limit(limit).all()
            return [{
                "id": lp.id,
                "name": lp.name,
                "country": lp.country,
                "country_code": lp.country_code,
                "latitude": lp.latitude,
                "longitude": lp.longitude,
                "is_tbd": lp.is_tbd,
                "source": lp.source
            } for lp in lps]
        finally:
            session.close()

