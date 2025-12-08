from models.Neo4j.seaplanes import get_seaplanes_by_model
from models.Neo4j.seaplanes_manufacturer import get_manufacturer_by_model
from models.Neo4j.seaplanes_models import (
    get_all_models,
    get_model,
)


def resolve_models(obj, info):
    return get_all_models()


def resolve_model(obj, info, name):
    return get_model(name)


def resolve_model_manufacturer(obj, info):
    model = obj.get("name")
    if model:
        return get_manufacturer_by_model(model)
    return None


def resolve_model_seaplanes(obj, info):
    model = obj.get("name")
    if model:
        return get_seaplanes_by_model(model)
    return None
