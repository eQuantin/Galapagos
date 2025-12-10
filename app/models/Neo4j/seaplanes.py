from .neo4j_models import get_neo4j_driver


def insert_seaplanes(seaplanes_data):
    driver = get_neo4j_driver()
    with driver.session() as session:
        for seaplane in seaplanes_data:
            query = """
                MATCH (sm:SeaplaneModel {name: $model_name})
                MATCH (p:Port {name: $location})
                MATCH (st:SeaplaneStatus {value: $status_value})
                CREATE (s:Seaplane {
                    name: $name,
                    fuel: $fuel,
                    crates: $crates,
                    flight_departure_port: null,
                    flight_destination_port: null,
                    flight_departure_time: null
                })
                CREATE (s)-[:MODEL_TYPE]->(sm)
                CREATE (s)-[:DOCKED_AT]->(p)
                CREATE (s)-[:HAS_STATUS]->(st)
            """
            session.run(
                query,
                model_name=seaplane["model"],
                name=seaplane["name"],
                location=seaplane["location"],
                status_value=seaplane["status"],
                fuel=seaplane["fuel"],
                crates=seaplane["crates"],
            )


def get_all_seaplanes():
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (s:Seaplane) RETURN s"
        result = session.run(query)
        return [dict(record["s"]) for record in result]


def get_seaplane(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (s:Seaplane {name: $name}) RETURN s"
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["s"]) if record else None


def get_seaplanes_by_model(model_name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (s:Seaplane)-[:MODEL_TYPE]->(sm:SeaplaneModel {name: $model_name}) RETURN s"
        result = session.run(query, model_name=model_name)
        return [dict(record["s"]) for record in result]


def get_seaplanes_by_port(port_name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (s:Seaplane)-[:DOCKED_AT]->(p:Port {name: $port_name}) RETURN s"
        result = session.run(query, port_name=port_name)
        return [dict(record["s"]) for record in result]


def get_seaplanes_by_status(status_value):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (s:Seaplane)-[:HAS_STATUS]->(st:SeaplaneStatus {value: $status_value}) RETURN s"
        result = session.run(query, status_value=status_value)
        return [dict(record["s"]) for record in result]


def update_seaplane_fuel(name, fuel_amount):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
            MATCH (s:Seaplane {name: $name})
            SET s.fuel = $fuel_amount
            RETURN s
        """
        result = session.run(query, name=name, fuel_amount=fuel_amount)
        record = result.single()
        return dict(record["s"]) if record else None


def update_seaplane_crates(name, crates_count):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
            MATCH (s:Seaplane {name: $name})
            SET s.crates = $crates_count
            RETURN s
        """
        result = session.run(query, name=name, crates_count=crates_count)
        record = result.single()
        return dict(record["s"]) if record else None


def update_seaplane_status(name, new_status):
    driver = get_neo4j_driver()
    with driver.session() as session:
        if new_status == "flying":
            query = """
                MATCH (s:Seaplane {name: $name})-[r:HAS_STATUS]->(:SeaplaneStatus)
                MATCH (new_st:SeaplaneStatus {value: $new_status})
                DELETE r
                CREATE (s)-[:HAS_STATUS]->(new_st)
                WITH s
                OPTIONAL MATCH (s)-[dock:DOCKED_AT]->(:Port)
                DELETE dock
                RETURN s
            """
        elif new_status == "docked":
            query = """
                MATCH (s:Seaplane {name: $name})-[r:HAS_STATUS]->(:SeaplaneStatus)
                MATCH (new_st:SeaplaneStatus {value: $new_status})
                DELETE r
                CREATE (s)-[:HAS_STATUS]->(new_st)
                SET s.flight_departure_port = null,
                    s.flight_destination_port = null,
                    s.flight_departure_time = null
                RETURN s
            """
        else:
            query = """
                MATCH (s:Seaplane {name: $name})-[r:HAS_STATUS]->(:SeaplaneStatus)
                MATCH (new_st:SeaplaneStatus {value: $new_status})
                DELETE r
                CREATE (s)-[:HAS_STATUS]->(new_st)
                RETURN s
            """
        result = session.run(query, name=name, new_status=new_status)
        record = result.single()
        return dict(record["s"]) if record else None


def update_seaplane_location(name, new_port):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
            MATCH (s:Seaplane {name: $name})
            MATCH (new_p:Port {name: $new_port})
            OPTIONAL MATCH (s)-[r:DOCKED_AT]->(:Port)
            DELETE r
            CREATE (s)-[:DOCKED_AT]->(new_p)
            RETURN s
        """
        result = session.run(query, name=name, new_port=new_port)
        record = result.single()
        return dict(record["s"]) if record else None


def get_available_seaplanes(port_name=None):
    driver = get_neo4j_driver()
    with driver.session() as session:
        if port_name:
            query = """
                MATCH (s:Seaplane)-[:HAS_STATUS]->(st:SeaplaneStatus {value: "docked"})
                MATCH (s)-[:DOCKED_AT]->(p:Port {name: $port_name})
                RETURN s
            """
            result = session.run(query, port_name=port_name)
        else:
            query = """
                MATCH (s:Seaplane)-[:HAS_STATUS]->(st:SeaplaneStatus {value: "docked"})
                RETURN s
            """
            result = session.run(query)
        return [dict(record["s"]) for record in result]


def remove_seaplane_location(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
            MATCH (s:Seaplane {name: $name})-[r:DOCKED_AT]->(:Port)
            DELETE r
            RETURN s
        """
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["s"]) if record else None


def start_seaplane_flight(name, departure_port, destination_port, departure_time):
    driver = get_neo4j_driver()
    with driver.session() as session:
        # Convert datetime to ISO string if needed
        if hasattr(departure_time, "isoformat"):
            departure_time = departure_time.isoformat()

        query = """
            MATCH (s:Seaplane {name: $name})
            SET s.flight_departure_port = $departure_port,
                s.flight_destination_port = $destination_port,
                s.flight_departure_time = $departure_time
            RETURN s
        """
        result = session.run(
            query,
            name=name,
            departure_port=departure_port,
            destination_port=destination_port,
            departure_time=departure_time,
        )
        record = result.single()
        return dict(record["s"]) if record else None


def clear_seaplane_flight_info(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = """
            MATCH (s:Seaplane {name: $name})
            SET s.flight_departure_port = null,
                s.flight_destination_port = null,
                s.flight_departure_time = null
            RETURN s
        """
        result = session.run(query, name=name)
        record = result.single()
        return dict(record["s"]) if record else None


def delete_seaplane(name):
    driver = get_neo4j_driver()
    with driver.session() as session:
        query = "MATCH (s:Seaplane {name: $name}) DETACH DELETE s"
        session.run(query, name=name)
        return True
