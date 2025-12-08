from .neo4j_models import get_neo4j_driver


def insert_seaplanes_models(models_data):
    driver = get_neo4j_driver()
    with driver.session() as session:
        for model in models_data:
            query = """
                MATCH (m:Manufacturer {name: $manufacturer})
                CREATE (sm:SeaplaneModel {
                    name: $name,
                    crate_capacity: $crate_capacity,
                    fuel_consumption_L_per_km: $fuel_consumption_L_per_km,
                    fuel_capacity_L: $fuel_capacity_L,
                    cost_per_km_USD: $cost_per_km_USD,
                    average_speed_kmh: $average_speed_kmh
                })
                CREATE (sm)-[:MANUFACTURED_BY]->(m)
            """
            session.run(
                query,
                name=model["name"],
                manufacturer=model["manufacturer"],
                crate_capacity=model["crate_capacity"],
                fuel_consumption_L_per_km=model["fuel_consumption_L_per_km"],
                fuel_capacity_L=model["fuel_capacity_L"],
                cost_per_km_USD=model["cost_per_km_USD"],
                average_speed_kmh=model["average_speed_kmh"],
            )


def get_all_models():
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = (
            "MATCH (sm:SeaplaneModel)-[:MANUFACTURED_BY]->(m:Manufacturer) RETURN sm, m"
        )
        result = session.run(query)
        return [dict(record["sm"]) for record in result]


def get_model(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (sm:SeaplaneModel {name: $name})-[:MANUFACTURED_BY]->(m:Manufacturer) RETURN sm, m"
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["sm"]) if record else None


def get_models_by_manufacturer(manufacturer_name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (sm:SeaplaneModel)-[:MANUFACTURED_BY]->(m:Manufacturer {name: $manufacturer_name}) RETURN sm"
        result = session.run(query, manufacturer_name=manufacturer_name)
        return [dict(record["sm"]) for record in result]


def get_model_by_seaplane(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (s:Seaplane {name: $name})-[:MODEL_TYPE]->(sm:SeaplaneModel) RETURN sm"
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["sm"]) if record else None
