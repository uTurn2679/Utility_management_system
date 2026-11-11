import { getAll, add, update, remove, addNotification } from '../db.js';

export const MetersView = {
  render(container, user, showToast, openModal, closeModal) {
    if (user.role !== 'admin' && user.role !== 'employee') {
      container.innerHTML = `<div class="content-card"><p class="text-danger">Access Denied. Admins and Employees only.</p></div>`;
      return;
    }

    this.renderList(container, user, showToast, openModal, closeModal);
  },

  renderList(container, user, showToast, openModal, closeModal) {
    const meters = getAll('meters');
    const customers = getAll('customers');
    const users = getAll('users');
    const readings = getAll('meter_readings');

    container.innerHTML = `
      <div class="filter-row">
        <div class="search-wrapper">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input type="text" id="meter-search" placeholder="Search meter number...">
        </div>
        <div class="filter-actions">
          <select id="meter-type-filter">
            <option value="">All Utilities</option>
            <option value="electricity">Electricity</option>
            <option value="water">Water</option>
            <option value="gas">Gas</option>
            <option value="wifi">WiFi</option>
          </select>
          ${user.role === 'admin' ? `
            <button class="btn btn-primary" id="add-meter-btn">
              <i class="fa-solid fa-plus"></i> Register Meter
            </button>
          ` : ''}
          <button class="btn btn-secondary" id="log-reading-btn">
            <i class="fa-solid fa-pen-to-square"></i> Log Reading
          </button>
        </div>
      </div>

      <div class="content-card">
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Meter Number</th>
                <th>Utility Type</th>
                <th>Assigned Customer</th>
                <th>Current Reading</th>
                <th>Installation Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="meter-table-body">
              <!-- Filled by JS -->
            </tbody>
          </table>
        </div>
      </div>
    `;

    const populateTable = () => {
      const searchTerm = document.getElementById('meter-search').value.toLowerCase();
      const typeFilter = document.getElementById('meter-type-filter').value;
      const tbody = document.getElementById('meter-table-body');

      const filtered = meters.filter(m => {
        const matchesSearch = m.meter_number.toLowerCase().includes(searchTerm);
        const matchesType = typeFilter === '' || m.utilityType === typeFilter;
        return matchesSearch && matchesType;
      });

      if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-muted" style="text-align:center;">No meters found.</td></tr>`;
        return;
      }

      tbody.innerHTML = filtered.map(m => {
        const customer = customers.find(c => c.customer_id === m.customer_id);
        const custUser = customer ? users.find(u => u.id === customer.user_id) : null;
        const custText = custUser ? `<strong>${custUser.name}</strong><br><small class="text-muted">${customer.phone}</small>` : '<span class="text-muted">Unassigned</span>';
        const unit = m.utilityType === 'electricity' ? 'kWh' : m.utilityType === 'wifi' ? 'Mbps' : 'm³';

        // Retrieve current reading from meter_readings
        const meterReadings = readings.filter(r => r.meter_id === m.meter_id);
        const currentReading = meterReadings.length > 0 ? Math.max(...meterReadings.map(r => r.unit_consumed)) : 0;

        let statusClass = 'success';
        if (m.status === 'maintenance') statusClass = 'warning';
        if (m.status === 'suspended') statusClass = 'danger';

        const actionButtons = user.role === 'admin' ? `
          <button class="btn-icon-only edit-meter-btn" data-id="${m.meter_id}" title="Edit Meter Specifications">
            <i class="fa-solid fa-pen"></i>
          </button>
          <button class="btn-icon-only danger delete-meter-btn" data-id="${m.meter_id}" title="Delete Meter">
            <i class="fa-solid fa-trash-can"></i>
          </button>
        ` : `
          <button class="btn-icon-only edit-meter-status-btn" data-id="${m.meter_id}" title="Change Status">
            <i class="fa-solid fa-sliders"></i>
          </button>
        `;

        return `
          <tr>
            <td><strong>${m.meter_number}</strong></td>
            <td><span class="badge badge-info">${m.utilityType.toUpperCase()}</span></td>
            <td>${custText}</td>
            <td><strong>${currentReading}</strong> ${unit}</td>
            <td>${m.installDate}</td>
            <td><span class="badge badge-${statusClass}">${m.status}</span></td>
            <td>
              <div class="action-btn-group">
                ${actionButtons}
              </div>
            </td>
          </tr>
        `;
      }).join('');

      // Actions bindings
      tbody.querySelectorAll('.edit-meter-status-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.showStatusModal(btn.dataset.id, openModal, closeModal, showToast, () => {
            this.renderList(container, user, showToast, openModal, closeModal);
          });
        });
      });

      tbody.querySelectorAll('.edit-meter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.showEditMeterModal(btn.dataset.id, openModal, closeModal, showToast, () => {
            this.renderList(container, user, showToast, openModal, closeModal);
          });
        });
      });

      tbody.querySelectorAll('.delete-meter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.showDeleteMeterModal(btn.dataset.id, openModal, closeModal, showToast, () => {
            this.renderList(container, user, showToast, openModal, closeModal);
          });
        });
      });
    };

    populateTable();

    // Event handlers
    document.getElementById('meter-search').addEventListener('input', populateTable);
    document.getElementById('meter-type-filter').addEventListener('change', populateTable);

    const addMeterBtn = document.getElementById('add-meter-btn');
    if (addMeterBtn) {
      addMeterBtn.addEventListener('click', () => {
        this.showAddMeterModal(openModal, closeModal, showToast, () => {
          this.renderList(container, user, showToast, openModal, closeModal);
        });
      });
    }

    document.getElementById('log-reading-btn').addEventListener('click', () => {
      this.showLogReadingModal(openModal, closeModal, showToast, () => {
        this.renderList(container, user, showToast, openModal, closeModal);
      });
    });
  },

  showStatusModal(meterId, openModal, closeModal, showToast, refreshCallback) {
    const meter = getAll('meters').find(m => m.meter_id === meterId);

    const modalHtml = `
      <div class="modal-header">
        <h2>Change Meter Status</h2>
      </div>
      <form id="edit-meter-status-form">
        <div class="form-group">
          <label>Meter Number</label>
          <input type="text" value="${meter.meter_number}" disabled style="opacity:0.7;">
        </div>
        <div class="form-group">
          <label for="meter-status-select">Select Status</label>
          <select id="meter-status-select">
            <option value="active" ${meter.status === 'active' ? 'selected' : ''}>Active</option>
            <option value="maintenance" ${meter.status === 'maintenance' ? 'selected' : ''}>Maintenance</option>
            <option value="suspended" ${meter.status === 'suspended' ? 'selected' : ''}>Suspended</option>
          </select>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" id="cancel-status-btn">Cancel</button>
          <button type="submit" class="btn btn-primary">Save Changes</button>
        </div>
      </form>
    `;

    openModal(modalHtml, () => {
      document.getElementById('cancel-status-btn').addEventListener('click', closeModal);
      document.getElementById('edit-meter-status-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const status = document.getElementById('meter-status-select').value;
        update('meters', meterId, { status });
        showToast('Meter status updated successfully', 'success');

        if (meter.customer_id) {
          const customer = getAll('customers').find(c => c.customer_id === meter.customer_id);
          if (customer) {
            addNotification(customer.user_id, `Your meter status has been changed to: ${status.toUpperCase()}`, 'warning');
          }
        }

        closeModal();
        refreshCallback();
      });
    });
  },

  showAddMeterModal(openModal, closeModal, showToast, refreshCallback) {
    const modalHtml = `
      <div class="modal-header">
        <h2>Register New Meter</h2>
      </div>
      <form id="add-meter-form">
        <div class="form-group">
          <label for="new-meter-serial">Meter Number</label>
          <input type="text" id="new-meter-serial" placeholder="MET-XXXXXX" required>
        </div>
        <div class="form-group">
          <label for="new-meter-type">Utility Type</label>
          <select id="new-meter-type" required>
            <option value="electricity">Electricity (kWh)</option>
            <option value="water">Water (m³)</option>
            <option value="gas">Gas (m³)</option>
            <option value="wifi">WiFi (Mbps)</option>
          </select>
        </div>
        <div class="form-group">
          <label for="new-meter-reading">Initial Reading</label>
          <input type="number" id="new-meter-reading" min="0" value="0" required>
        </div>
        <div class="form-group">
          <label for="new-meter-date">Installation Date</label>
          <input type="date" id="new-meter-date" required>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" id="cancel-meter-btn">Cancel</button>
          <button type="submit" class="btn btn-primary">Register</button>
        </div>
      </form>
    `;

    openModal(modalHtml, () => {
      document.getElementById('new-meter-date').value = new Date().toISOString().split('T')[0];
      document.getElementById('cancel-meter-btn').addEventListener('click', closeModal);

      document.getElementById('add-meter-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const meterNumber = document.getElementById('new-meter-serial').value.trim().toUpperCase();
        const utilityType = document.getElementById('new-meter-type').value;
        const initialReading = parseInt(document.getElementById('new-meter-reading').value, 10);
        const installDate = document.getElementById('new-meter-date').value;

        const metersList = getAll('meters');
        if (metersList.some(m => m.meter_number === meterNumber)) {
          showToast('Meter Number already exists.', 'danger');
          return;
        }

        const newMeter = add('meters', {
          meter_number: meterNumber,
          utilityType,
          installDate,
          customer_id: null,
          status: 'active'
        });

        // Log the initial reading value inside meter_readings table
        add('meter_readings', {
          meter_id: newMeter.meter_id,
          month: 'Initial',
          unit_consumed: initialReading
        });

        showToast('Meter registered successfully.', 'success');
        closeModal();
        refreshCallback();
      });
    });
  },

  showEditMeterModal(meterId, openModal, closeModal, showToast, refreshCallback) {
    const meter = getAll('meters').find(m => m.meter_id === meterId);
    const customers = getAll('customers');
    const users = getAll('users');

    const modalHtml = `
      <div class="modal-header">
        <h2>Edit Meter Specifications</h2>
      </div>
      <form id="edit-meter-form">
        <div class="form-group">
          <label for="edit-meter-number">Meter Number</label>
          <input type="text" id="edit-meter-number" value="${meter.meter_number}" required>
        </div>
        <div class="form-group" style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
          <div>
            <label for="edit-meter-type">Utility Type</label>
            <select id="edit-meter-type" required>
              <option value="electricity" ${meter.utilityType === 'electricity' ? 'selected' : ''}>Electricity (kWh)</option>
              <option value="water" ${meter.utilityType === 'water' ? 'selected' : ''}>Water (m³)</option>
              <option value="gas" ${meter.utilityType === 'gas' ? 'selected' : ''}>Gas (m³)</option>
              <option value="wifi" ${meter.utilityType === 'wifi' ? 'selected' : ''}>WiFi (Mbps)</option>
            </select>
          </div>
          <div>
            <label for="edit-meter-status">Meter Status</label>
            <select id="edit-meter-status" required>
              <option value="active" ${meter.status === 'active' ? 'selected' : ''}>Active</option>
              <option value="maintenance" ${meter.status === 'maintenance' ? 'selected' : ''}>Maintenance</option>
              <option value="suspended" ${meter.status === 'suspended' ? 'selected' : ''}>Suspended</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label for="edit-meter-date">Installation Date</label>
          <input type="date" id="edit-meter-date" value="${meter.installDate}" required>
        </div>
        <div class="form-group">
          <label for="edit-meter-customer">Assign Customer</label>
          <select id="edit-meter-customer">
            <option value="">-- Unassigned / Free --</option>
            ${customers.map(c => {
              const u = users.find(usr => usr.id === c.user_id);
              const isAssigned = c.customer_id === meter.customer_id;
              return `<option value="${c.customer_id}" ${isAssigned ? 'selected' : ''}>${u ? u.name : 'Unknown'} (${c.customer_id})</option>`;
            }).join('')}
          </select>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" id="cancel-edit-btn">Cancel</button>
          <button type="submit" class="btn btn-primary">Save Changes</button>
        </div>
      </form>
    `;

    openModal(modalHtml, () => {
      document.getElementById('cancel-edit-btn').addEventListener('click', closeModal);

      document.getElementById('edit-meter-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const meter_number = document.getElementById('edit-meter-number').value.trim().toUpperCase();
        const utilityType = document.getElementById('edit-meter-type').value;
        const status = document.getElementById('edit-meter-status').value;
        const installDate = document.getElementById('edit-meter-date').value;
        const customer_id = document.getElementById('edit-meter-customer').value || null;

        const metersList = getAll('meters');
        // Validate duplicates excluding current meter
        if (metersList.some(m => m.meter_number === meter_number && m.meter_id !== meterId)) {
          showToast('Meter Number already registered on another meter.', 'danger');
          return;
        }

        // Update the meter details
        update('meters', meterId, {
          meter_number,
          utilityType,
          status,
          installDate,
          customer_id
        });

        showToast('Meter specs and customer assignment updated.', 'success');
        closeModal();
        refreshCallback();
      });
    });
  },

  showDeleteMeterModal(meterId, openModal, closeModal, showToast, refreshCallback) {
    const meter = getAll('meters').find(m => m.meter_id === meterId);

    const modalHtml = `
      <div class="modal-header">
        <h2 class="text-danger"><i class="fa-solid fa-trash-can"></i> De-register Meter?</h2>
      </div>
      <div style="font-size:0.9rem; line-height:1.5; margin-bottom:24px;">
        <p>Are you sure you want to permanently de-register the meter <strong>${meter.meter_number}</strong> (${meter.utilityType.toUpperCase()})?</p>
        <p class="text-muted" style="margin-top:8px;">This will remove the meter details and its telemetry records. Any assigned customer will be unlinked automatically.</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" id="cancel-delete-btn">Cancel</button>
        <button class="btn btn-danger" id="confirm-delete-btn">Confirm Delete</button>
      </div>
    `;

    openModal(modalHtml, () => {
      document.getElementById('cancel-delete-btn').addEventListener('click', closeModal);

      document.getElementById('confirm-delete-btn').addEventListener('click', () => {
        // Remove from meters
        remove('meters', meterId);

        // Remove linked readings history
        const readings = getAll('meter_readings');
        const filteredReadings = readings.filter(r => r.meter_id !== meterId);
        localStorage.setItem('utilis_db_meter_readings', JSON.stringify(filteredReadings));

        showToast(`Meter ${meter.meter_number} de-registered successfully.`, 'warning');
        closeModal();
        refreshCallback();
      });
    });
  },

  showLogReadingModal(openModal, closeModal, showToast, refreshCallback) {
    const customers = getAll('customers');
    const users = getAll('users');
    const meters = getAll('meters').filter(m => m.status === 'active');
    const readings = getAll('meter_readings');

    const modalHtml = `
      <div class="modal-header">
        <h2>Log Meter Reading</h2>
      </div>
      <form id="log-reading-form">
        <div class="form-group">
          <label for="log-customer-select">Select Customer</label>
          <select id="log-customer-select" required>
            <option value="">-- Choose Customer --</option>
            ${customers.map(c => {
              const u = users.find(usr => usr.id === c.user_id);
              return `<option value="${c.customer_id}">${u ? u.name : 'Unknown'} (${c.customer_id})</option>`;
            }).join('')}
          </select>
        </div>
        <div class="form-group">
          <label for="log-meter-select">Select Meter</label>
          <select id="log-meter-select" required disabled>
            <option value="">-- Select Customer First --</option>
          </select>
        </div>
        <div class="form-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
          <div>
            <label for="log-prev-reading">Previous Reading</label>
            <input type="number" id="log-prev-reading" disabled style="opacity:0.7;">
          </div>
          <div>
            <label for="log-new-reading">Current Reading</label>
            <input type="number" id="log-new-reading" min="0" required disabled>
          </div>
        </div>
        <div class="form-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
          <div>
            <label for="log-month">Billing Month</label>
            <select id="log-month" required disabled>
              <option value="January">January</option>
              <option value="February">February</option>
              <option value="March">March</option>
              <option value="April">April</option>
              <option value="May">May</option>
              <option value="June" selected>June</option>
              <option value="July">July</option>
              <option value="August">August</option>
              <option value="September">September</option>
              <option value="October">October</option>
              <option value="November">November</option>
              <option value="December">December</option>
            </select>
          </div>
          <div>
            <label for="log-consumed-reading">Consumed Unit (Calculated)</label>
            <input type="number" id="log-consumed-reading" disabled value="0" style="opacity:0.7; font-weight:700; color:var(--primary);">
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" id="cancel-log-btn">Cancel</button>
          <button type="submit" class="btn btn-primary" id="submit-log-btn" disabled>Log Reading</button>
        </div>
      </form>
    `;

    openModal(modalHtml, () => {
      const custSelect = document.getElementById('log-customer-select');
      const meterSelect = document.getElementById('log-meter-select');
      const prevInput = document.getElementById('log-prev-reading');
      const newInput = document.getElementById('log-new-reading');
      const monthSelect = document.getElementById('log-month');
      const consumedInput = document.getElementById('log-consumed-reading');
      const submitBtn = document.getElementById('submit-log-btn');

      const updateConsumedUnits = () => {
        const prev = parseInt(prevInput.value, 10) || 0;
        const curr = parseInt(newInput.value, 10) || 0;
        const consumed = curr >= prev ? curr - prev : 0;
        consumedInput.value = consumed;
      };

      newInput.addEventListener('input', updateConsumedUnits);

      custSelect.addEventListener('change', () => {
        const cId = custSelect.value;
        meterSelect.innerHTML = '<option value="">-- Choose Meter --</option>';
        prevInput.value = '';
        newInput.value = '';
        newInput.disabled = true;
        monthSelect.disabled = true;
        consumedInput.value = '0';
        submitBtn.disabled = true;

        if (!cId) {
          meterSelect.disabled = true;
          return;
        }

        const filteredMeters = meters.filter(m => m.customer_id === cId);
        if (filteredMeters.length === 0) {
          showToast('No active meters assigned to this customer.', 'warning');
          meterSelect.disabled = true;
          return;
        }

        meterSelect.innerHTML += filteredMeters.map(m => `
          <option value="${m.meter_id}">${m.meter_number} (${m.utilityType.toUpperCase()})</option>
        `).join('');
        meterSelect.disabled = false;
      });

      meterSelect.addEventListener('change', () => {
        const mId = meterSelect.value;
        if (!mId) {
          prevInput.value = '';
          newInput.value = '';
          newInput.disabled = true;
          monthSelect.disabled = true;
          consumedInput.value = '0';
          submitBtn.disabled = true;
          return;
        }

        const meterReadings = readings.filter(r => r.meter_id === mId);
        const currentReading = meterReadings.length > 0 ? Math.max(...meterReadings.map(r => r.unit_consumed)) : 0;

        prevInput.value = currentReading;
        newInput.disabled = false;
        newInput.min = currentReading;
        newInput.value = currentReading + 120; // auto increment
        monthSelect.disabled = false;
        submitBtn.disabled = false;
        updateConsumedUnits();
      });

      document.getElementById('cancel-log-btn').addEventListener('click', closeModal);

      document.getElementById('log-reading-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const mId = meterSelect.value;
        const newReading = parseInt(newInput.value, 10);
        const prevReading = parseInt(prevInput.value, 10);
        const month = monthSelect.value;

        if (newReading < prevReading) {
          showToast('Current reading cannot be lower than the previous reading.', 'danger');
          return;
        }

        // Add to meter_readings table
        add('meter_readings', {
          meter_id: mId,
          month: month,
          unit_consumed: newReading
        });

        showToast('Reading logged successfully', 'success');

        const meterObj = meters.find(m => m.meter_id === mId);
        if (meterObj.customer_id) {
          const customer = customers.find(c => c.customer_id === meterObj.customer_id);
          if (customer) {
            addNotification(customer.user_id, `A new meter reading of ${newReading} units was logged for ${month}.`, 'info');
          }
        }

        closeModal();
        refreshCallback();
      });
    });
  }
};
