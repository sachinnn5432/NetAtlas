"""Geospatial Converter and GeoPandas Integration for NetAtlas."""

import json
from typing import List, Dict, Any, Optional
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, shape, mapping
from backend.models.database import SessionLocal
from backend.models.db_models import (
    CableModel, LandingStationModel, IXPModel, FacilityModel
)
from backend.config.settings import PROCESSED_DATA_DIR, GEOJSON_DATA_DIR
from backend.config.logging_config import logger

class GeoConverter:
    """Converts database records to GeoDataFrames, Parquet layers, and GeoJSON."""

    @staticmethod
    def get_cables_geodataframe(simplify_tolerance: Optional[float] = None) -> gpd.GeoDataFrame:
        """Loads submarine cables into a GeoPandas GeoDataFrame."""
        session = SessionLocal()
        try:
            records = session.query(CableModel).all()
            data = []
            for r in records:
                if not r.geometry_geojson:
                    continue
                try:
                    raw_geom = json.loads(r.geometry_geojson)
                    s_geom = shape(raw_geom)
                    if simplify_tolerance:
                        s_geom = s_geom.simplify(tolerance=simplify_tolerance, preserve_topology=True)

                    data.append({
                        "id": r.id,
                        "name": r.name,
                        "rfs_year": r.rfs_year,
                        "length_km": r.length_km,
                        "owners": r.owners,
                        "is_planned": r.is_planned,
                        "landing_points_count": r.landing_points_count,
                        "geometry": s_geom
                    })
                except Exception as e:
                    logger.debug("Failed parsing cable geom %s: %e", r.id, e)

            if not data:
                return gpd.GeoDataFrame()

            gdf = gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")
            return gdf
        finally:
            session.close()

    @staticmethod
    def get_landing_stations_geodataframe() -> gpd.GeoDataFrame:
        """Loads landing stations into a GeoPandas GeoDataFrame."""
        session = SessionLocal()
        try:
            records = session.query(LandingStationModel).all()
            data = []
            for r in records:
                if r.latitude is not None and r.longitude is not None:
                    data.append({
                        "id": r.id,
                        "name": r.name,
                        "country": r.country,
                        "country_code": r.country_code,
                        "cable_count": r.cable_count,
                        "is_tbd": r.is_tbd,
                        "geometry": Point(r.longitude, r.latitude)
                    })
            if not data:
                return gpd.GeoDataFrame()
            gdf = gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")
            return gdf
        finally:
            session.close()

    @staticmethod
    def get_facilities_geodataframe() -> gpd.GeoDataFrame:
        """Loads interconnection facilities with valid coordinates into a GeoDataFrame."""
        session = SessionLocal()
        try:
            records = session.query(FacilityModel).filter(
                FacilityModel.latitude.isnot(None),
                FacilityModel.longitude.isnot(None)
            ).all()
            data = []
            for r in records:
                data.append({
                    "id": r.id,
                    "name": r.name,
                    "city": r.city,
                    "country": r.country,
                    "region": r.region_continent,
                    "net_count": r.net_count,
                    "ix_count": r.ix_count,
                    "geometry": Point(r.longitude, r.latitude)
                })
            if not data:
                return gpd.GeoDataFrame()
            return gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")
        finally:
            session.close()

    @classmethod
    def export_all_to_parquet(cls):
        """Exports all geospatial layers to Parquet for analytical workflows."""
        logger.info("Exporting geospatial layers to Parquet...")
        cables_gdf = cls.get_cables_geodataframe()
        if not cables_gdf.empty:
            cables_gdf.to_parquet(PROCESSED_DATA_DIR / "cables.parquet")

        lps_gdf = cls.get_landing_stations_geodataframe()
        if not lps_gdf.empty:
            lps_gdf.to_parquet(PROCESSED_DATA_DIR / "landing_stations.parquet")

        facs_gdf = cls.get_facilities_geodataframe()
        if not facs_gdf.empty:
            facs_gdf.to_parquet(PROCESSED_DATA_DIR / "facilities.parquet")

        logger.info("Geospatial layers successfully serialized to Parquet.")

