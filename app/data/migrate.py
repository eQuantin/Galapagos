# Neo4j migration
from data.clients import scientists_data
from data.islands import islands_data
from data.lockers import lockers_data
from data.ports import ports_data
from data.seaplanes.manufacturer import seaplanes_manufacturer_data
from data.seaplanes.models import seaplanes_models_data
from data.seaplanes.seaplanes import seaplanes_data
from data.seaplanes.status import seaplanes_status_data
from data.warehouse import warehouse_data
from models.Neo4j.clients import insert_clients
from models.Neo4j.islands import insert_islands
from models.Neo4j.lockers import insert_lockers
from models.Neo4j.neo4j_models import clean_database
from models.Neo4j.ports import create_port_distance_relationships, insert_ports
from models.Neo4j.seaplanes import insert_seaplanes
from models.Neo4j.seaplanes_manufacturer import insert_seaplanes_manufacturers
from models.Neo4j.seaplanes_models import insert_seaplanes_models
from models.Neo4j.seaplanes_status import insert_seaplanes_status
from models.Neo4j.warehouse import insert_warehouse
from models.Mongo.scientific_equipment import insert_scientific_equipment
from data.scientific_equipment import equipment_data


def migrate():
    clean_database()
    insert_islands(islands_data)
    insert_ports(ports_data)
    insert_seaplanes_manufacturers(seaplanes_manufacturer_data)
    insert_seaplanes_models(seaplanes_models_data)
    insert_seaplanes_status(seaplanes_status_data)
    insert_seaplanes(seaplanes_data)
    insert_lockers(lockers_data)
    insert_warehouse(warehouse_data)
    insert_clients(scientists_data)
    insert_scientific_equipment(equipment_data)
    create_port_distance_relationships()
