from models.Neo4j.ports import (
    get_distance_between_ports,
    get_shortest_path_between_ports,
)


def find_optimal_route(start_port, delivery_ports):
    if len(delivery_ports) == 1:
        path = get_shortest_path_between_ports(start_port, delivery_ports[0])
        if not path:
            return None

        route = path["ports"]
        segments = _calculate_segments(route)
        total_distance = path["total_distance_km"]

        if route[-1] != start_port:
            return_path = get_shortest_path_between_ports(route[-1], start_port)
            if return_path:
                route.extend(return_path["ports"][1:])
                segments.extend(_calculate_segments(return_path["ports"]))
                total_distance += return_path["total_distance_km"]

        return {
            "route": route,
            "total_distance_km": round(total_distance, 2),
            "segments": segments,
        }

    furthest_distance = 0
    furthest_port = None

    for port in delivery_ports:
        distance = get_distance_between_ports(start_port, port)
        if not distance:
            return None
        if distance > furthest_distance:
            furthest_distance = distance
            furthest_port = port

    if not furthest_port:
        return None

    path = get_shortest_path_between_ports(start_port, furthest_port)
    if not path:
        return None
    route = path["ports"]
    segments = _calculate_segments(route)
    total_distance = path["total_distance_km"]

    if route[-1] != start_port:
        return_path = get_shortest_path_between_ports(route[-1], start_port)
        if return_path:
            route.extend(return_path["ports"][1:])

    # Calculate total distance and segments for final route
    segments = _calculate_segments(route)
    total_distance = sum(seg["distance_km"] for seg in segments)

    return {
        "route": route,
        "total_distance_km": round(total_distance, 2),
        "segments": segments,
    }


def _calculate_segments(route):
    segments = []

    for i in range(len(route) - 1):
        distance = get_distance_between_ports(route[i], route[i + 1])
        if distance is not None:
            segments.append(
                {
                    "from": route[i],
                    "to": route[i + 1],
                    "distance_km": distance,
                }
            )

    return segments


def calculate_duration(total_distance_km, average_speed_kmh, num_stops):
    travel_time_hours = total_distance_km / average_speed_kmh
    stop_time_hours = num_stops * 1.0  # 1 hour per stop

    return round(travel_time_hours + stop_time_hours, 2)
