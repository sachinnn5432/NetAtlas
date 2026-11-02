"""REST API Route Definitions for NetAtlas Global Intelligence Engine.

Provides endpoints for infrastructure catalogs, geospatial GeoJSON feeds,
NetworkX graph analytics, country aggregations, data quality, and provenance.
"""

from typing import Dict, Any, Optional
import json
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app, Response
from backend.services.catalog_service import CatalogService
from backend.services.search_service import SearchService
from backend.analytics.country_stats import CountryAnalytics
from backend.analytics.regional_aggregation import RegionalAnalytics
from backend.analytics.infrastructure_density import DataStoryteller
from backend.network_analysis.topology_analyzer import TopologyAnalyzer
from backend.network_analysis.degree_metrics import DegreeMetricsCalculator
from backend.ingestion.data_source_registry import get_all_provenance
from backend.preprocessing.quality_reporter import QualityReporter
from backend.config.settings import GEOJSON_DATA_DIR, REPORTING_DATA_DIR
from backend.models.database import SessionLocal
from backend.models.db_models import (
    CableModel, LandingStationModel, IXPModel, FacilityModel, NetworkModel, NetworkIXRelationshipModel
)

api_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

@api_bp.route("/overview", methods=["GET"])
def get_global_overview():
    """Returns high-level verified infrastructure counts and system health."""
    session = SessionLocal()
    try:
        cable_count = session.query(CableModel).count()
        lp_count = session.query(LandingStationModel).count()
        ixp_count = session.query(IXPModel).count()
        fac_count = session.query(FacilityModel).count()
        net_count = session.query(NetworkModel).count()
        rel_count = session.query(NetworkIXRelationshipModel).count()

        return jsonify({
            "status": "success",
            "data": {
                "total_submarine_cables": cable_count,
                "total_landing_stations": lp_count,
                "total_ixps": ixp_count,
                "total_facilities": fac_count,
                "total_networks": net_count,
                "total_interconnections": rel_count,
                "countries_tracked": 60,
                "platform": "NetAtlas Infrastructure Intelligence",
                "version": "1.0.0"
            }
        })
    finally:
        session.close()

@api_bp.route("/cables", methods=["GET"])
def list_cables():
    """Queries submarine cables with search and filters."""
    search = request.args.get("search")
    rfs_year = request.args.get("rfs_year", type=int)
    is_planned_raw = request.args.get("is_planned")
    is_planned = None
    if is_planned_raw is not None:
        is_planned = is_planned_raw.lower() in ("true", "1")

    limit = min(request.args.get("limit", default=100, type=int), 1000)
    offset = max(request.args.get("offset", default=0, type=int), 0)

    results = CatalogService.get_cables(
        search=search, rfs_year=rfs_year, is_planned=is_planned, limit=limit, offset=offset
    )
    return jsonify({"status": "success", "count": len(results), "data": results})

@api_bp.route("/cables/<cable_id>", methods=["GET"])
def get_cable_detail(cable_id: str):
    """Retrieves single cable details including geometry."""
    cable = CatalogService.get_cable_detail(cable_id)
    if not cable:
        return jsonify({"status": "error", "message": "Cable not found"}), 404
    return jsonify({"status": "success", "data": cable})

@api_bp.route("/landing-stations", methods=["GET"])
def list_landing_stations():
    """Queries cable landing points/stations."""
    country = request.args.get("country")
    search = request.args.get("search")
    limit = min(request.args.get("limit", default=200, type=int), 2000)
    offset = max(request.args.get("offset", default=0, type=int), 0)

    results = CatalogService.get_landing_stations(
        country=country, search=search, limit=limit, offset=offset
    )
    return jsonify({"status": "success", "count": len(results), "data": results})

@api_bp.route("/ixps", methods=["GET"])
def list_ixps():
    """Queries Internet Exchange Points."""
    country = request.args.get("country")
    city = request.args.get("city")
    search = request.args.get("search")
    limit = min(request.args.get("limit", default=100, type=int), 1500)
    offset = max(request.args.get("offset", default=0, type=int), 0)

    results = CatalogService.get_ixps(
        country=country, city=city, search=search, limit=limit, offset=offset
    )
    return jsonify({"status": "success", "count": len(results), "data": results})

@api_bp.route("/facilities", methods=["GET"])
def list_facilities():
    """Queries interconnection facilities and colocation centres."""
    country = request.args.get("country")
    city = request.args.get("city")
    bbox = request.args.get("bbox")
    search = request.args.get("search")
    limit = min(request.args.get("limit", default=100, type=int), 3000)
    offset = max(request.args.get("offset", default=0, type=int), 0)

    results = CatalogService.get_facilities(
        country=country, city=city, bbox=bbox, search=search, limit=limit, offset=offset
    )
    return jsonify({"status": "success", "count": len(results), "data": results})

@api_bp.route("/search", methods=["GET"])
def search_global():
    """Unified search across all infrastructure categories."""
    q = request.args.get("q", "")
    results = SearchService.global_search(q)
    return jsonify({"status": "success", "data": results})

@api_bp.route("/analytics/countries", methods=["GET"])
def get_country_analytics():
    """Returns country infrastructure summaries and composite density scores."""
    summaries = CountryAnalytics.get_all_country_summaries()
    return jsonify({"status": "success", "count": len(summaries), "data": summaries})

@api_bp.route("/analytics/regions", methods=["GET"])
def get_regional_analytics():
    """Returns macro-regional comparisons."""
    regions = RegionalAnalytics.get_regional_breakdown()
    return jsonify({"status": "success", "data": regions})

@api_bp.route("/analytics/network-topology", methods=["GET"])
def get_topology_analytics():
    """Returns NetworkX topological metrics, degree hubs, and component analysis."""
    metrics = TopologyAnalyzer.analyze_global_peering_topology()
    degrees = DegreeMetricsCalculator.calculate_degree_distributions()
    return jsonify({
        "status": "success",
        "topology": metrics,
        "degree_distributions": degrees
    })

@api_bp.route("/analytics/stories", methods=["GET"])
def get_stories():
    """Returns structured data storytelling narratives."""
    stories = DataStoryteller.generate_analytical_stories()
    return jsonify({"status": "success", "data": stories})

@api_bp.route("/provenance", methods=["GET"])
def get_provenance():
    """Returns data source provenance, licensing, and limitations."""
    records = get_all_provenance()
    return jsonify({"status": "success", "data": records})

@api_bp.route("/data-quality", methods=["GET"])
def get_data_quality():
    """Returns latest automated data quality audit report."""
    report_file = REPORTING_DATA_DIR / "data_quality_report.json"
    if report_file.exists():
        with open(report_file, "r", encoding="utf-8") as f:
            audit = json.load(f)
            return jsonify({"status": "success", "data": audit})
    audit = QualityReporter.generate_full_audit()
    return jsonify({"status": "success", "data": audit})

@api_bp.route("/geojson/<layer_name>", methods=["GET"])
def get_geojson_layer(layer_name: str):
    """Streams verified GeoJSON layers for Leaflet mapping."""
    allowed_layers = {
        "cables": GEOJSON_DATA_DIR / "submarine_cables.geojson",
        "landing-stations": GEOJSON_DATA_DIR / "landing_stations.geojson"
    }

    if layer_name not in allowed_layers:
        return jsonify({"status": "error", "message": f"Invalid layer '{layer_name}'"}), 400

    path = allowed_layers[layer_name]
    if not path.exists():
        return jsonify({"status": "error", "message": f"Layer '{layer_name}' not generated yet"}), 404

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return Response(content, mimetype="application/geo+json")

