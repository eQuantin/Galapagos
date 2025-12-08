from .neo4j_models import get_neo4j_driver


def insert_warehouse(warehouse_data):
    driver = get_neo4j_driver()
    with driver.session() as session:
        for warehouse in warehouse_data:
            query = """
                MATCH (p:Port {name: $port_name})
                CREATE (w:Warehouse {name: $name, id: $id})
                CREATE (w)-[:LOCATED_AT]->(p)
                RETURN w
            """
            session.run(
                query,
                port_name=warehouse["port"],
                name=warehouse["name"],
                id=warehouse["id"],
            )


def get_all_warehouses():
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (w:Warehouse) RETURN w"
        result = session.run(query)
        return [dict(record["w"]) for record in result]


def get_warehouse(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (w:Warehouse {name: $name}) RETURN w"
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["w"]) if record else None


def get_warehouse_by_id(id):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (w:Warehouse {id: $id}) RETURN w"
        result = session.run(query, id=id)
        record = result.single()
        return dict(record["w"]) if record else None


def get_warehouse_by_port(port_name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
            MATCH (w:Warehouse)-[:LOCATED_AT]->(p:Port {name: $port_name})
            RETURN w
        """
        result = session.run(query, port_name=port_name)
        record = result.single()
        return dict(record["w"]) if record else None
