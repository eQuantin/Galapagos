from utils.harvesine import haversine

from .neo4j_models import get_neo4j_driver


def insert_ports(ports_data):
    driver = get_neo4j_driver()
    with driver.session() as session:
        for port in ports_data:
            query = """
                MATCH (i:Island {name: $island_name})
                CREATE (p:Port {name: $name, latitude: $latitude, longitude: $longitude})
                CREATE (p)-[:LOCATED_ON]->(i)
            """
            session.run(
                query,
                name=port["name"],
                latitude=port["latitude"],
                longitude=port["longitude"],
                island_name=port["island"],
            )


def get_all_ports():
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (p:Port) RETURN p"
        result = session.run(query)
        return [dict(record["p"]) for record in result]


def get_port(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (p:Port {name: $name}) RETURN p"
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["p"]) if record else None


def get_ports_by_island(island_name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (p:Port)-[:LOCATED_ON]->(i:Island {name: $island_name}) RETURN p"
        result = session.run(query, island_name=island_name)
        return [dict(record["p"]) for record in result]


def get_port_by_locker(locker_id):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (l:Locker {id: $locker_id})-[:LOCATED_AT]->(p:Port) RETURN p"
        result = session.run(query, locker_id=locker_id)
        record = result.single()
        return dict(record["p"]) if record else None


def get_port_by_warehouse(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (w:Warehouse {name: $name})-[:LOCATED_AT]->(p:Port) RETURN p"
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["p"]) if record else None


def get_port_by_seaplane(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (s:Seaplane {name: $name})-[:DOCKED_AT]->(p:Port) RETURN p"
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["p"]) if record else None


def create_port_distance_relationships():
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (p:Port) RETURN p"
        result = session.run(query)
        ports = [dict(record["p"]) for record in result]

        for i, port1 in enumerate(ports):
            for port2 in ports[i + 1 :]:
                distance = haversine(
                    port1["latitude"],
                    port1["longitude"],
                    port2["latitude"],
                    port2["longitude"],
                )

                query = """
                    MATCH (p1:Port {name: $name1})
                    MATCH (p2:Port {name: $name2})
                    MERGE (p1)-[:DISTANCE_TO {distance_km: $distance}]->(p2)
                    MERGE (p2)-[:DISTANCE_TO {distance_km: $distance}]->(p1)
                """
                session.run(
                    query,
                    name1=port1["name"],
                    name2=port2["name"],
                    distance=round(distance, 2),
                )
        return


def get_nearby_ports(port_name, limit=None):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
            MATCH (p1:Port {name: $port_name})-[d:DISTANCE_TO]->(p2:Port)
        """

        conditions = []
        params = {"port_name": port_name}

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " RETURN p2, d.distance_km as distance ORDER BY distance ASC"

        if limit is not None:
            query += " LIMIT $limit"
            params["limit"] = limit

        result = session.run(query, **params)
        return [
            {"port": dict(record["p2"]), "distance_km": record["distance"]}
            for record in result
        ]


def get_distance_between_ports(port1_name, port2_name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
            MATCH (p1:Port {name: $port1})-[d:DISTANCE_TO]->(p2:Port {name: $port2})
            RETURN d.distance_km as distance
        """
        result = session.run(query, port1=port1_name, port2=port2_name)
        record = result.single()
        return record["distance"] if record else None


def get_shortest_path_between_ports(start_port_name, end_port_name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
            MATCH (start:Port {name: $start_port}), (end:Port {name: $end_port})
            CALL apoc.algo.dijkstra(start, end, 'DISTANCE_TO', 'distance_km')
            YIELD path, weight
            RETURN
                [node in nodes(path) | node.name] as ports,
                weight as total_distance_km,
                length(path) as num_stops
        """
        result = session.run(query, start_port=start_port_name, end_port=end_port_name)
        record = result.single()

        if record:
            return {
                "ports": record["ports"],
                "total_distance_km": round(record["total_distance_km"], 2),
                "num_stops": record["num_stops"],
            }
        return None
