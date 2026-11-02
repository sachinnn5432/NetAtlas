"""PeeringDB API Client and Ingestion Engine.

Fetches and normalizes Internet Exchange Points (IXPs), facilities,
networks (Autonomous Systems), and interconnection topologies from PeeringDB.
Implements retry handling with exponential backoff, rate limiting, and local raw caching.
"""

from typing import Dict, Any, List, Optional
import time
import json
import requests
from pathlib import Path
from backend.config.settings import (
    PEERINGDB_API_BASE,
    PEERINGDB_RATE_LIMIT_DELAY_SEC,
    REQUEST_TIMEOUT_SEC,
    RAW_DATA_DIR,
    USER_AGENT
)
from backend.config.logging_config import logger
from backend.models.database import SessionLocal
from backend.models.db_models import (
    IXPModel,
    FacilityModel,
    NetworkModel,
    NetworkIXRelationshipModel,
    NetworkFacilityRelationshipModel
)
from backend.ingestion.geojson_loader import validate_wgs84_coordinates

class PeeringDBClient:
    """Client for querying and ingesting PeeringDB public infrastructure data."""

    def __init__(self, base_url: str = PEERINGDB_API_BASE):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/json"
        })

    def _fetch_endpoint(self, endpoint: str, max_records: Optional[int] = None, page_size: int = 250, max_retries: int = 3) -> List[Dict[str, Any]]:
        """Executes paginated GET requests with exponential backoff and rate limiting."""
        raw_file = RAW_DATA_DIR / f"peeringdb_{endpoint}.json"

        # Check local cache first to avoid excessive remote API calls
        if raw_file.exists() and raw_file.stat().st_size > 1000:
            logger.info("Loading cached PeeringDB %s from: %s", endpoint, raw_file)
            try:
                with open(raw_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                    if isinstance(cached_data, dict) and "data" in cached_data:
                        return cached_data["data"]
                    elif isinstance(cached_data, list):
                        return cached_data
            except Exception as e:
                logger.warning("Cache read failed for %s, fetching from network: %s", endpoint, e)

        url = f"{self.base_url}/{endpoint}"
        all_records = []
        skip = 0

        logger.info("Beginning paginated fetch for PeeringDB %s (page_size=%d)...", endpoint, page_size)

        while True:
            params = {"limit": page_size, "skip": skip}
            page_data = None
            delay = 1.0

            for attempt in range(1, max_retries + 1):
                try:
                    response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT_SEC)
                    if response.status_code == 200:
                        payload = response.json()
                        page_data = payload.get("data", [])
                        break
                    elif response.status_code == 429:
                        logger.warning("PeeringDB rate limit encountered (429) at skip=%d. Backing off %0.1fs", skip, delay)
                        time.sleep(delay)
                        delay *= 2
                    else:
                        logger.error("PeeringDB HTTP error %d at skip=%d: %s", response.status_code, skip, response.text[:200])
                        time.sleep(delay)
                        delay *= 2
                except requests.RequestException as exc:
                    logger.warning("PeeringDB request exception on %s skip=%d (attempt %d): %s", endpoint, skip, attempt, exc)
                    time.sleep(delay)
                    delay *= 2

            if page_data is None or len(page_data) == 0:
                break

            all_records.extend(page_data)
            logger.info("Fetched %d records so far for PeeringDB %s (skip=%d)", len(all_records), endpoint, skip)

            if max_records and len(all_records) >= max_records:
                all_records = all_records[:max_records]
                break

            if len(page_data) < page_size:
                # Reached end of records
                break

            skip += page_size
            time.sleep(PEERINGDB_RATE_LIMIT_DELAY_SEC)

        # Cache full dataset locally
        if all_records:
            try:
                with open(raw_file, "w", encoding="utf-8") as f:
                    json.dump({"data": all_records}, f)
                logger.info("Saved %d records to local cache: %s", len(all_records), raw_file)
            except Exception as e:
                logger.warning("Failed saving cache for %s: %s", endpoint, e)

        return all_records

    def ingest_facilities(self, max_records: Optional[int] = 3000) -> int:
        """Ingests colocation and data centre facilities."""
        records = self._fetch_endpoint("fac", max_records=max_records, page_size=250)
        if not records:
            logger.warning("No facility records retrieved.")
            return 0

        session = SessionLocal()
        inserted_or_updated = 0
        try:
            for r in records:
                fac_id = r.get("id")
                if not fac_id:
                    continue

                lat = r.get("latitude")
                lon = r.get("longitude")
                # Normalize and validate coordinates
                if lat is not None and lon is not None:
                    try:
                        lat = float(lat)
                        lon = float(lon)
                        if not validate_wgs84_coordinates(lon, lat):
                            lat, lon = None, None
                    except (ValueError, TypeError):
                        lat, lon = None, None
                else:
                    lat, lon = None, None

                existing = session.query(FacilityModel).filter_by(id=fac_id).first()
                if not existing:
                    existing = FacilityModel(id=fac_id)
                    session.add(existing)

                existing.name = (r.get("name") or "Unnamed Facility").strip()
                existing.org_name = (r.get("org_name") or None)
                existing.city = (r.get("city") or "").strip()
                existing.country = (r.get("country") or "").upper().strip()
                existing.region_continent = (r.get("region_continent") or None)
                existing.state = (r.get("state") or None)
                existing.zipcode = (r.get("zipcode") or None)
                existing.address1 = (r.get("address1") or None)
                existing.latitude = lat
                existing.longitude = lon
                existing.net_count = int(r.get("net_count") or 0)
                existing.ix_count = int(r.get("ix_count") or 0)
                existing.diverse_serving_substations = bool(r.get("diverse_serving_substations")) if r.get("diverse_serving_substations") is not None else None
                existing.website = (r.get("website") or None)
                existing.status = (r.get("status") or "ok")
                inserted_or_updated += 1

            session.commit()
            logger.info("Ingested %d PeeringDB facilities.", inserted_or_updated)
            return inserted_or_updated
        except Exception as exc:
            session.rollback()
            logger.error("Failed to commit facilities: %s", exc)
            raise
        finally:
            session.close()

    def ingest_ixps(self, max_records: Optional[int] = None) -> int:
        """Ingests Internet Exchange Points (IXPs)."""
        records = self._fetch_endpoint("ix", max_records=max_records, page_size=250)
        if not records:
            logger.warning("No IXP records retrieved.")
            return 0

        session = SessionLocal()
        inserted_or_updated = 0
        try:
            for r in records:
                ix_id = r.get("id")
                if not ix_id:
                    continue

                existing = session.query(IXPModel).filter_by(id=ix_id).first()
                if not existing:
                    existing = IXPModel(id=ix_id)
                    session.add(existing)

                existing.name = (r.get("name") or f"IXP-{ix_id}").strip()
                existing.name_long = (r.get("name_long") or None)
                existing.city = (r.get("city") or "").strip()
                existing.country = (r.get("country") or "").upper().strip()
                existing.region_continent = (r.get("region_continent") or None)
                existing.media = (r.get("media") or None)
                existing.proto_unicast = bool(r.get("proto_unicast", True))
                existing.proto_multicast = bool(r.get("proto_multicast", False))
                existing.proto_ipv6 = bool(r.get("proto_ipv6", True))
                existing.website = (r.get("website") or None)
                existing.net_count = int(r.get("net_count") or 0)
                existing.fac_count = int(r.get("fac_count") or 0)
                existing.created_date = str(r.get("created") or "")
                existing.updated_date = str(r.get("updated") or "")
                existing.status = (r.get("status") or "ok")

                inserted_or_updated += 1

            session.commit()
            logger.info("Ingested %d PeeringDB IXPs.", inserted_or_updated)
            return inserted_or_updated
        except Exception as exc:
            session.rollback()
            logger.error("Failed to commit IXPs: %s", exc)
            raise
        finally:
            session.close()

    def ingest_networks(self, limit: Optional[int] = None) -> int:
        """Ingests networks (Autonomous Systems / Operators)."""
        records = self._fetch_endpoint("net", max_records=limit, page_size=250)
        if not records:
            return 0

        session = SessionLocal()
        inserted_or_updated = 0
        try:
            for r in records:
                net_id = r.get("id")
                asn = r.get("asn")
                if not net_id or not asn:
                    continue

                existing = session.query(NetworkModel).filter_by(id=net_id).first()
                if not existing:
                    existing = NetworkModel(id=net_id)
                    session.add(existing)

                existing.name = (r.get("name") or f"AS{asn}").strip()
                existing.aka = (r.get("aka") or None)
                existing.asn = int(asn)
                existing.info_type = (r.get("info_type") or None)
                existing.policy_general = (r.get("policy_general") or None)
                existing.website = (r.get("website") or None)
                existing.netixlan_count = int(r.get("netixlan_count") or 0)
                existing.netfac_count = int(r.get("netfac_count") or 0)
                inserted_or_updated += 1

            session.commit()
            logger.info("Ingested %d PeeringDB networks.", inserted_or_updated)
            return inserted_or_updated
        except Exception as exc:
            session.rollback()
            logger.error("Failed to commit networks: %s", exc)
            raise
        finally:
            session.close()

    def ingest_network_ix_relationships(self, limit: Optional[int] = 10000) -> int:
        """Ingests Network-to-IX interconnection relationships (netixlan)."""
        records = self._fetch_endpoint("netixlan", max_records=limit, page_size=250)
        if not records:
            return 0

        session = SessionLocal()
        inserted = 0
        try:
            # Query existing net and ix IDs to guarantee relational integrity
            valid_net_ids = {row[0] for row in session.query(NetworkModel.id).all()}
            valid_ix_ids = {row[0] for row in session.query(IXPModel.id).all()}

            for r in records:
                rel_id = r.get("id")
                net_id = r.get("net_id")
                ix_id = r.get("ix_id")
                asn = r.get("asn")

                if not rel_id or not net_id or not ix_id or not asn:
                    continue
                if net_id not in valid_net_ids or ix_id not in valid_ix_ids:
                    continue

                existing = session.query(NetworkIXRelationshipModel).filter_by(id=rel_id).first()
                if not existing:
                    existing = NetworkIXRelationshipModel(id=rel_id)
                    session.add(existing)

                existing.net_id = net_id
                existing.ix_id = ix_id
                existing.asn = int(asn)
                existing.speed = int(r.get("speed") or 0)
                existing.is_rs_peer = bool(r.get("is_rs_peer", False))
                existing.operational = bool(r.get("operational", True))
                existing.status = (r.get("status") or "ok")
                inserted += 1

            session.commit()
            logger.info("Ingested %d PeeringDB Network-to-IX relationships.", inserted)
            return inserted
        except Exception as exc:
            session.rollback()
            logger.error("Failed to commit Network-to-IX relationships: %s", exc)
            raise
        finally:
            session.close()
