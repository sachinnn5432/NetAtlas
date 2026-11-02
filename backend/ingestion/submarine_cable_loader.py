"""Submarine Cable and Landing Station Ingestion Engine.

Fetches and normalizes authentic global submarine fiber-optic cables,
landing stations, geometries, commissioning years, lengths, and country connectivity.
"""

from typing import Dict, Any, List, Optional
import json
import re
import requests
from pathlib import Path
from backend.config.settings import (
    CABLE_GEOJSON_URL,
    LANDING_POINT_GEOJSON_URL,
    CABLE_ALL_URL,
    CABLE_DETAIL_BASE_URL,
    REQUEST_TIMEOUT_SEC,
    RAW_DATA_DIR,
    GEOJSON_DATA_DIR,
    USER_AGENT
)
from backend.config.logging_config import logger
from backend.models.database import SessionLocal
from backend.models.db_models import CableModel, LandingStationModel
from backend.ingestion.geojson_loader import (
    validate_wgs84_coordinates,
    validate_and_clean_geometry,
    build_feature_collection
)
from backend.ingestion.osm_loader import resolve_country_code

class SubmarineCableLoader:
    """Ingests global submarine fiber-optic cable routes and landing points."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/json"
        })

    def _fetch_or_cache(self, url: str, filename: str) -> Optional[Any]:
        """Fetches from URL or reads from raw cache."""
        cache_path = RAW_DATA_DIR / filename
        if cache_path.exists() and cache_path.stat().st_size > 1000:
            logger.info("Loading cached cable resource: %s", filename)
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning("Cache read failed for %s, refetching: %s", filename, e)

        try:
            logger.info("Fetching remote resource: %s", url)
            resp = self.session.get(url, timeout=REQUEST_TIMEOUT_SEC)
            if resp.status_code == 200:
                data = resp.json()
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(data, f)
                return data
            else:
                logger.error("Failed fetching %s (status %d)", url, resp.status_code)
                return None
        except Exception as exc:
            logger.error("Exception fetching %s: %s", url, exc)
            return None

    def ingest_landing_stations(self) -> int:
        """Ingests landing points/stations with valid geographic coordinates."""
        data = self._fetch_or_cache(LANDING_POINT_GEOJSON_URL, "landing_point_geo.json")
        if not data or "features" not in data:
            logger.error("No landing point features found.")
            return 0

        features = data["features"]
        session = SessionLocal()
        inserted_count = 0
        valid_geojson_features = []

        try:
            for feat in features:
                props = feat.get("properties", {})
                geom = feat.get("geometry", {})
                lp_id = props.get("id") or feat.get("id")
                coords = geom.get("coordinates")

                if not lp_id or not coords or len(coords) < 2:
                    continue

                lon, lat = coords[0], coords[1]
                if not validate_wgs84_coordinates(lon, lat):
                    logger.warning("Invalid landing station coordinate for %s: (%s, %s)", lp_id, lon, lat)
                    continue

                full_name = props.get("name", "Unknown Station")
                # Parse country from name if format is 'City, Country'
                country_name = "Unknown"
                if "," in full_name:
                    parts = [p.strip() for p in full_name.split(",")]
                    country_name = parts[-1]
                iso2 = resolve_country_code(country_name)

                existing = session.query(LandingStationModel).filter_by(id=lp_id).first()
                if not existing:
                    existing = LandingStationModel(id=lp_id)
                    session.add(existing)

                existing.name = full_name
                existing.country = country_name
                existing.country_code = iso2
                existing.latitude = float(lat)
                existing.longitude = float(lon)
                existing.is_tbd = bool(props.get("is_tbd", False))
                existing.source = "TeleGeography / Public Submarine Cable API"

                inserted_count += 1

                valid_geojson_features.append({
                    "type": "Feature",
                    "id": lp_id,
                    "properties": {
                        "id": lp_id,
                        "name": full_name,
                        "country": country_name,
                        "country_code": iso2,
                        "is_tbd": existing.is_tbd
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(lon), float(lat)]
                    }
                })

            session.commit()

            # Save clean GeoJSON for Leaflet
            geojson_out = GEOJSON_DATA_DIR / "landing_stations.geojson"
            with open(geojson_out, "w", encoding="utf-8") as f:
                json.dump(build_feature_collection(valid_geojson_features), f)

            logger.info("Ingested %d authentic cable landing stations.", inserted_count)
            return inserted_count
        except Exception as exc:
            session.rollback()
            logger.error("Error committing landing stations: %s", exc)
            raise
        finally:
            session.close()

    def ingest_cables(self, fetch_details_sample: int = 150) -> int:
        """Ingests submarine cable routes, properties, geometries, and landing points."""
        geo_data = self._fetch_or_cache(CABLE_GEOJSON_URL, "cable_geo.json")
        all_meta = self._fetch_or_cache(CABLE_ALL_URL, "cable_all.json") or []

        if not geo_data or "features" not in geo_data:
            logger.error("No cable route features found.")
            return 0

        # Build metadata lookup map
        meta_lookup = {}
        for c in all_meta:
            cid = c.get("id")
            if cid:
                meta_lookup[cid] = c

        features = geo_data.get("features", [])
        # Group segments by cable_id so multi-segment routes are unified cleanly
        cables_by_id: Dict[str, Dict[str, Any]] = {}
        for feat in features:
            props = feat.get("properties", {})
            geom = feat.get("geometry", {})
            cable_id = props.get("id")

            if not cable_id or not geom:
                continue

            cleaned_geom, err = validate_and_clean_geometry(geom)
            if not cleaned_geom:
                logger.warning("Cable geometry discarded for %s: %s", cable_id, err)
                continue

            cable_name = props.get("name") or meta_lookup.get(cable_id, {}).get("name") or cable_id

            if cable_id not in cables_by_id:
                # Initialize
                coords = []
                if cleaned_geom.get("type") == "MultiLineString":
                    coords.extend(cleaned_geom.get("coordinates", []))
                elif cleaned_geom.get("type") == "LineString":
                    coords.append(cleaned_geom.get("coordinates", []))

                cables_by_id[cable_id] = {
                    "id": cable_id,
                    "name": cable_name,
                    "color": props.get("color", "#1f77b4"),
                    "coordinates": coords
                }
            else:
                # Merge additional route segments into the MultiLineString
                if cleaned_geom.get("type") == "MultiLineString":
                    cables_by_id[cable_id]["coordinates"].extend(cleaned_geom.get("coordinates", []))
                elif cleaned_geom.get("type") == "LineString":
                    cables_by_id[cable_id]["coordinates"].append(cleaned_geom.get("coordinates", []))

        features_unified = []
        for cid, cdata in cables_by_id.items():
            unified_geom = {
                "type": "MultiLineString",
                "coordinates": cdata["coordinates"]
            }
            features_unified.append((cid, cdata["name"], cdata["color"], unified_geom))

        session = SessionLocal()
        inserted_count = 0
        valid_geojson_features = []

        try:
            for cable_id, cable_name, color, cleaned_geom in features_unified:
                existing = session.query(CableModel).filter_by(id=cable_id).first()
                if not existing:
                    existing = CableModel(id=cable_id)
                    session.add(existing)

                existing.name = cable_name
                existing.geometry_geojson = json.dumps(cleaned_geom)
                existing.source = "TeleGeography / Public Submarine Cable API"

                inserted_count += 1

                valid_geojson_features.append({
                    "type": "Feature",
                    "id": cable_id,
                    "properties": {
                        "id": cable_id,
                        "name": cable_name,
                        "color": color,
                        "rfs_year": existing.rfs_year,
                        "length_km": existing.length_km,
                        "is_planned": existing.is_planned,
                        "owners": existing.owners
                    },
                    "geometry": cleaned_geom
                })

            session.commit()

            # Now enrich cable details (RFS year, length, owners, connected landing points)
            # We fetch sample or cached details for high-profile cables
            self._enrich_cable_details(session, limit=fetch_details_sample)

            # Re-export clean GeoJSON with updated attributes
            cables = session.query(CableModel).all()
            export_features = []
            for c in cables:
                if c.geometry_geojson:
                    geom = json.loads(c.geometry_geojson)
                    export_features.append({
                        "type": "Feature",
                        "id": c.id,
                        "properties": {
                            "id": c.id,
                            "name": c.name,
                            "rfs_year": c.rfs_year,
                            "length_km": c.length_km,
                            "owners": c.owners,
                            "is_planned": c.is_planned,
                            "landing_points_count": c.landing_points_count,
                            "countries_connected": json.loads(c.countries_connected) if c.countries_connected else []
                        },
                        "geometry": geom
                    })

            geojson_out = GEOJSON_DATA_DIR / "submarine_cables.geojson"
            with open(geojson_out, "w", encoding="utf-8") as f:
                json.dump(build_feature_collection(export_features), f)

            logger.info("Ingested and geometry-verified %d global submarine cables.", inserted_count)
            return inserted_count
        except Exception as exc:
            session.rollback()
            logger.error("Error committing cables: %s", exc)
            raise
        finally:
            session.close()

    def _enrich_cable_details(self, session, limit: int = 150):
        """Enriches cable records with RFS year, length, owners, and landing stations."""
        cables_to_enrich = session.query(CableModel).limit(limit).all()
        logger.info("Enriching metadata for %d submarine cables...", len(cables_to_enrich))

        cable_details_dir = RAW_DATA_DIR / "cable_details"
        cable_details_dir.mkdir(parents=True, exist_ok=True)

        for cable in cables_to_enrich:
            cid = cable.id
            detail_file = cable_details_dir / f"{cid}.json"
            detail = None

            if detail_file.exists():
                try:
                    with open(detail_file, "r", encoding="utf-8") as f:
                        detail = json.load(f)
                except Exception:
                    detail = None

            if not detail:
                url = f"{CABLE_DETAIL_BASE_URL}/{cid}.json"
                try:
                    r = self.session.get(url, timeout=10)
                    if r.status_code == 200:
                        detail = r.json()
                        with open(detail_file, "w", encoding="utf-8") as f:
                            json.dump(detail, f)
                except Exception:
                    pass

            if detail:
                # Parse length
                length_str = str(detail.get("length", ""))
                length_km = None
                if length_str:
                    clean_len = re.sub(r"[^\d.]", "", length_str)
                    try:
                        length_km = float(clean_len)
                    except ValueError:
                        pass
                cable.length_km = length_km

                # Parse RFS year
                rfs = detail.get("rfs_year") or detail.get("rfs")
                try:
                    cable.rfs_year = int(rfs) if rfs else None
                except (ValueError, TypeError):
                    cable.rfs_year = None

                cable.owners = detail.get("owners")
                cable.suppliers = detail.get("suppliers")
                cable.is_planned = bool(detail.get("is_planned", False))
                cable.url = detail.get("url")

                # Landing points & countries
                lps = detail.get("landing_points", [])
                cable.landing_points_count = len(lps)
                countries = []
                for lp in lps:
                    cname = lp.get("country")
                    if cname and cname not in countries:
                        countries.append(cname)
                cable.countries_connected = json.dumps(countries)

        session.commit()
        logger.info("Completed cable metadata enrichment.")
