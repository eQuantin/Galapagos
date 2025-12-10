// Store seaplanes and orders data
const deliverySeaplanes = {};
const deliveryPendingOrders = [];
const deliverySelectedOrders = new Set();

// GraphQL Queries and Mutations
const DELIVERY_SEAPLANES_QUERY = `
    query {
        seaplanes {
            name
            status { value }
            location { name }
            model {
                crate_capacity
            }
            crates
        }
    }
`;

const DELIVERY_PENDING_ORDERS_QUERY = `
    query {
        ordersByStatus(status: "pending") {
            id
            crate_quantity
            client { name locker { port { name } } }
            warehouse { name port { name } }
            created_at
        }
    }
`;

const DELIVERY_CREATE_MUTATION = `
    mutation CreateDelivery($orderIds: [String!]!, $seaplaneName: String!) {
        createDelivery(orderIds: $orderIds, seaplaneName: $seaplaneName) {
            success
            message
            delivery {
                id
                route
                total_distance_km
                estimated_duration_hours
            }
        }
    }
`;

// Load seaplanes for delivery form
async function loadSeaplanes() {
  try {
    const response = await fetch("/graphql", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: DELIVERY_SEAPLANES_QUERY }),
    });

    const result = await response.json();

    if (result.data && result.data.seaplanes) {
      const seaplaneSelect = document.getElementById(
        "seaplane-delivery-select",
      );

      // Filter for available seaplanes (docked status)
      const availableSeaplanes = result.data.seaplanes.filter(function (sp) {
        return sp.status.value === "docked";
      });

      availableSeaplanes.forEach(function (seaplane) {
        deliverySeaplanes[seaplane.name] = seaplane;
        const option = document.createElement("option");
        option.value = seaplane.name;
        option.textContent =
          seaplane.name + " (" + seaplane.model.crate_capacity + " crates)";
        seaplaneSelect.appendChild(option);
      });
    }
  } catch (error) {
    console.error("Error loading seaplanes:", error);
  }
}

// Load pending orders
async function loadPendingOrders() {
  try {
    const response = await fetch("/graphql", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: DELIVERY_PENDING_ORDERS_QUERY }),
    });

    const result = await response.json();

    if (result.data && result.data.ordersByStatus) {
      deliveryPendingOrders.length = 0;
      deliveryPendingOrders.push.apply(
        deliveryPendingOrders,
        result.data.ordersByStatus,
      );
      renderOrderList();
    }
  } catch (error) {
    console.error("Error loading pending orders:", error);
  }
}

// Render order list with checkboxes
function renderOrderList() {
  const orderListDiv = document.getElementById("order-list");

  if (deliveryPendingOrders.length === 0) {
    orderListDiv.innerHTML =
      '<div class="order-list-empty">No pending orders available</div>';
    return;
  }

  orderListDiv.innerHTML = "";

  deliveryPendingOrders.forEach(function (order) {
    const orderItem = document.createElement("div");
    orderItem.className = "order-item";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = "order-" + order.id;
    checkbox.value = order.id;
    checkbox.className = "order-checkbox";

    checkbox.addEventListener("change", function () {
      if (this.checked) {
        deliverySelectedOrders.add(order.id);
      } else {
        deliverySelectedOrders.delete(order.id);
      }
      updateSelectedOrdersInfo();
    });

    const label = document.createElement("label");
    label.htmlFor = "order-" + order.id;
    label.className = "order-label";

    const orderInfo = document.createElement("div");
    orderInfo.className = "order-info";

    const clientName = order.client ? order.client.name : "Unknown";
    const warehouseName = order.warehouse ? order.warehouse.name : "Unknown";
    const warehousePort =
      order.warehouse && order.warehouse.port
        ? order.warehouse.port.name
        : "Unknown";
    const clientPort =
      order.client && order.client.locker && order.client.locker.port
        ? order.client.locker.port.name
        : "Unknown";

    orderInfo.innerHTML =
      '<div class="order-main-info">' +
      "<strong>Order #" +
      order.id.substring(0, 8) +
      "</strong> - " +
      '<span class="order-crates">' +
      order.crate_quantity +
      " crate(s)</span>" +
      "</div>" +
      '<div class="order-route-info">' +
      warehouseName +
      " (" +
      warehousePort +
      ") → " +
      clientName +
      " (" +
      clientPort +
      ")" +
      "</div>";

    label.appendChild(orderInfo);

    orderItem.appendChild(checkbox);
    orderItem.appendChild(label);

    orderListDiv.appendChild(orderItem);
  });
}

// Update selected orders info display
function updateSelectedOrdersInfo() {
  const infoDiv = document.getElementById("selected-orders-info");
  const orderCountSpan = document.getElementById("selected-order-count");
  const crateCountSpan = document.getElementById("selected-crate-count");

  if (deliverySelectedOrders.size === 0) {
    infoDiv.style.display = "none";
    return;
  }

  infoDiv.style.display = "block";
  orderCountSpan.textContent = deliverySelectedOrders.size;

  let totalCrates = 0;
  deliverySelectedOrders.forEach(function (orderId) {
    const order = deliveryPendingOrders.find(function (o) {
      return o.id === orderId;
    });
    if (order) {
      totalCrates += order.crate_quantity;
    }
  });

  crateCountSpan.textContent = totalCrates;

  // Validate against seaplane capacity if selected
  const seaplaneName = document.getElementById(
    "seaplane-delivery-select",
  ).value;
  if (seaplaneName && deliverySeaplanes[seaplaneName]) {
    const capacity = deliverySeaplanes[seaplaneName].model.crate_capacity;
    if (totalCrates > capacity) {
      crateCountSpan.style.color = "#dc3545";
      crateCountSpan.style.fontWeight = "bold";
    } else {
      crateCountSpan.style.color = "#28a745";
      crateCountSpan.style.fontWeight = "bold";
    }
  }
}

// Handle seaplane selection to show info
document
  .getElementById("seaplane-delivery-select")
  .addEventListener("change", function () {
    const seaplaneName = this.value;
    const seaplaneInfo = document.getElementById("seaplane-delivery-info");
    const statusSpan = document.getElementById("seaplane-delivery-status");
    const capacitySpan = document.getElementById("seaplane-delivery-capacity");
    const locationSpan = document.getElementById("seaplane-delivery-location");

    if (seaplaneName && deliverySeaplanes[seaplaneName]) {
      const seaplane = deliverySeaplanes[seaplaneName];
      seaplaneInfo.style.display = "block";
      statusSpan.textContent = seaplane.status.value;
      capacitySpan.textContent = seaplane.model.crate_capacity;
      locationSpan.textContent = seaplane.location
        ? seaplane.location.name
        : "Unknown";

      // Re-validate selected orders
      updateSelectedOrdersInfo();
    } else {
      seaplaneInfo.style.display = "none";
    }
  });

// Handle delivery form submission
document
  .getElementById("delivery-form")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const seaplaneName = document.getElementById(
      "seaplane-delivery-select",
    ).value;
    const submitBtn = document.getElementById("submit-delivery");
    const messageDiv = document.getElementById("delivery-message");

    // Validation
    if (deliverySelectedOrders.size === 0) {
      messageDiv.className = "delivery-message error";
      messageDiv.textContent = "Please select at least one order";
      setTimeout(function () {
        messageDiv.className = "delivery-message";
      }, 3000);
      return;
    }

    // Validate total crates against capacity
    if (deliverySeaplanes[seaplaneName]) {
      let totalCrates = 0;
      deliverySelectedOrders.forEach(function (orderId) {
        const order = deliveryPendingOrders.find(function (o) {
          return o.id === orderId;
        });
        if (order) {
          totalCrates += order.crate_quantity;
        }
      });

      const capacity = deliverySeaplanes[seaplaneName].model.crate_capacity;
      if (totalCrates > capacity) {
        messageDiv.className = "delivery-message error";
        messageDiv.textContent =
          "Total crates (" +
          totalCrates +
          ") exceeds seaplane capacity (" +
          capacity +
          ")";
        setTimeout(function () {
          messageDiv.className = "delivery-message";
        }, 3000);
        return;
      }
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Creating Delivery...";

    try {
      const orderIds = Array.from(deliverySelectedOrders);

      const response = await fetch("/graphql", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: DELIVERY_CREATE_MUTATION,
          variables: {
            orderIds: orderIds,
            seaplaneName: seaplaneName,
          },
        }),
      });

      const result = await response.json();

      if (result.data && result.data.createDelivery) {
        const deliveryResult = result.data.createDelivery;

        if (deliveryResult.success) {
          messageDiv.className = "delivery-message success";

          let message = deliveryResult.message;
          if (deliveryResult.delivery) {
            const delivery = deliveryResult.delivery;
            message +=
              "<br><strong>Delivery ID:</strong> " +
              delivery.id.substring(0, 8) +
              "<br><strong>Route:</strong> " +
              delivery.route.join(" → ") +
              "<br><strong>Distance:</strong> " +
              delivery.total_distance_km.toFixed(2) +
              " km" +
              "<br><strong>Est. Duration:</strong> " +
              delivery.estimated_duration_hours.toFixed(2) +
              " hours";
          }
          messageDiv.innerHTML = message;

          // Reset form
          document.getElementById("delivery-form").reset();
          document.getElementById("seaplane-delivery-info").style.display =
            "none";
          deliverySelectedOrders.clear();
          updateSelectedOrdersInfo();

          // Reload data
          setTimeout(function () {
            loadPendingOrders();
            loadSeaplanes();
          }, 1000);
        } else {
          messageDiv.className = "delivery-message error";
          messageDiv.textContent = deliveryResult.message;
        }
      } else if (result.errors) {
        messageDiv.className = "delivery-message error";
        messageDiv.textContent = "Error: " + result.errors[0].message;
      }
    } catch (error) {
      messageDiv.className = "delivery-message error";
      messageDiv.textContent = "Failed to create delivery. Please try again.";
      console.error("Error creating delivery:", error);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Create Delivery";

      // Hide message after 8 seconds
      setTimeout(function () {
        messageDiv.className = "delivery-message";
      }, 8000);
    }
  });

// Load data when page loads
loadSeaplanes();
loadPendingOrders();
