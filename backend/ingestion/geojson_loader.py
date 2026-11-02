"""GeoJSON Loading, Geometry Validation, and Coordinate Normalization Module.

Validates WGS84 (EPSG:4326) geometries, verifies coordinate bounds,
and constructs GeoJSON FeatureCollections for map rendering.
"""

from typing import Dict, Any, List, Tuple, Optional
import json
from shapely.geometry import shape, mapping, MultiLineString, LineString, Point
from backend.config.logging_config import logger

def validate_wgs84_coordinates(lon: float, lat: float) -> bool:
    """Validates that coordinates conform to WGS84 bounds: [-180, 180] and [-90, 90]."""
    if lon is None or lat is None:
        return False
    if not isinstance(lon, (int, float)) or not isinstance(lat, (int, float)):
        return False
    return (-180.0 <= lon <= 180.0) and (-90.0 <= lat <= 90.0)

def validate_and_clean_geometry(geom_dict: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Validates a geometry dictionary using Shapely.

    Returns (cleaned_geom_dict, error_message).
    """
    if not geom_dict or not isinstance(geom_dict, dict):
        return None, "Empty or invalid geometry dictionary"

    try:
        geom_type = geom_dict.get("type")
        coords = geom_dict.get("coordinates")

        if not geom_type or coords is None:
            return None, "Missing geometry type or coordinates"

        s_geom = shape(geom_dict)

        # Check validity and attempt to make valid if self-intersecting
        if not s_geom.is_valid:
            logger.warning("Geometry invalid, attempting repair: %s", s_geom.geom_type)
            s_geom = s_geom.buffer(0)

        # Verify coordinate bounds
        bounds = s_geom.bounds  # (minx, miny, maxx, maxy)
        minx, miny, maxx, maxy = bounds
        if not (-180.0 <= minx <= 180.0 and -180.0 <= maxx <= 180.0 and
                -90.0 <= miny <= 90.0 and -90.0 <= maxy <= 90.0):
            return None, f"Geometry out of WGS84 bounds: {bounds}"

        return mapping(s_geom), None

    except Exception as exc:
        return None, f"Geometry validation exception: {str(exc)}"

def parse_geojson_features(geojson_content: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parses features from a GeoJSON object with validation."""
    if not isinstance(geojson_content, dict):
        raise ValueError("GeoJSON content must be a dictionary")

    features = geojson_content.get("features", [])
    valid_features = []
    discarded_count = 0

    for idx, feat in enumerate(features):
        props = feat.get("properties", {})
        geom = feat.get("geometry")

        cleaned_geom, err = validate_and_clean_geometry(geom)
        if cleaned_geom:
            valid_features.append({
                "type": "Feature",
                "id": feat.get("id", props.get("id", f"feat_{idx}")),
                "properties": props,
                "geometry": cleaned_geom
            })
        else:
            discarded_count += 1
            logger.debug("Feature %d discarded: %s", idx, err)

    logger.info("Parsed %d valid features (%d discarded).", len(valid_features), discarded_count)
    return valid_features

def build_feature_collection(features: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Wraps features into a valid GeoJSON FeatureCollection."""
    return {
        "type": "FeatureCollection",
        "features": features
    }

