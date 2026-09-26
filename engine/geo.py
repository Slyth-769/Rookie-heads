"""
Geo-spatial calculations and Geo-Fencing for Disaster Alert Targeting
Provides:
1. Haversine distance formula (kilometers)
2. Circle radius containment check
3. Point-in-polygon ray-casting test
4. Pre-defined coastal disaster district boundaries and centroids
"""

import math

# Reference Coordinates for Disaster-Prone Districts (Centroids + Default Radius)
DISTRICT_CENTROIDS = {
    "Puri": {"lat": 19.8135, "lng": 85.8312, "radius_km": 35, "risk": "High Cyclone & Tsunami"},
    "Balasore": {"lat": 21.4934, "lng": 86.9135, "radius_km": 40, "risk": "Extreme Cyclone & Tidal Surge"},
    "Jagatsinghpur": {"lat": 20.2667, "lng": 86.1667, "radius_km": 30, "risk": "Super-Cyclone Zone (Paradeep)"},
    "Kendrapara": {"lat": 20.5034, "lng": 86.4227, "radius_km": 35, "risk": "Flood & Storm Surge"},
    "Ganjam": {"lat": 19.3800, "lng": 84.9900, "radius_km": 45, "risk": "Severe Cyclone (Phailin/Titli)"},
    "Bhadrak": {"lat": 21.0574, "lng": 86.4959, "radius_km": 30, "risk": "Flood Inundation & Cyclone"},
    "Cuttack": {"lat": 20.4625, "lng": 85.8828, "radius_km": 25, "risk": "Mahanadi River Basin Flooding"},
    "Bhubaneswar": {"lat": 20.2961, "lng": 85.8245, "radius_km": 25, "risk": "Urban Flash Flood & Heatwave"}
}

def haversine_distance_km(lat1, lon1, lat2, lon2):
    """
    Computes great-circle distance between two GPS coordinates using Haversine formula.
    """
    R = 6371.0  # Earth's mean radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def is_point_in_radius(point_lat, point_lng, center_lat, center_lng, radius_km):
    """Checks if point lies within circle radius in kilometers"""
    dist = haversine_distance_km(point_lat, point_lng, center_lat, center_lng)
    return dist <= radius_km, round(dist, 2)

def is_point_in_polygon(point_lat, point_lng, polygon_coords):
    """
    Ray-casting algorithm for point-in-polygon.
    polygon_coords: list of dicts [{"lat": ..., "lng": ...}] or tuples [(lat, lng), ...]
    """
    if not polygon_coords or len(polygon_coords) < 3:
        return False
        
    num_vertices = len(polygon_coords)
    inside = False
    
    p1x = polygon_coords[0]["lat"] if isinstance(polygon_coords[0], dict) else polygon_coords[0][0]
    p1y = polygon_coords[0]["lng"] if isinstance(polygon_coords[0], dict) else polygon_coords[0][1]
    
    for i in range(num_vertices + 1):
        idx = i % num_vertices
        p2x = polygon_coords[idx]["lat"] if isinstance(polygon_coords[idx], dict) else polygon_coords[idx][0]
        p2y = polygon_coords[idx]["lng"] if isinstance(polygon_coords[idx], dict) else polygon_coords[idx][1]
        
        if point_lng > min(p1y, p2y):
            if point_lng <= max(p1y, p2y):
                if point_lat <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (point_lng - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or point_lat <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
        
    return inside
