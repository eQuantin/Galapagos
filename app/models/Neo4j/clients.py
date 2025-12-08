from .neo4j_models import get_neo4j_driver


def insert_clients(clients_data):
    driver = get_neo4j_driver()
    with driver.session() as session:
        for client in clients_data:
            query = """
                MATCH (l:Locker)-[:LOCATED_AT]->(p:Port {name: $locker_port})
                CREATE (c:Client {
                    name: $name,
                    specialty: $specialty,
                    id: $id
                })
                CREATE (c)-[:ASSIGNED_TO]->(l)
                RETURN c
            """
            session.run(
                query,
                name=client["name"],
                specialty=client["specialty"],
                id=client["id"],
                locker_port=client["locker"],
            )


def get_all_clients():
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (c:Client) RETURN c ORDER BY c.name"
        result = session.run(query)
        return [dict(record["c"]) for record in result]


def get_client_by_name(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (c:Client {name: $name}) RETURN c"
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["c"]) if record else None


def get_client_by_id(id):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (c:Client {id: $id}) RETURN c"
        result = session.run(query, id=id)
        record = result.single()
        return dict(record["c"]) if record else None


def get_clients_by_locker(locker_id):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
            MATCH (c:Client)-[:ASSIGNED_TO]->(l:Locker {id: $locker_id})
            RETURN c
        """
        result = session.run(query, locker_id=locker_id)
        return [dict(record["c"]) for record in result]
