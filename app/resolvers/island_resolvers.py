from models.Neo4j.islands import get_island, get_islands
from models.Neo4j.ports import get_ports_by_island


def resolve_islands(obj, info):
    return get_islands()


def resolve_island(obj, info, name):
    return get_island(name)


def resolve_island_ports(obj, info):
    island = obj.get("name")
    if island:
        return get_ports_by_island(island)
    return []
