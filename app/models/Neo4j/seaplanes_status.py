from .neo4j_models import get_neo4j_driver


def insert_seaplanes_status(status_data):
    driver = get_neo4j_driver()
    with driver.session() as session:
        for status in status_data:
            value = status["value"]

            query = "CREATE (st:SeaplaneStatus {value: $value})"
            session.run(query, value=value)


def get_all_status():
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (st:SeaplaneStatus) RETURN st"
        result = session.run(query)
        return [dict(record["st"]) for record in result]


def get_status(value):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (st:SeaplaneStatus {value: $value}) RETURN st"
        result = session.run(query, value=value)
        record = result.single()
        return dict(record["st"]) if record else None


def get_status_by_seaplane(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (s:Seaplane {name: $name})-[:HAS_STATUS]->(st:SeaplaneStatus) RETURN st"
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["st"]) if record else None
