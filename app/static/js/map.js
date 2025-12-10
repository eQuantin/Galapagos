// Initialize the map centered on Galapagos Islands
const map = L.map("map").setView([-0.9538, -90.9656], 9);

// Add OpenStreetMap tiles
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  maxZoom: 18,
}).addTo(map);

// Store seaplanes grouped by location
const seaplanesByLocation = {};
const markers = {};
const allSeaplanes = {};
const portMarkers = {};

// GraphQL query to fetch all seaplanes with their locations
const SEAPLANES_QUERY = `
    query {
        seaplanes {
            name
            fuel
            crates
            status { value }
            location { name latitude longitude }
            model {
                name
                crate_capacity
                fuel_consumption_L_per_km
                fuel_capacity_L
                cost_per_km_USD
                average_speed_kmh
                manufacturer { name }
            }
        }
    }
`;

// Create port marker icon
function createPortMarkerIcon() {
  return L.divIcon({
    className: "port-marker-wrapper",
    html:
      '<div class="marker-wrapper">' +
      '<div style="background: #28a745; border: 3px solid white; border-radius: 50%; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">' +
      '<span style="font-size: 14px;">⚓</span>' +
      "</div>" +
      "</div>",
    iconSize: [26, 26],
    iconAnchor: [13, 13],
    popupAnchor: [0, -13],
  });
}

// Create icon based on seaplane count and status
function createMarkerIcon(seaplanes) {
  const count = seaplanes.length;
  const hasMaintenance = seaplanes.some(function (s) {
    return s.status && s.status.value === "maintenance";
  });
  const hasFlying = seaplanes.some(function (s) {
    return s.status && s.status.value === "flying";
  });

  let bgColor = "#1e3a5f";
  let emoji = "✈️";

  if (hasMaintenance) {
    bgColor = "#ffc107";
    emoji = "🔧";
  } else if (hasFlying) {
    bgColor = "#17a2b8";
    emoji = "🛫";
  }

  const badgeHtml =
    count > 1 ? '<span class="seaplane-count-badge">' + count + "</span>" : "";

  return L.divIcon({
    className: "seaplane-marker-wrapper",
    html:
      '<div class="marker-wrapper">' +
      '<div style="background: ' +
      bgColor +
      '; border: 3px solid white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">' +
      '<span style="font-size: 16px;">' +
      emoji +
      "</span>" +
      "</div>" +
      badgeHtml +
      "</div>",
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15],
  });
}

// Create popup content for location with seaplanes
function createPopupContent(locationName, seaplanes) {
  if (seaplanes.length === 1) {
    return (
      '<div class="popup-title">' +
      seaplanes[0].name +
      "</div>" +
      '<div style="color: #666; font-size: 0.9rem;">📍 ' +
      locationName +
      "</div>" +
      '<div style="margin-top: 8px; color: #1e3a5f; font-size: 0.85rem;">Click for details</div>'
    );
  }

  let itemsHtml = seaplanes
    .map(function (seaplane) {
      const status = seaplane.status ? seaplane.status.value : "unknown";
      let statusEmoji = "✈️";
      if (status === "maintenance") {
        statusEmoji = "🔧";
      } else if (status === "flying") {
        statusEmoji = "🛫";
      }
      return (
        '<div class="seaplane-selector-item" onclick="selectSeaplane(\'' +
        seaplane.name +
        "')\">" +
        '<div class="name">' +
        statusEmoji +
        " " +
        seaplane.name +
        "</div>" +
        '<div class="status">' +
        status.charAt(0).toUpperCase() +
        status.slice(1) +
        "</div>" +
        "</div>"
      );
    })
    .join("");

  return (
    '<div class="popup-title">📍 ' +
    locationName +
    " (" +
    seaplanes.length +
    " seaplanes)</div>" +
    '<div class="seaplane-selector">' +
    itemsHtml +
    "</div>"
  );
}

// Create popup content for port
function createPortPopupContent(port) {
  return (
    '<div class="popup-title">⚓ ' +
    port.name +
    "</div>" +
    '<div style="color: #666; font-size: 0.9rem; margin-top: 4px;">📍 ' +
    port.island.name +
    "</div>" +
    '<div style="margin-top: 8px; color: #666; font-size: 0.85rem;">Coordinates: ' +
    port.latitude.toFixed(4) +
    ", " +
    port.longitude.toFixed(4) +
    "</div>"
  );
}

// Fetch seaplane data and add markers
async function loadSeaplanes() {
  try {
    const response = await fetch("/graphql", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: SEAPLANES_QUERY }),
    });

    const result = await response.json();

    if (result.data && result.data.seaplanes) {
      result.data.seaplanes.forEach(function (seaplane) {
        if (seaplane.location) {
          const locationKey =
            seaplane.location.latitude + "," + seaplane.location.longitude;

          if (!seaplanesByLocation[locationKey]) {
            seaplanesByLocation[locationKey] = {
              name: seaplane.location.name,
              latitude: seaplane.location.latitude,
              longitude: seaplane.location.longitude,
              seaplanes: [],
            };
          }

          seaplanesByLocation[locationKey].seaplanes.push(seaplane);
          allSeaplanes[seaplane.name] = seaplane;
        }
      });

      Object.keys(seaplanesByLocation).forEach(function (locationKey) {
        addLocationMarker(seaplanesByLocation[locationKey]);
      });
    }
  } catch (error) {
    console.error("Error loading seaplanes:", error);
  }
}

// Add a marker for a location with seaplanes
function addLocationMarker(location) {
  const icon = createMarkerIcon(location.seaplanes);
  const popupContent = createPopupContent(location.name, location.seaplanes);

  const marker = L.marker([location.latitude, location.longitude], {
    icon: icon,
  })
    .addTo(map)
    .bindPopup(popupContent, { maxWidth: 250 });

  marker.on("click", function () {
    if (location.seaplanes.length === 1) {
      showSeaplaneDetails(location.seaplanes[0]);
    }
  });

  markers[location.latitude + "," + location.longitude] = marker;
}

// Select a seaplane from the popup list
function selectSeaplane(name) {
  const seaplane = allSeaplanes[name];
  if (seaplane) {
    showSeaplaneDetails(seaplane);
    map.closePopup();
  }
}

window.selectSeaplane = selectSeaplane;

// GraphQL query to fetch all ports
const PORTS_QUERY = `
    query {
        ports {
            name
            latitude
            longitude
            island {
                name
            }
        }
    }
`;

// Fetch port data and add markers
async function loadPorts() {
  try {
    const response = await fetch("/graphql", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: PORTS_QUERY }),
    });

    const result = await response.json();

    if (result.data && result.data.ports) {
      result.data.ports.forEach(function (port) {
        addPortMarker(port);
      });
    }
  } catch (error) {
    console.error("Error loading ports:", error);
  }
}

// Add a marker for a port
function addPortMarker(port) {
  const icon = createPortMarkerIcon();
  const popupContent = createPortPopupContent(port);

  const marker = L.marker([port.latitude, port.longitude], { icon: icon })
    .addTo(map)
    .bindPopup(popupContent, { maxWidth: 250 });

  portMarkers[port.name] = marker;
}

// Load seaplanes and ports when this script runs
loadSeaplanes();
loadPorts();
