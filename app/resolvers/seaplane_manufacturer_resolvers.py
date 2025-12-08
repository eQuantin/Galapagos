from models.Neo4j.seaplanes_manufacturer import (
    get_manufacturer,
    get_manufacturers,
)
from models.Neo4j.seaplanes_models import get_models_by_manufacturer


def resolve_manufacturers(obj, info):
    return get_manufacturers()


def resolve_manufacturer(obj, info, name):
    return get_manufacturer(name)


def resolve_manufacturer_models(obj, info):
    manufacturer = obj.get("name")
    if manufacturer:
        return get_models_by_manufacturer(manufacturer)
    return None
