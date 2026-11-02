"""Pydantic validation schemas for NetAtlas API and data serialization."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class CableBase(BaseModel):
    id: str
    name: str
    rfs_year: Optional[int] = None
    length_km: Optional[float] = None
    owners: Optional[str] = None
    suppliers: Optional[str] = None
    is_planned: bool = False
    url: Optional[str] = None
    landing_points_count: int = 0
    countries_connected: Optional[List[str]] = None
    source: str = "TeleGeography / Public Submarine Cable API"

class LandingStationBase(BaseModel):
    id: str
    name: str
    country: str
    country_code: Optional[str] = None
    latitude: float
    longitude: float
    is_tbd: bool = False
    cable_count: int = 1
    connected_cables: Optional[List[str]] = None
    source: str = "TeleGeography / Public Submarine Cable API"

class IXPBase(BaseModel):
    id: int
    name: str
    name_long: Optional[str] = None
    city: Optional[str] = None
    country: str
    region_continent: Optional[str] = None
    media: Optional[str] = None
    proto_unicast: bool = True
    proto_multicast: bool = False
    proto_ipv6: bool = True
    website: Optional[str] = None
    net_count: int = 0
    fac_count: int = 0
    created_date: Optional[str] = None
    updated_date: Optional[str] = None
    status: str = "ok"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: str = "PeeringDB API (CC BY-SA 4.0)"

class FacilityBase(BaseModel):
    id: int
    name: str
    org_name: Optional[str] = None
    city: Optional[str] = None
    country: str
    region_continent: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    address1: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    net_count: int = 0
    ix_count: int = 0
    diverse_serving_substations: Optional[bool] = None
    website: Optional[str] = None
    status: str = "ok"
    source: str = "PeeringDB API (CC BY-SA 4.0)"

class NetworkBase(BaseModel):
    id: int
    name: str
    aka: Optional[str] = None
    asn: int
    info_type: Optional[str] = None
    policy_general: Optional[str] = None
    website: Optional[str] = None
    netixlan_count: int = 0
    netfac_count: int = 0

class NetworkRelationshipBase(BaseModel):
    id: int
    net_id: int
    ix_id: int
    asn: int
    speed: int
    is_rs_peer: bool = False
    operational: bool = True
    status: str = "ok"

class DataSourceProvenanceSchema(BaseModel):
    id: str
    name: str
    url: str
    license: str
    download_date: str
    record_count: int
    geographic_coverage: str
    temporal_coverage: str
    known_limitations: str
    status: str = "active"

class CountryStatsSchema(BaseModel):
    country_code: str
    country_name: str
    region: str
    ixp_count: int
    facility_count: int
    landing_station_count: int
    cable_count: int
    connected_networks_count: int
    infrastructure_density_score: float

class GlobalOverviewStatsSchema(BaseModel):
    total_cables: int
    total_landing_stations: int
    total_ixps: int
    total_facilities: int
    total_networks: int
    total_interconnections: int
    countries_covered: int
    data_freshness_date: str

