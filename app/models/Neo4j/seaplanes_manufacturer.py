from .neo4j_models import get_neo4j_driver


def insert_seaplanes_manufacturers(manufacturers_data):
    driver = get_neo4j_driver()
    with driver.session() as session:
        for manufacturer in manufacturers_data:
            query = "CREATE (m:Manufacturer {name: $name})"
            session.run(query, name=manufacturer["name"])


def get_manufacturers():
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (m:Manufacturer) RETURN m"
        result = session.run(query)
        return [dict(record["m"]) for record in result]


def get_manufacturer(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (m:Manufacturer {name: $name}) RETURN m"
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["m"]) if record else None


def get_manufacturer_by_model(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (m:Manufacturer)<-[:MANUFACTURED_BY]-(sm:SeaplaneModel {name: $name}) RETURN m"
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["m"]) if record else None
