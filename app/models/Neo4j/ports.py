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
        query = """
            MATCH (p:Port)-[:LOCATED_ON]->(i:Island {name: $island_name})
            RETURN p
        """
        result = session.run(query, island_name=island_name)
        return [dict(record["p"]) for record in result]


def get_port_by_locker(locker_id):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
            MATCH (l:Locker {id: $locker_id})-[:LOCATED_AT]->(p:Port)
            RETURN p
        """
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
