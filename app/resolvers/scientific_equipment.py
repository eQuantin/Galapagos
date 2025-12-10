from models.Mongo.scientific_equipment import (
    get_all_equipment,
)

def resolve_scientific_equipments(obj, info):
    return get_all_equipment()
