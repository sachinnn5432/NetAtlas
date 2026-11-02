"""Spatial Indexing and Bounding Box Operations for NetAtlas."""

import math
from typing import List, Dict, Any, Tuple, Optional

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the great-circle distance between two points on the Earth in kilometers."""
    r = 6371.0  # Earth's radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 2)

class SpatialBBox:
    """Represents a geographic bounding box [min_lon, min_lat, max_lon, max_lat]."""

    def __init__(self, min_lon: float, min_lat: float, max_lon: float, max_lat: float):
        self.min_lon = min_lon
        self.min_lat = min_lat
        self.max_lon = max_lon
        self.max_lat = max_lat

    def contains_point(self, lon: float, lat: float) -> bool:
        """Checks if a point (lon, lat) falls within this bounding box."""
        if lon is None or lat is None:
            return False
        return (self.min_lon <= lon <= self.max_lon) and (self.min_lat <= lat <= self.max_lat)

    @classmethod
    def from_string(cls, bbox_str: str) -> Optional["SpatialBBox"]:
        """Parses a comma-separated bounding box 'min_lon,min_lat,max_lon,max_lat'."""
        try:
            parts = [float(x.strip()) for x in bbox_str.split(",")]
            if len(parts) == 4:
                return cls(parts[0], parts[1], parts[2], parts[3])
        except Exception:
            pass
        return None

