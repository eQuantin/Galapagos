from .neo4j_models import get_neo4j_driver


def insert_islands(islands_data):
    driver = get_neo4j_driver()
    with driver.session() as session:
        for island in islands_data:
            query = """
                CREATE (i:Island {name: $name})
            """
            session.run(query, name=island["name"])


def get_islands():
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (i:Island) RETURN i"
        result = session.run(query)
        return [dict(record["i"]) for record in result]


def get_island(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (i:Island {name: $name}) RETURN i"
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["i"]) if record else None


def get_island_by_port(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (i:Island)<-[:LOCATED_ON]-(p:Port {name: $name}) RETURN i"
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["i"]) if record else None
