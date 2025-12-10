// Store clients data
const allClients = {};

// GraphQL Queries
const CLIENTS_QUERY = `
    query {
        clients {
            id
            name
            specialty
            locker { id capacity remaining_capacity }
        }
    }
`;

const WAREHOUSES_QUERY = `
    query {
        warehouses {
            id
            name
            port { name }
        }
    }
`;

const CREATE_ORDER_MUTATION = `
    mutation CreateOrder($clientId: Int!, $warehouseId: Int!, $crateQuantity: Int!) {
        createOrder(client_id: $clientId, warehouse_id: $warehouseId, crateQuantity: $crateQuantity) {
            success
            message
            order { id crate_quantity status }
        }
    }
`;

// Load clients for the order form
async function loadClients() {
  try {
    const response = await fetch("/graphql", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: CLIENTS_QUERY }),
    });

    const result = await response.json();

    if (result.data && result.data.clients) {
      const clientSelect = document.getElementById("client-select");

      result.data.clients.forEach(function (client) {
        allClients[client.id] = client;
        const option = document.createElement("option");
        option.value = client.id;
        option.textContent = client.name + " (" + client.specialty + ")";
        clientSelect.appendChild(option);
      });
    }
  } catch (error) {
    console.error("Error loading clients:", error);
  }
}

// Load warehouses for the order form
async function loadWarehouses() {
  try {
    const response = await fetch("/graphql", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: WAREHOUSES_QUERY }),
    });

    const result = await response.json();

    if (result.data && result.data.warehouses) {
      const warehouseSelect = document.getElementById("warehouse-select");

      result.data.warehouses.forEach(function (warehouse) {
        const option = document.createElement("option");
        option.value = warehouse.id;
        option.textContent = warehouse.name + " (" + warehouse.port.name + ")";
        warehouseSelect.appendChild(option);
      });
    }
  } catch (error) {
    console.error("Error loading warehouses:", error);
  }
}

// Handle client selection to show locker info
document
  .getElementById("client-select")
  .addEventListener("change", function () {
    const clientId = this.value;
    const clientInfo = document.getElementById("client-info");
    const lockerCapacity = document.getElementById("locker-capacity");
    const crateInput = document.getElementById("crate-quantity");

    if (clientId && allClients[clientId]) {
      const client = allClients[clientId];
      if (client.locker) {
        clientInfo.style.display = "block";
        lockerCapacity.textContent = client.locker.remaining_capacity;
        crateInput.max = client.locker.remaining_capacity;
      } else {
        clientInfo.style.display = "block";
        lockerCapacity.textContent = "No locker assigned";
      }
    } else {
      clientInfo.style.display = "none";
    }
  });

// Handle order form submission
document
  .getElementById("order-form")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const clientId = parseInt(document.getElementById("client-select").value);
    const warehouseId = parseInt(
      document.getElementById("warehouse-select").value,
    );
    const crateQuantity = parseInt(
      document.getElementById("crate-quantity").value,
    );
    const submitBtn = document.getElementById("submit-order");
    const messageDiv = document.getElementById("order-message");

    submitBtn.disabled = true;
    submitBtn.textContent = "Placing Order...";

    try {
      const response = await fetch("/graphql", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: CREATE_ORDER_MUTATION,
          variables: {
            clientId: clientId,
            warehouseId: warehouseId,
            crateQuantity: crateQuantity,
          },
        }),
      });

      const result = await response.json();

      if (result.data && result.data.createOrder) {
        const orderResult = result.data.createOrder;

        if (orderResult.success) {
          messageDiv.className = "order-message success";
          messageDiv.textContent = orderResult.message;

          document.getElementById("order-form").reset();
          document.getElementById("client-info").style.display = "none";

          // Reload clients to update locker capacities
          setTimeout(function () {
            const clientSelect = document.getElementById("client-select");
            clientSelect.innerHTML =
              '<option value="">Select a client...</option>';
            loadClients();
          }, 1000);
        } else {
          messageDiv.className = "order-message error";
          messageDiv.textContent = orderResult.message;
        }
      } else if (result.errors) {
        messageDiv.className = "order-message error";
        messageDiv.textContent = "Error: " + result.errors[0].message;
      }
    } catch (error) {
      messageDiv.className = "order-message error";
      messageDiv.textContent = "Failed to place order. Please try again.";
      console.error("Error creating order:", error);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Place Order";

      // Hide message after 5 seconds
      setTimeout(function () {
        messageDiv.className = "order-message";
      }, 5000);
    }
  });

// Load data when this script runs
loadClients();
loadWarehouses();
