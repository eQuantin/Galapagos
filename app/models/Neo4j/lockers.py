from .neo4j_models import get_neo4j_driver


def insert_lockers(locker_data):
    driver = get_neo4j_driver()
    with driver.session() as session:
        for locker in locker_data:
            query = """
                MATCH (p:Port {name: $port_name})
                CREATE (l:Locker {
                    is_empty: $is_empty,
                    capacity_type: $capacity_type,
                    capacity_max: $capacity_max,
                    remaining_capacity: $remaining_capacity,
                    id: $id
                })
                CREATE (l)-[:LOCATED_AT]->(p)
                RETURN l
            """

            session.run(
                query,
                port_name=locker["port_name"],
                capacity=locker["capacity_max"],
                id=locker["id"],
                remaining_capacity=locker["remaining_capacity"],
                capacity_type=locker["capacity_type"],
            )


def get_all_lockers():
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (l:Locker) RETURN l"
        result = session.run(query)
        return [dict(record["l"]) for record in result]


def get_locker_by_port(port_name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (l:Locker)-[:LOCATED_AT]->(p:Port {name: $port_name}) RETURN l"
        result = session.run(query, port_name=port_name)
        record = result.single()
        return dict(record["l"]) if record else None


def get_locker(id):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (l:Locker {id: $id}) RETURN l"
        result = session.run(query, id=id)
        record = result.single()
        return dict(record["l"]) if record else None


def get_locker_for_client(client_name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = (
            "MATCH (c:Client {name: $client_name})-[:ASSIGNED_TO]->(l:Locker) RETURN l"
        )
        result = session.run(query, client_name=client_name)
        record = result.single()
        return dict(record["l"]) if record else None


def update_locker_capacity(port_name, new_remaining_capacity):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
            MATCH (l:Locker)-[:LOCATED_AT]->(p:Port {name: $port_name})
            SET l.remaining_capacity = $new_remaining_capacity
            RETURN l
        """
        result = session.run(
            query,
            port_name=port_name,
            new_remaining_capacity=new_remaining_capacity,
        )
        record = result.single()
        return dict(record["l"]) if record else None


def get_lockers_with_available_capacity(min_capacity=1):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
            MATCH (l:Locker)-[:LOCATED_AT]->(p:Port)
            WHERE l.remaining_capacity >= $min_capacity
            RETURN l, p
            ORDER BY l.remaining_capacity DESC
        """
        result = session.run(query, min_capacity=min_capacity)
        lockers = []
        for record in result:
            locker_data = dict(record["l"])
            locker_data["port"] = dict(record["p"])
            lockers.append(locker_data)
        return lockers
