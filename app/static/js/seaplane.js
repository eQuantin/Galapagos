// Display seaplane details in the info panel
function showSeaplaneDetails(seaplane) {
    document.getElementById('placeholder').style.display = 'none';
    document.getElementById('seaplane-details').classList.add('active');

    document.getElementById('seaplane-name').textContent = seaplane.name;

    const statusEl = document.getElementById('seaplane-status');
    const status = seaplane.status ? seaplane.status.value : 'unknown';
    statusEl.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    statusEl.className = 'status-badge status-' + status;

    if (seaplane.model) {
        document.getElementById('seaplane-model').textContent = seaplane.model.name;
        document.getElementById('seaplane-manufacturer').textContent =
            seaplane.model.manufacturer ? seaplane.model.manufacturer.name : '-';
        document.getElementById('seaplane-capacity').textContent = seaplane.model.crate_capacity;
        document.getElementById('seaplane-fuel-capacity').textContent =
            seaplane.model.fuel_capacity_L.toFixed(1);
        document.getElementById('seaplane-consumption').textContent =
            seaplane.model.fuel_consumption_L_per_km.toFixed(2) + ' L/km';
        document.getElementById('seaplane-speed').textContent =
            seaplane.model.average_speed_kmh.toFixed(0) + ' km/h';
        document.getElementById('seaplane-cost').textContent =
            '$' + seaplane.model.cost_per_km_USD.toFixed(2);

        const fuelPercentage = (seaplane.fuel / seaplane.model.fuel_capacity_L) * 100;
        const fuelBar = document.getElementById('fuel-bar-fill');
        fuelBar.style.width = fuelPercentage + '%';
        fuelBar.classList.toggle('low', fuelPercentage < 25);
    }

    document.getElementById('seaplane-location').textContent =
        seaplane.location ? seaplane.location.name : 'In flight';
    document.getElementById('seaplane-crates').textContent = seaplane.crates;
    document.getElementById('seaplane-fuel').textContent = seaplane.fuel.toFixed(1);
}
