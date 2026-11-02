"""SQLAlchemy ORM models for NetAtlas.

Defines schemas for cables, landing stations, IXPs, facilities, networks,
interconnection relationships, provenance tracking, and geographic reference data.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class CableModel(Base):
    """Submarine fiber-optic cable model."""
    __tablename__ = "cables"

    id = Column(String(128), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    rfs_year = Column(Integer, nullable=True, index=True)
    length_km = Column(Float, nullable=True)
    owners = Column(Text, nullable=True)
    suppliers = Column(Text, nullable=True)
    is_planned = Column(Boolean, default=False, index=True)
    url = Column(String(512), nullable=True)
    landing_points_count = Column(Integer, default=0)
    countries_connected = Column(Text, nullable=True)  # JSON list
    geometry_geojson = Column(Text, nullable=True)     # MultiLineString GeoJSON
    source = Column(String(128), default="TeleGeography / Public Submarine Cable API")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_cable_rfs", "rfs_year"),
        Index("ix_cable_planned", "is_planned"),
    )

class LandingStationModel(Base):
    """Submarine cable landing point / station model."""
    __tablename__ = "landing_stations"

    id = Column(String(128), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    country = Column(String(128), nullable=False, index=True)
    country_code = Column(String(8), nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_tbd = Column(Boolean, default=False)
    cable_count = Column(Integer, default=1)
    connected_cables = Column(Text, nullable=True)  # JSON list of cable IDs
    source = Column(String(128), default="TeleGeography / Public Submarine Cable API")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_landing_country", "country"),
        Index("ix_landing_coords", "latitude", "longitude"),
    )

class IXPModel(Base):
    """Internet Exchange Point (IXP) model from PeeringDB."""
    __tablename__ = "ixps"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    name_long = Column(String(512), nullable=True)
    city = Column(String(128), nullable=True, index=True)
    country = Column(String(8), nullable=False, index=True)
    region_continent = Column(String(32), nullable=True, index=True)
    media = Column(String(64), nullable=True)
    proto_unicast = Column(Boolean, default=True)
    proto_multicast = Column(Boolean, default=False)
    proto_ipv6 = Column(Boolean, default=True)
    website = Column(String(512), nullable=True)
    net_count = Column(Integer, default=0, index=True)
    fac_count = Column(Integer, default=0)
    created_date = Column(String(64), nullable=True)
    updated_date = Column(String(64), nullable=True)
    status = Column(String(32), default="ok")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    source = Column(String(128), default="PeeringDB API (CC BY-SA 4.0)")

    __table_args__ = (
        Index("ix_ixp_country_city", "country", "city"),
    )

class FacilityModel(Base):
    """Data Centre and Colocation Interconnection Facility model from PeeringDB."""
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    org_name = Column(String(255), nullable=True)
    city = Column(String(128), nullable=True, index=True)
    country = Column(String(8), nullable=False, index=True)
    region_continent = Column(String(32), nullable=True, index=True)
    state = Column(String(64), nullable=True)
    zipcode = Column(String(32), nullable=True)
    address1 = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    net_count = Column(Integer, default=0, index=True)
    ix_count = Column(Integer, default=0)
    diverse_serving_substations = Column(Boolean, nullable=True)
    website = Column(String(512), nullable=True)
    status = Column(String(32), default="ok")
    source = Column(String(128), default="PeeringDB API (CC BY-SA 4.0)")

    __table_args__ = (
        Index("ix_facility_geo", "latitude", "longitude"),
        Index("ix_facility_country", "country"),
    )

class NetworkModel(Base):
    """Network Operator / Autonomous System model from PeeringDB."""
    __tablename__ = "networks"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    aka = Column(String(255), nullable=True)
    asn = Column(Integer, nullable=False, index=True)
    info_type = Column(String(64), nullable=True)
    policy_general = Column(String(64), nullable=True)
    website = Column(String(512), nullable=True)
    netixlan_count = Column(Integer, default=0)
    netfac_count = Column(Integer, default=0)
    source = Column(String(128), default="PeeringDB API (CC BY-SA 4.0)")

class NetworkIXRelationshipModel(Base):
    """Network <-> IXP Interconnection relationship from PeeringDB."""
    __tablename__ = "network_ix_relationships"

    id = Column(Integer, primary_key=True)
    net_id = Column(Integer, ForeignKey("networks.id"), nullable=False, index=True)
    ix_id = Column(Integer, ForeignKey("ixps.id"), nullable=False, index=True)
    asn = Column(Integer, nullable=False, index=True)
    speed = Column(Integer, default=0)  # Speed in Mbps
    is_rs_peer = Column(Boolean, default=False)
    operational = Column(Boolean, default=True)
    status = Column(String(32), default="ok")

class NetworkFacilityRelationshipModel(Base):
    """Network <-> Facility Colocation relationship from PeeringDB."""
    __tablename__ = "network_facility_relationships"

    id = Column(Integer, primary_key=True)
    net_id = Column(Integer, ForeignKey("networks.id"), nullable=False, index=True)
    fac_id = Column(Integer, ForeignKey("facilities.id"), nullable=False, index=True)

class DataSourceProvenanceModel(Base):
    """Provenance and transparency tracking for each ingested dataset."""
    __tablename__ = "data_source_provenance"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    url = Column(String(512), nullable=False)
    license = Column(String(128), nullable=False)
    download_date = Column(String(64), nullable=False)
    record_count = Column(Integer, default=0)
    geographic_coverage = Column(String(255), nullable=False)
    temporal_coverage = Column(String(255), nullable=False)
    known_limitations = Column(Text, nullable=False)
    status = Column(String(32), default="active")

class CountryReferenceModel(Base):
    """Country and regional reference dataset for ISO mapping and normalization."""
    __tablename__ = "country_reference"

    iso2 = Column(String(8), primary_key=True)
    iso3 = Column(String(8), nullable=True, index=True)
    country_name = Column(String(128), nullable=False, index=True)
    region = Column(String(64), nullable=False, index=True)
    subregion = Column(String(64), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

