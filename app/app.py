from ariadne import (
    MutationType,
    ObjectType,
    QueryType,
    graphql_sync,
    load_schema_from_path,
    make_executable_schema,
)
from ariadne.explorer import ExplorerGraphiQL
from data.migrate import migrate
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from resolvers.client_resolvers import (
    resolve_client,
    resolve_client_locker,
    resolve_clients,
)
from resolvers.delivery_resolvers import (
    resolve_active_delivery_for_seaplane,
    resolve_create_delivery,
    resolve_deliveries,
    resolve_deliveries_by_seaplane,
    resolve_deliveries_by_status,
    resolve_delivery,
    resolve_delivery_orders,
    resolve_delivery_progress,
    resolve_delivery_progress_field,
    resolve_delivery_seaplane,
    resolve_start_delivery,
)
from resolvers.island_resolvers import (
    resolve_island,
    resolve_island_ports,
    resolve_islands,
)
from resolvers.locker_resolvers import (
    resolve_locker,
    resolve_locker_clients,
    resolve_locker_port,
    resolve_lockers,
)
from resolvers.maintenance_resolvers import (
    resolve_move_seaplane_into_maintenance,
    resolve_move_seaplane_out_of_maintenance,
    resolve_seaplanes_in_maintenance,
)
from resolvers.order_resolvers import (
    resolve_cancel_order,
    resolve_create_order,
    resolve_order,
    resolve_order_client,
    resolve_order_locker,
    resolve_order_warehouse,
    resolve_orders,
    resolve_orders_by_client,
    resolve_orders_by_status,
    resolve_orders_by_warehouse,
    resolve_update_order_status,
)
from resolvers.port_resolvers import (
    resolve_nearby_ports,
    resolve_port,
    resolve_port_island,
    resolve_port_locker,
    resolve_port_seaplanes,
    resolve_port_warehouse,
    resolve_ports,
    resolve_shortest_path_between_ports,
)
from resolvers.seaplane_manufacturer_resolvers import (
    resolve_manufacturer,
    resolve_manufacturer_models,
    resolve_manufacturers,
)
from resolvers.seaplane_model_resolvers import (
    resolve_model,
    resolve_model_manufacturer,
    resolve_model_seaplanes,
    resolve_models,
)
from resolvers.seaplane_resolvers import (
    resolve_seaplane,
    resolve_seaplane_current_position,
    resolve_seaplane_model,
    resolve_seaplane_port,
    resolve_seaplane_status,
    resolve_seaplanes,
)
from resolvers.seaplane_status_resolvers import (
    resolve_status,
    resolve_status_seaplane,
    resolve_statuses,
)
from resolvers.warehouse_resolvers import (
    resolve_warehouse,
    resolve_warehouse_port,
    resolve_warehouses,
)

load_dotenv()

# Load schema
type_defs = load_schema_from_path("schemas/schema.graphql")

# ============================================================================
# Query Type Resolvers
# ============================================================================
query_type = QueryType()

# Island queries
query_type.set_field("islands", resolve_islands)
query_type.set_field("island", resolve_island)

# Port queries
query_type.set_field("ports", resolve_ports)
query_type.set_field("port", resolve_port)
query_type.set_field("nearbyPorts", resolve_nearby_ports)
query_type.set_field("shortestPathBetweenPorts", resolve_shortest_path_between_ports)

# Client queries
query_type.set_field("clients", resolve_clients)
query_type.set_field("client", resolve_client)

# Locker queries
query_type.set_field("lockers", resolve_lockers)
query_type.set_field("locker", resolve_locker)

# Warehouse queries
query_type.set_field("warehouses", resolve_warehouses)
query_type.set_field("warehouse", resolve_warehouse)

# Seaplane queries
query_type.set_field("seaplanes", resolve_seaplanes)
query_type.set_field("seaplane", resolve_seaplane)
query_type.set_field("seaplanesInMaintenance", resolve_seaplanes_in_maintenance)

# Seaplane model queries
query_type.set_field("seaplaneModels", resolve_models)
query_type.set_field("seaplaneModel", resolve_model)

# Manufacturer queries
query_type.set_field("manufacturers", resolve_manufacturers)
query_type.set_field("manufacturer", resolve_manufacturer)

# Status queries
query_type.set_field("seaplaneStatuses", resolve_statuses)
query_type.set_field("seaplaneStatus", resolve_status)

# Order queries
query_type.set_field("orders", resolve_orders)
query_type.set_field("order", resolve_order)
query_type.set_field("ordersByClient", resolve_orders_by_client)
query_type.set_field("ordersByWarehouse", resolve_orders_by_warehouse)
query_type.set_field("ordersByStatus", resolve_orders_by_status)

# Delivery queries
query_type.set_field("deliveries", resolve_deliveries)
query_type.set_field("delivery", resolve_delivery)
query_type.set_field("deliveriesBySeaplane", resolve_deliveries_by_seaplane)
query_type.set_field("deliveriesByStatus", resolve_deliveries_by_status)
query_type.set_field("activeDeliveryForSeaplane", resolve_active_delivery_for_seaplane)
query_type.set_field("deliveryProgress", resolve_delivery_progress)

# ============================================================================
# Mutation Type Resolvers
# ============================================================================
mutation_type = MutationType()

# Seaplane maintenance mutations
mutation_type.set_field(
    "moveSeaplaneIntoMaintenance", resolve_move_seaplane_into_maintenance
)
mutation_type.set_field(
    "moveSeaplaneOutOfMaintenance", resolve_move_seaplane_out_of_maintenance
)

# Order mutations
mutation_type.set_field("createOrder", resolve_create_order)
mutation_type.set_field("updateOrderStatus", resolve_update_order_status)
mutation_type.set_field("cancelOrder", resolve_cancel_order)

# Delivery mutations
mutation_type.set_field("createDelivery", resolve_create_delivery)
mutation_type.set_field("startDelivery", resolve_start_delivery)

# ============================================================================
# Object Type Resolvers (Nested Fields)
# ============================================================================

# Island type
island_type = ObjectType("Island")
island_type.set_field("ports", resolve_island_ports)

# Port type
port_type = ObjectType("Port")
port_type.set_field("locker", resolve_port_locker)
port_type.set_field("warehouse", resolve_port_warehouse)
port_type.set_field("seaplanes", resolve_port_seaplanes)
port_type.set_field("island", resolve_port_island)

# Client type
client_type = ObjectType("Client")
client_type.set_field("locker", resolve_client_locker)

# Locker type
locker_type = ObjectType("Locker")
locker_type.set_field("clients", resolve_locker_clients)
locker_type.set_field("port", resolve_locker_port)

# Warehouse type
warehouse_type = ObjectType("Warehouse")
warehouse_type.set_field("port", resolve_warehouse_port)

# Seaplane type
seaplane_type = ObjectType("Seaplane")
seaplane_type.set_field("location", resolve_seaplane_port)
seaplane_type.set_field("model", resolve_seaplane_model)
seaplane_type.set_field("status", resolve_seaplane_status)
seaplane_type.set_field("currentPosition", resolve_seaplane_current_position)

# SeaplaneModel type
seaplane_model_type = ObjectType("SeaplaneModel")
seaplane_model_type.set_field("manufacturer", resolve_model_manufacturer)
seaplane_model_type.set_field("seaplanes", resolve_model_seaplanes)

# Manufacturer type
manufacturer_type = ObjectType("Manufacturer")
manufacturer_type.set_field("models", resolve_manufacturer_models)

# SeaplaneStatus type
seaplane_status_type = ObjectType("SeaplaneStatus")
seaplane_status_type.set_field("seaplanes", resolve_status_seaplane)

# MaintenanceResponse type
maintenance_response_type = ObjectType("MaintenanceResponse")
maintenance_response_type.set_field("seaplane", resolve_seaplane_port)

# Order type
order_type = ObjectType("Order")
order_type.set_field("client", resolve_order_client)
order_type.set_field("warehouse", resolve_order_warehouse)
order_type.set_field("locker", resolve_order_locker)

# Delivery type
delivery_type = ObjectType("Delivery")
delivery_type.set_field("seaplane", resolve_delivery_seaplane)
delivery_type.set_field("orders", resolve_delivery_orders)
delivery_type.set_field("progress", resolve_delivery_progress_field)

# ============================================================================
# Create Executable Schema
# ============================================================================
schema = make_executable_schema(
    type_defs,
    [
        query_type,
        mutation_type,
        island_type,
        port_type,
        client_type,
        locker_type,
        warehouse_type,
        seaplane_type,
        seaplane_model_type,
        manufacturer_type,
        seaplane_status_type,
        maintenance_response_type,
        order_type,
        delivery_type,
    ],
)

# ============================================================================
# Flask App
# ============================================================================
app = Flask(__name__, template_folder="template")
explorer_html = ExplorerGraphiQL().html(None)


@app.route("/", methods=["GET"])
def index():
    return render_template("app.html")


@app.route("/graphql", methods=["GET"])
def graphql_explorer():
    return explorer_html, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value={"request": request},
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code


@app.cli.command("migrate")
def migrate_command():
    """Run database migrations."""
    print("Running migrations...")
    migrate()
    print("Migrations completed successfully!")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
