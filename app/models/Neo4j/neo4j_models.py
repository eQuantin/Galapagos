import os

from neo4j import GraphDatabase


def get_neo4j_driver():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    if uri and user and password:
        return GraphDatabase.driver(uri, auth=(user, password))
    raise Exception("Invalid values")


def clean_database():
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (n) DETACH DELETE n"
        session.run(query)
        print("Cleaned Neo4j database")


def get_nodes(label):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (n:" + label + ") RETURN n"
        result = session.run(query)
        return [dict(record["n"]) for record in result]
