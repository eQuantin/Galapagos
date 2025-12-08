from models.Neo4j.ports import get_port_by_warehouse
from models.Neo4j.warehouse import get_all_warehouses, get_warehouse


def resolve_warehouses(obj, info):
    return get_all_warehouses()


def resolve_warehouse(obj, info, name):
    return get_warehouse(name)


def resolve_warehouse_port(obj, info):
    warehouse = obj.get("name")
    if warehouse:
        return get_port_by_warehouse(warehouse)
    return None
