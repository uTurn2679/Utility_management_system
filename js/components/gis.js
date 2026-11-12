import { getAll } from '../db.js';

export const GisView = {
  render(container, user, showToast, openModal, closeModal) {
    container.innerHTML = `
      <div style="display:grid; grid-template-columns: 1fr 320px; gap:20px; height:calc(100vh - 160px); min-height:600px;">
        
        <!-- Left: Map Container and Mode Controls -->
        <div style="display:flex; flex-direction:column; gap:16px;">
          <!-- Controls Panel -->
          <div class="content-card" style="padding:16px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div style="display:flex; gap:12px;">
              <button class="btn btn-primary toggle-layer-btn active" id="btn-show-demand" style="gap:6px;">
                <i class="fa-solid fa-gauge-high"></i> Utility Demand
              </button>
              <button class="btn btn-secondary toggle-layer-btn" id="btn-show-issues" style="gap:6px;">
                <i class="fa-solid fa-triangle-exclamation"></i> Complaint Hotspots
              </button>
            </div>
            
            <div style="display:flex; align-items:center; gap:8px;">
              <label for="gis-utility-filter" style="font-size:0.8rem; font-weight:600; color:var(--text-secondary)">Utility Type:</label>
              <select id="gis-utility-filter" style="padding:6px 12px; font-size:0.8rem; width:150px;">
                <option value="all">All Utilities</option>
                <option value="electricity">Electricity</option>
                <option value="water">Water</option>
                <option value="gas">Gas</option>
                <option value="wifi">WiFi</option>
              </select>
            </div>
          </div>
          
          <!-- Interactive Map -->
          <div style="flex:1; position:relative; min-height:450px;">
            <div id="gis-map" style="position:absolute; top:0; bottom:0; left:0; right:0; border-radius:12px; border:1px solid var(--border-color); z-index:1; background:#12121e;"></div>
          </div>
        </div>
        
        <!-- Right: Side Panel with GIS Analytics Stats & Fast-Focus Controls -->
        <div style="display:flex; flex-direction:column; gap:16px; height:100%; overflow-y:auto;">
          <!-- Stats Summary Card -->
          <div class="content-card" style="padding:20px;">
            <h3 style="font-size:1rem; margin-bottom:16px; font-weight:700;"><i class="fa-solid fa-chart-line" style="color:var(--primary)"></i> Spatial Overview</h3>
            <div style="display:flex; flex-direction:column; gap:16px;">
              <div style="background:var(--bg-tertiary); padding:12px; border-radius:8px; border:1px solid var(--border-color)">
                <span style="font-size:0.75rem; color:var(--text-muted);">Highest Demand Area</span>
                <h4 style="font-size:1.15rem; font-weight:700; margin-top:4px;" id="gis-stat-high-demand">Uttara</h4>
              </div>
              <div style="background:var(--bg-tertiary); padding:12px; border-radius:8px; border:1px solid var(--border-color)">
                <span style="font-size:0.75rem; color:var(--text-muted);">Active Spatial Incidents</span>
                <h4 style="font-size:1.15rem; font-weight:700; margin-top:4px; color:var(--danger);" id="gis-stat-incidents">0</h4>
              </div>
              <div style="background:var(--bg-tertiary); padding:12px; border-radius:8px; border:1px solid var(--border-color)">
                <span style="font-size:0.75rem; color:var(--text-muted);">Total Spatial Customers</span>
                <h4 style="font-size:1.15rem; font-weight:700; margin-top:4px;" id="gis-stat-customers">0</h4>
              </div>
            </div>
          </div>
          
          <!-- Quick Focus Navigation -->
          <div class="content-card" style="padding:20px; flex:1;">
            <h3 style="font-size:1rem; margin-bottom:12px; font-weight:700;"><i class="fa-solid fa-compass" style="color:var(--primary)"></i> Neighborhood Focus</h3>
            <p style="font-size:0.75rem; color:var(--text-muted); margin-bottom:16px;">Quickly jump and focus the GIS viewport to specific service sectors:</p>
            <div style="display:flex; flex-direction:column; gap:8px;" id="gis-focus-list">
              <!-- Dynamically rendered -->
            </div>
          </div>
        </div>
        
      </div>
    `;

    setTimeout(() => this.initGisMap(showToast), 100);
  },

  initGisMap(showToast) {
    const mapElement = document.getElementById('gis-map');
    if (!mapElement) return;

    // Define coordinates for Dhaka neighborhoods
    const NEIGHBORHOODS = {
      'mirpur': { lat: 23.8056, lng: 90.3625, name: 'Mirpur' },
      'uttara': { lat: 23.8759, lng: 90.3795, name: 'Uttara' },
      'banani': { lat: 23.7937, lng: 90.4066, name: 'Banani' },
      'gulshan': { lat: 23.7925, lng: 90.4194, name: 'Gulshan' },
      'dhanmondi': { lat: 23.7461, lng: 90.3742, name: 'Dhanmondi' },
      'motijheel': { lat: 23.7330, lng: 90.4172, name: 'Motijheel' },
      'mohammadpur': { lat: 23.7542, lng: 90.3629, name: 'Mohammadpur' }
    };

    // Default map coordinates: Center of Dhaka
    const dhakaCenter = [23.7808, 90.3796];
    
    // Initialize Leaflet Map
    // Leaflet binds to global 'L'
    if (typeof L === 'undefined') {
      showToast('Error loading map library. Please check network connection.', 'danger');
      mapElement.innerHTML = `<div class="text-danger" style="text-align:center; padding: 100px;">Leaflet Map Library CDN Failed to load.</div>`;
      return;
    }

    const map = L.map('gis-map').setView(dhakaCenter, 12);

    // Modern Dark Tile Map style (from CartoDB)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CartoDB</a>',
      subdomains: 'abcd',
      maxZoom: 20
    }).addTo(map);

    // Fetch Database Collections
    const customers = getAll('customers');
    const users = getAll('users');
    const bills = getAll('bills');
    const complaints = getAll('complaints');
    const maintenance = getAll('maintenance');

    // Populate Sidebar focus list
    const focusList = document.getElementById('gis-focus-list');
    focusList.innerHTML = Object.entries(NEIGHBORHOODS).map(([key, n]) => `
      <button class="btn btn-secondary focus-btn" data-lat="${n.lat}" data-lng="${n.lng}" style="text-align:left; font-size:0.8rem; padding:8px 12px; justify-content:space-between;">
        <span><i class="fa-solid fa-location-dot" style="margin-right:6px; color:var(--primary);"></i> ${n.name}</span>
        <i class="fa-solid fa-chevron-right" style="font-size:0.7rem;"></i>
      </button>
    `).join('');

    focusList.querySelectorAll('.focus-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const lat = parseFloat(btn.dataset.lat);
        const lng = parseFloat(btn.dataset.lng);
        map.flyTo([lat, lng], 14, { duration: 1.5 });
      });
    });

    // Address Parsing Helpers mapping customers to coordinates
    const getCoordinatesForCustomer = (customer) => {
      const address = customer.address.toLowerCase();
      
      // Match neighborhood names
      for (const [key, n] of Object.entries(NEIGHBORHOODS)) {
        if (address.includes(key)) {
          // Add a tiny random offset to avoid overlapping customer dots exactly
          const offsetLat = (Math.random() - 0.5) * 0.015;
          const offsetLng = (Math.random() - 0.5) * 0.015;
          return { lat: n.lat + offsetLat, lng: n.lng + offsetLng, sector: n.name };
        }
      }

      // Default fallback coordinate mapping with random offset
      const hash = customer.customer_id.split('-')[1] || '123';
      const offsetLat = (parseInt(hash) % 100 - 50) * 0.0006;
      const offsetLng = (parseInt(hash) % 97 - 48) * 0.0006;
      return { lat: dhakaCenter[0] + offsetLat, lng: dhakaCenter[1] + offsetLng, sector: 'Central Sector' };
    };

    // Calculate demands per neighborhood
    const neighborhoodDemand = {};
    Object.keys(NEIGHBORHOODS).forEach(name => {
      neighborhoodDemand[NEIGHBORHOODS[name].name] = 0;
    });

    // Populate data matrices
    const customersWithCoords = customers.map(c => {
      const coords = getCoordinatesForCustomer(c);
      const userObj = users.find(u => u.id === c.user_id);
      const cBills = bills.filter(b => b.customer_id === c.customer_id);
      const totalBill = cBills.reduce((acc, curr) => acc + curr.amount, 0);
      
      if (coords.sector && neighborhoodDemand[coords.sector] !== undefined) {
        neighborhoodDemand[coords.sector] += totalBill;
      }

      return {
        ...c,
        name: userObj ? userObj.name : 'Unknown Customer',
        lat: coords.lat,
        lng: coords.lng,
        sector: coords.sector,
        totalDemand: totalBill,
        billsList: cBills
      };
    });

    // Determine highest demand area
    let maxDemandArea = 'Uttara';
    let maxVal = -1;
    Object.entries(neighborhoodDemand).forEach(([area, val]) => {
      if (val > maxVal) {
        maxVal = val;
        maxDemandArea = area;
      }
    });

    document.getElementById('gis-stat-high-demand').textContent = maxDemandArea + ` (৳${maxVal.toLocaleString()})`;
    document.getElementById('gis-stat-customers').textContent = customers.length;

    // Layer groups
    const demandLayerGroup = L.layerGroup().addTo(map);
    const incidentLayerGroup = L.layerGroup();

    // Render Utility Demand Circles
    const renderDemandLayer = (utilityTypeFilter) => {
      demandLayerGroup.clearLayers();

      customersWithCoords.forEach(c => {
        // Filter utility specific bills if filtered
        let amount = c.totalDemand;
        if (utilityTypeFilter !== 'all') {
          const filteredBills = c.billsList.filter(b => {
            const meter = getAll('meters').find(m => m.meter_id === b.meterId);
            return meter && meter.utilityType === utilityTypeFilter;
          });
          amount = filteredBills.reduce((acc, curr) => acc + curr.amount, 0);
        }

        if (amount <= 0) return; // skip if no active demand

        // Compute radius and color
        const radius = Math.min(Math.max(amount / 50, 40), 200); // normalized bounds
        let circleColor = 'var(--primary)';
        if (amount > 15000) circleColor = '#f857a6'; // high demand
        else if (amount > 5000) circleColor = '#f5af19'; // medium demand

        const circle = L.circle([c.lat, c.lng], {
          color: circleColor,
          fillColor: circleColor,
          fillOpacity: 0.25,
          radius: radius
        });

        circle.bindPopup(`
          <div style="font-family: var(--font-secondary); padding: 4px;">
            <strong style="font-size:0.9rem; color:#fff;">${c.name}</strong><br>
            <span style="color:var(--text-secondary); font-size:0.8rem;">Sector: ${c.sector}</span><br>
            <span style="color:var(--primary); font-weight:700; font-size:0.95rem; display:block; margin-top:6px;">Demand: ৳${amount.toLocaleString()}</span>
          </div>
        `);

        demandLayerGroup.addLayer(circle);
      });
    };

    // Render Complaint Hotspots
    const renderIncidentsLayer = (utilityTypeFilter) => {
      incidentLayerGroup.clearLayers();
      let incidentCount = 0;

      // Merge complaints and maintenance tickets
      const incidentList = [];
      complaints.forEach(comp => {
        incidentList.push({
          id: comp.complaint_id,
          customer_id: comp.customer_id,
          type: 'Support Ticket',
          category: comp.category, // e.g. billing, meter, connection
          title: comp.subject,
          desc: comp.description,
          status: comp.status
        });
      });

      maintenance.forEach(maint => {
        incidentList.push({
          id: maint.maintenance_id,
          customer_id: maint.customer_id,
          type: 'Maintenance Request',
          category: maint.request_type, // Meter Problem, Line Problem, Water Leakage, Gas Leakage
          title: maint.request_type,
          desc: maint.description,
          status: maint.status
        });
      });

      incidentList.forEach(inc => {
        const cust = customersWithCoords.find(c => c.customer_id === inc.customer_id);
        if (!cust) return;

        // Apply utility type filter match if applicable
        if (utilityTypeFilter !== 'all') {
          const categoryLower = inc.category.toLowerCase();
          const titleLower = inc.title.toLowerCase();
          
          let matches = false;
          if (utilityTypeFilter === 'electricity' && (categoryLower.includes('elec') || titleLower.includes('elec') || categoryLower.includes('meter') || categoryLower.includes('power'))) matches = true;
          if (utilityTypeFilter === 'water' && (categoryLower.includes('water') || titleLower.includes('water') || categoryLower.includes('leak'))) matches = true;
          if (utilityTypeFilter === 'gas' && (categoryLower.includes('gas') || titleLower.includes('gas') || categoryLower.includes('leak'))) matches = true;
          if (utilityTypeFilter === 'wifi' && (categoryLower.includes('wifi') || titleLower.includes('wifi') || categoryLower.includes('connect'))) matches = true;
          
          if (!matches) return; // Skip if filtered
        }

        incidentCount++;

        // Choose color based on status/type
        let markerColor = '#f857a6'; // red for pending
        if (inc.status === 'resolved' || inc.status === 'solved') markerColor = '#00cd9b'; // green for solved
        else if (inc.status === 'assigned' || inc.status === 'processing') markerColor = '#f5af19'; // yellow

        // Create Custom Leaflet DivIcon
        const customIcon = L.divIcon({
          className: 'custom-gis-marker',
          html: `<div style="background-color:${markerColor}; width:12px; height:12px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 10px ${markerColor};"></div>`,
          iconSize: [12, 12]
        });

        const marker = L.marker([cust.lat + 0.001, cust.lng + 0.001], { icon: customIcon }); // slightly offset from demand circle

        marker.bindPopup(`
          <div style="font-family: var(--font-secondary); padding: 4px; max-width:200px;">
            <span class="badge" style="background:${markerColor}; color:#fff; font-size:0.65rem; padding: 2px 6px; border-radius:4px;">${inc.type.toUpperCase()}</span>
            <strong style="font-size:0.85rem; color:#fff; display:block; margin-top:8px;">${inc.title}</strong>
            <p style="color:var(--text-secondary); font-size:0.75rem; margin: 4px 0 8px 0; line-height: 1.3;">${inc.desc.substring(0, 80)}${inc.desc.length > 80 ? '...' : ''}</p>
            <span style="font-size:0.7rem; color:var(--text-muted);">Reporter: ${cust.name} (${cust.sector})</span>
          </div>
        `);

        incidentLayerGroup.addLayer(marker);
      });

      document.getElementById('gis-stat-incidents').textContent = incidentCount;
    };

    // Initial render
    renderDemandLayer('all');
    renderIncidentsLayer('all');

    // Wire Layer Button Toggles
    const btnShowDemand = document.getElementById('btn-show-demand');
    const btnShowIssues = document.getElementById('btn-show-issues');

    btnShowDemand.addEventListener('click', () => {
      btnShowDemand.classList.toggle('active');
      btnShowDemand.classList.toggle('btn-primary');
      btnShowDemand.classList.toggle('btn-secondary');

      if (btnShowDemand.classList.contains('active')) {
        map.addLayer(demandLayerGroup);
      } else {
        map.removeLayer(demandLayerGroup);
      }
    });

    btnShowIssues.addEventListener('click', () => {
      btnShowIssues.classList.toggle('active');
      btnShowIssues.classList.toggle('btn-primary');
      btnShowIssues.classList.toggle('btn-secondary');

      if (btnShowIssues.classList.contains('active')) {
        map.addLayer(incidentLayerGroup);
      } else {
        map.removeLayer(incidentLayerGroup);
      }
    });

    // Wire Utility Type Filter Dropdown
    document.getElementById('gis-utility-filter').addEventListener('change', (e) => {
      const type = e.target.value;
      renderDemandLayer(type);
      renderIncidentsLayer(type);
    });

    // Auto resize map layout on rendering load
    setTimeout(() => {
      map.invalidateSize();
    }, 200);
  }
};
