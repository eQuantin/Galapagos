from datetime import datetime

from models.Neo4j.ports import get_port
from models.Neo4j.seaplanes import get_seaplane
from models.Neo4j.seaplanes_models import get_model_by_seaplane
from utils.harvesine import haversine


def calculate_current_position(seaplane_name):
    seaplane = get_seaplane(seaplane_name)
    if not seaplane:
        return None

    departure_port_name = seaplane.get("flight_departure_port")
    destination_port_name = seaplane.get("flight_destination_port")
    departure_time_str = seaplane.get("flight_departure_time")

    if not all([departure_port_name, destination_port_name, departure_time_str]):
        return None

    departure_port = get_port(departure_port_name)
    destination_port = get_port(destination_port_name)

    if not departure_port or not destination_port:
        return None

    dep_lat = departure_port["latitude"]
    dep_lon = departure_port["longitude"]
    dest_lat = destination_port["latitude"]
    dest_lon = destination_port["longitude"]

    seaplane_model = get_model_by_seaplane(seaplane_name)
    if not seaplane_model:
        return None

    speed_kmh = seaplane_model.get("average_speed_kmh", 0)
    if speed_kmh <= 0:
        return None

    total_distance_km = haversine(dep_lat, dep_lon, dest_lat, dest_lon)

    # Parse departure time - assume ISO 8601 format, naive UTC
    if isinstance(departure_time_str, str):
        # Remove Z suffix if present (treat as UTC)
        departure_time_str = departure_time_str.rstrip("Z")
        departure_time = datetime.fromisoformat(departure_time_str)
    else:
        departure_time = departure_time_str

    # Ensure we have a valid datetime
    if not isinstance(departure_time, datetime):
        return None

    # Current time in UTC
    current_time = datetime.utcnow()
    elapsed_time = current_time - departure_time
    elapsed_hours = elapsed_time.total_seconds() / 3600

    # Calculate distance traveled
    distance_traveled_km = elapsed_hours * speed_kmh

    # Calculate progress (0 to 1)
    progress = min(distance_traveled_km / total_distance_km, 1.0)

    # Interpolate position along great circle route
    current_lat, current_lon = interpolate_great_circle(
        dep_lat, dep_lon, dest_lat, dest_lon, progress
    )

    # Calculate estimated arrival time
    total_travel_hours = total_distance_km / speed_kmh
    remaining_hours = total_travel_hours - elapsed_hours
    if remaining_hours < 0:
        remaining_hours = 0

    from datetime import timedelta

    estimated_arrival = current_time + timedelta(hours=remaining_hours)

    return {
        "latitude": round(current_lat, 6),
        "longitude": round(current_lon, 6),
        "progress_percent": round(progress * 100, 2),
        "distance_traveled_km": round(distance_traveled_km, 2),
        "distance_remaining_km": round(
            max(0, total_distance_km - distance_traveled_km), 2
        ),
        "estimated_arrival": estimated_arrival.isoformat(),
        "departure_port": departure_port_name,
        "destination_port": destination_port_name,
        "departure_time": departure_time.isoformat(),
    }


def interpolate_great_circle(lat1, lon1, lat2, lon2, fraction):
    import math

    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Convert to Cartesian coordinates
    x1 = math.cos(lat1_rad) * math.cos(lon1_rad)
    y1 = math.cos(lat1_rad) * math.sin(lon1_rad)
    z1 = math.sin(lat1_rad)

    x2 = math.cos(lat2_rad) * math.cos(lon2_rad)
    y2 = math.cos(lat2_rad) * math.sin(lon2_rad)
    z2 = math.sin(lat2_rad)

    # Calculate angular distance
    dot_product = x1 * x2 + y1 * y2 + z1 * z2
    # Clamp to avoid numerical errors
    dot_product = max(-1.0, min(1.0, dot_product))
    angular_distance = math.acos(dot_product)

    # Handle case where points are very close
    if angular_distance < 1e-10:
        return lat1, lon1

    # Spherical linear interpolation (slerp)
    sin_angular_distance = math.sin(angular_distance)
    a = math.sin((1 - fraction) * angular_distance) / sin_angular_distance
    b = math.sin(fraction * angular_distance) / sin_angular_distance

    # Interpolated Cartesian coordinates
    x = a * x1 + b * x2
    y = a * y1 + b * y2
    z = a * z1 + b * z2

    # Convert back to latitude/longitude
    lat_rad = math.asin(z)
    lon_rad = math.atan2(y, x)

    lat = math.degrees(lat_rad)
    lon = math.degrees(lon_rad)

    return lat, lon


def get_all_flying_seaplanes_positions():
    from models.Neo4j.seaplanes import get_seaplanes_by_status

    flying_seaplanes = get_seaplanes_by_status("flying")
    positions = []

    for seaplane in flying_seaplanes:
        name = seaplane.get("name")
        if name:
            position = calculate_current_position(name)
            if position:
                positions.append({"seaplane_name": name, **position})

    return positions


def estimate_arrival_time(seaplane_name):
    position = calculate_current_position(seaplane_name)
    if not position:
        return None

    return {
        "seaplane_name": seaplane_name,
        "estimated_arrival": position["estimated_arrival"],
        "distance_remaining_km": position["distance_remaining_km"],
        "progress_percent": position["progress_percent"],
        "destination_port": position["destination_port"],
    }


def check_if_arrived(seaplane_name, threshold_percent=99.0):
    position = calculate_current_position(seaplane_name)
    if not position:
        return False

    return position["progress_percent"] >= threshold_percent


def get_seaplane_flight_status(seaplane_name):
    from models.Neo4j.ports import get_port_by_seaplane
    from models.Neo4j.seaplanes_status import get_status_by_seaplane

    seaplane = get_seaplane(seaplane_name)
    if not seaplane:
        return None

    status_obj = get_status_by_seaplane(seaplane_name)
    status = status_obj.get("value") if status_obj else "unknown"

    result = {
        "seaplane_name": seaplane_name,
        "status": status,
        "is_flying": status == "flying",
        "position": None,
        "docked_at": None,
    }

    if status == "flying":
        result["position"] = calculate_current_position(seaplane_name)
    elif status == "docked":
        port = get_port_by_seaplane(seaplane_name)
        if port:
            result["docked_at"] = port.get("name")

    return result
