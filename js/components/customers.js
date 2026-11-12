import { getAll, add, update, remove, addNotification } from '../db.js';

export const CustomersView = {
  render(container, user, showToast, openModal, closeModal) {
    if (user.role !== 'admin') {
      container.innerHTML = `<div class="content-card"><p class="text-danger">Access Denied. Admins only.</p></div>`;
      return;
    }

    this.renderList(container, showToast, openModal, closeModal);
  },

  renderList(container, showToast, openModal, closeModal) {
    const customers = getAll('customers');
    const users = getAll('users');
    const meters = getAll('meters');

    container.innerHTML = `
      <div class="filter-row">
        <div class="search-wrapper">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input type="text" id="customer-search" placeholder="Search by name, email or username...">
        </div>
        <div class="filter-actions">
          <button class="btn btn-primary" id="add-customer-btn">
            <i class="fa-solid fa-user-plus"></i> Add Customer
          </button>
        </div>
      </div>

      <div class="content-card">
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Customer Name</th>
                <th>Phone / Username</th>
                <th>Email Address</th>
                <th>Assigned Meter</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="customer-table-body">
              <!-- Filled by JS -->
            </tbody>
          </table>
        </div>
      </div>
    `;

    const populateTable = (searchTerm = '') => {
      const tbody = document.getElementById('customer-table-body');
      
      const filtered = customers.filter(c => {
        const u = users.find(usr => usr.id === c.user_id);
        if (!u) return false;
        return u.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
               u.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
               u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
               c.phone.includes(searchTerm);
      });

      if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-muted" style="text-align:center;">No customers found.</td></tr>`;
        return;
      }

      tbody.innerHTML = filtered.map(c => {
        const u = users.find(usr => usr.id === c.user_id);
        const meter = meters.find(m => m.customer_id === c.customer_id);
        const meterText = meter ? `<span class="badge badge-info">${meter.meter_number} (${meter.utilityType})</span>` : '<span class="text-muted">None</span>';
        
        const statusVal = u.status || 'active';
        const statusBadge = statusVal === 'active' ? 
          `<span class="badge badge-success">Active</span>` : 
          `<span class="badge badge-danger">Inactive</span>`;

        return `
          <tr>
            <td>
              <div style="font-weight:600;">${u.name}</div>
              <small class="text-muted">Cust ID: ${c.customer_id}</small>
            </td>
            <td>
              <div>${c.phone}</div>
              <small class="text-muted">@${u.username}</small>
            </td>
            <td>${u.email}</td>
            <td>${meterText}</td>
            <td>${statusBadge}</td>
            <td>
              <div class="action-btn-group">
                <button class="btn-icon-only primary view-details-btn" data-id="${c.customer_id}" title="View Details">
                  <i class="fa-solid fa-eye"></i>
                </button>
                <button class="btn-icon-only edit-customer-btn" data-id="${c.customer_id}" title="Edit Customer">
                  <i class="fa-solid fa-pen"></i>
                </button>
                <button class="btn-icon-only danger status-toggle-btn" data-id="${u.id}" title="${statusVal === 'active' ? 'Deactivate' : 'Activate'}">
                  <i class="fa-solid ${statusVal === 'active' ? 'fa-user-slash' : 'fa-user-check'}"></i>
                </button>
                <button class="btn-icon-only danger delete-customer-btn" data-id="${c.customer_id}" title="Delete Customer">
                  <i class="fa-solid fa-trash-can"></i>
                </button>
              </div>
            </td>
          </tr>
        `;
      }).join('');

      // Add actions event listeners
      tbody.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', () => this.showCustomerDetails(btn.dataset.id, openModal, closeModal));
      });

      tbody.querySelectorAll('.edit-customer-btn').forEach(btn => {
        btn.addEventListener('click', () => this.showEditCustomerModal(btn.dataset.id, openModal, closeModal, showToast, () => {
          this.renderList(container, showToast, openModal, closeModal);
        }));
      });

      tbody.querySelectorAll('.status-toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const uId = btn.dataset.id;
          const uList = getAll('users');
          const target = uList.find(usr => usr.id === uId);
          const currentStatus = target.status || 'active';
          const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
          update('users', uId, { status: newStatus });
          showToast(`User status updated to ${newStatus}`, 'success');
          this.renderList(container, showToast, openModal, closeModal);
        });
      });

      tbody.querySelectorAll('.delete-customer-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.showDeleteCustomerModal(btn.dataset.id, openModal, closeModal, showToast, () => {
            this.renderList(container, showToast, openModal, closeModal);
          });
        });
      });
    };

    populateTable();

    // Search bar event
    document.getElementById('customer-search').addEventListener('input', (e) => {
      populateTable(e.target.value);
    });

    // Add Customer button event
    document.getElementById('add-customer-btn').addEventListener('click', () => {
      this.showAddCustomerModal(openModal, closeModal, showToast, () => {
        this.renderList(container, showToast, openModal, closeModal);
      });
    });
  },

  showCustomerDetails(customerId, openModal, closeModal) {
    const customer = getAll('customers').find(c => c.customer_id === customerId);
    const user = getAll('users').find(u => u.id === customer.user_id);
    const meters = getAll('meters');
    const bills = getAll('bills').filter(b => b.customer_id === customerId);

    const meter = meters.find(m => m.customer_id === customerId);
    const unpaidBills = bills.filter(b => b.status === 'unpaid' || b.status === 'overdue');
    const unpaidAmount = unpaidBills.reduce((sum, b) => sum + b.amount, 0);

    const modalHtml = `
      <div class="modal-header">
        <h2>Customer Profile Details</h2>
      </div>
      <div style="display:flex; flex-direction:column; gap:20px;">
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; background:var(--bg-tertiary); padding:16px; border-radius:8px; border:1px solid var(--border-color)">
          <div>
            <div class="text-muted" style="font-size:0.75rem;">FULL NAME</div>
            <div style="font-weight:600; font-size:1.1rem;">${user.name}</div>
          </div>
          <div>
            <div class="text-muted" style="font-size:0.75rem;">USERNAME / ID</div>
            <div>${user.username} (${customer.customer_id})</div>
          </div>
          <div style="margin-top:10px;">
            <div class="text-muted" style="font-size:0.75rem;">EMAIL</div>
            <div>${user.email}</div>
          </div>
          <div style="margin-top:10px;">
            <div class="text-muted" style="font-size:0.75rem;">PHONE</div>
            <div>${customer.phone}</div>
          </div>
          <div style="margin-top:10px; grid-column: span 2;">
            <div class="text-muted" style="font-size:0.75rem;">ADDRESS</div>
            <div>${customer.address}</div>
          </div>
        </div>

        <div>
          <h3 style="font-size:1rem; margin-bottom:10px;"><i class="fa-solid fa-gauge-high"></i> Linked Meter Info</h3>
          ${meter ? `
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; background:var(--bg-tertiary); padding:12px; border-radius:8px; border:1px solid var(--border-color)">
              <div><strong>Meter Number:</strong> ${meter.meter_number}</div>
              <div><strong>Utility Type:</strong> ${meter.utilityType.toUpperCase()}</div>
              <div><strong>Status:</strong> <span class="badge badge-${meter.status === 'active' ? 'success' : 'warning'}">${meter.status}</span></div>
              <div><strong>Installation Date:</strong> ${meter.installDate}</div>
            </div>
          ` : `<p class="text-muted">No meter linked to this customer.</p>`}
        </div>

        <div>
          <h3 style="font-size:1rem; margin-bottom:10px;"><i class="fa-solid fa-file-invoice-dollar"></i> Billing & Account Balance</h3>
          <div style="display:flex; gap:24px; margin-bottom:15px;">
            <div>
              <div class="text-muted" style="font-size:0.8rem;">Total Bills Generated</div>
              <div style="font-weight:700; font-size:1.2rem;">${bills.length}</div>
            </div>
            <div>
              <div class="text-muted" style="font-size:0.8rem;">Unpaid Outstandings</div>
              <div style="font-weight:700; font-size:1.2rem; color:var(--danger)">৳${unpaidAmount.toLocaleString()}</div>
            </div>
          </div>

          <div class="table-responsive" style="max-height: 200px;">
            <table class="data-table" style="font-size:0.8rem;">
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Amount</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                ${bills.length === 0 ? `<tr><td colspan="3" class="text-muted text-center" style="text-align:center;">No bills found.</td></tr>` : 
                  bills.map(b => `
                    <tr>
                      <td>${b.billingMonth} ${b.billingYear}</td>
                      <td>৳${b.amount}</td>
                      <td><span class="badge badge-${b.status === 'paid' ? 'success' : 'danger'}">${b.status}</span></td>
                    </tr>
                  `).join('')
                }
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" id="close-detail-modal">Close</button>
      </div>
    `;

    openModal(modalHtml, () => {
      document.getElementById('close-detail-modal').addEventListener('click', closeModal);
    });
  },

  showAddCustomerModal(openModal, closeModal, showToast, refreshCallback) {
    const meters = getAll('meters');

    const modalHtml = `
      <div class="modal-header">
        <h2>Register New Customer</h2>
      </div>
      <form id="add-customer-form">
        <div class="form-group">
          <label for="new-fullname">Full Name</label>
          <input type="text" id="new-fullname" placeholder="e.g. Abul Hasan" required>
        </div>
        <div class="form-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
          <div>
            <label for="new-username">Username</label>
            <input type="text" id="new-username" placeholder="e.g. abul_h" required>
          </div>
          <div>
            <label for="new-phone">Phone Number</label>
            <input type="text" id="new-phone" placeholder="017XXXXXXXX" required>
          </div>
        </div>
        <div class="form-group">
          <label for="new-email">Email Address</label>
          <input type="email" id="new-email" placeholder="e.g. abul@gmail.com" required>
        </div>
        <div class="form-group">
          <label for="new-password">Password</label>
          <input type="password" id="new-password" placeholder="••••••••" required>
        </div>
        <div class="form-group">
          <label for="new-address">Home Address</label>
          <input type="text" id="new-address" placeholder="e.g. House 42, Road 5, Sector 3, Uttara" required>
        </div>
        <div class="form-group">
          <label for="new-meter">Assign Meter (Optional)</label>
          <select id="new-meter">
            <option value="">-- No Meter --</option>
            ${meters.map(m => {
              const assignedCust = m.customer_id ? getAll('customers').find(c => c.customer_id === m.customer_id) : null;
              const assignedUser = assignedCust ? getAll('users').find(u => u.id === assignedCust.user_id) : null;
              const suffix = assignedUser ? ` [Assigned to ${assignedUser.name}]` : ' [Free]';
              return `<option value="${m.meter_id}">${m.meter_number} (${m.utilityType.toUpperCase()})${suffix}</option>`;
            }).join('')}
          </select>
        </div>
        
        <div style="margin-bottom: 20px;">
          <label style="display:flex; align-items:center; gap:8px; cursor:pointer; font-weight:500; color:var(--primary);">
            <input type="checkbox" id="create-new-meter-check"> Create and link a brand new meter instead
          </label>
        </div>
        
        <div id="new-meter-creation-fields" class="hidden" style="background:var(--bg-tertiary); padding:16px; border-radius:8px; border:1px solid var(--border-hover); margin-bottom:20px;">
          <div class="form-group">
            <label for="direct-meter-serial">New Meter Number</label>
            <input type="text" id="direct-meter-serial" placeholder="MET-XXXXXX">
          </div>
          <div class="form-group" style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
            <div>
              <label for="direct-meter-type">Utility Type</label>
              <select id="direct-meter-type">
                <option value="electricity">Electricity (kWh)</option>
                <option value="water">Water (m³)</option>
                <option value="gas">Gas (m³)</option>
                <option value="wifi">WiFi (Mbps)</option>
              </select>
            </div>
            <div>
              <label for="direct-meter-reading">Initial Reading</label>
              <input type="number" id="direct-meter-reading" min="0" value="0">
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" id="cancel-add-btn">Cancel</button>
          <button type="submit" class="btn btn-primary">Create Customer</button>
        </div>
      </form>
    `;

    openModal(modalHtml, () => {
      document.getElementById('cancel-add-btn').addEventListener('click', closeModal);

      const meterCheck = document.getElementById('create-new-meter-check');
      const creationFields = document.getElementById('new-meter-creation-fields');
      const existingMeterSelect = document.getElementById('new-meter');

      meterCheck.addEventListener('change', () => {
        if (meterCheck.checked) {
          creationFields.classList.remove('hidden');
          existingMeterSelect.disabled = true;
          document.getElementById('direct-meter-serial').required = true;
        } else {
          creationFields.classList.add('hidden');
          existingMeterSelect.disabled = false;
          document.getElementById('direct-meter-serial').required = false;
        }
      });

      document.getElementById('add-customer-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const name = document.getElementById('new-fullname').value;
        const username = document.getElementById('new-username').value;
        const phone = document.getElementById('new-phone').value;
        const email = document.getElementById('new-email').value;
        const password = document.getElementById('new-password').value;
        const address = document.getElementById('new-address').value;
        
        const createDirectMeter = meterCheck.checked;
        let meterId = existingMeterSelect.value;

        const usersList = getAll('users');
        if (usersList.some(u => u.username === username)) {
          showToast('Username is already taken.', 'danger');
          return;
        }

        // 1. Create User
        const newUser = {
          name,
          username,
          email,
          password,
          role: 'customer',
          status: 'active'
        };
        const createdUser = add('users', newUser);

        // 2. Create Customer Profile
        const newCustomer = {
          user_id: createdUser.id,
          phone,
          address
        };
        const createdCustomer = add('customers', newCustomer);

        // 3. Update Meter if assigned
        if (createDirectMeter) {
          const directSerial = document.getElementById('direct-meter-serial').value.trim().toUpperCase();
          const directType = document.getElementById('direct-meter-type').value;
          const directReading = parseInt(document.getElementById('direct-meter-reading').value, 10) || 0;

          if (!directSerial) {
            showToast('Please provide a meter serial number.', 'danger');
            return;
          }

          const allMeters = getAll('meters');
          if (allMeters.some(m => m.meter_number === directSerial)) {
            showToast('Meter Number already exists.', 'danger');
            return;
          }

          const newMeterObj = add('meters', {
            meter_number: directSerial,
            utilityType: directType,
            installDate: new Date().toISOString().split('T')[0],
            customer_id: createdCustomer.customer_id,
            status: 'active'
          });

          add('meter_readings', {
            meter_id: newMeterObj.meter_id,
            month: 'Initial',
            unit_consumed: directReading
          });

          addNotification(createdUser.id, `Meter ${directSerial} has been created and assigned to your account.`, 'success');
        } else if (meterId) {
          update('meters', meterId, { customer_id: createdCustomer.customer_id });
          addNotification(createdUser.id, `Meter number has been assigned to your account.`, 'success');
        }

        showToast('Customer profile registered successfully.', 'success');
        closeModal();
        refreshCallback();
      });
    });
  },

  showEditCustomerModal(customerId, openModal, closeModal, showToast, refreshCallback) {
    const customer = getAll('customers').find(c => c.customer_id === customerId);
    const user = getAll('users').find(u => u.id === customer.user_id);
    const meters = getAll('meters');
    const currentMeter = meters.find(m => m.customer_id === customerId);

    const modalHtml = `
      <div class="modal-header">
        <h2>Edit Customer Profile</h2>
      </div>
      <form id="edit-customer-form">
        <div class="form-group">
          <label for="edit-fullname">Full Name</label>
          <input type="text" id="edit-fullname" value="${user.name}" required>
        </div>
        <div class="form-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
          <div>
            <label>Username</label>
            <input type="text" value="${user.username}" disabled style="opacity:0.7;">
          </div>
          <div>
            <label for="edit-phone">Phone Number</label>
            <input type="text" id="edit-phone" value="${customer.phone}" required>
          </div>
        </div>
        <div class="form-group">
          <label for="edit-email">Email Address</label>
          <input type="email" id="edit-email" value="${user.email}" required>
        </div>
        <div class="form-group">
          <label for="edit-address">Home Address</label>
          <input type="text" id="edit-address" value="${customer.address}" required>
        </div>
        <div class="form-group">
          <label for="edit-meter">Assign/Change Meter</label>
          <select id="edit-meter">
            <option value="">-- No Meter --</option>
            ${currentMeter ? `<option value="${currentMeter.meter_id}" selected>${currentMeter.meter_number} (${currentMeter.utilityType.toUpperCase()}) [Current]</option>` : ''}
            ${meters.filter(m => m.customer_id !== customerId).map(m => {
              const assignedCust = m.customer_id ? getAll('customers').find(c => c.customer_id === m.customer_id) : null;
              const assignedUser = assignedCust ? getAll('users').find(u => u.id === assignedCust.user_id) : null;
              const suffix = assignedUser ? ` [Assigned to ${assignedUser.name}]` : ' [Free]';
              return `<option value="${m.meter_id}">${m.meter_number} (${m.utilityType.toUpperCase()})${suffix}</option>`;
            }).join('')}
          </select>
        </div>

        <div style="margin-bottom: 20px;">
          <label style="display:flex; align-items:center; gap:8px; cursor:pointer; font-weight:500; color:var(--primary);">
            <input type="checkbox" id="edit-create-new-meter-check"> Create and link a brand new meter instead
          </label>
        </div>
        
        <div id="edit-new-meter-creation-fields" class="hidden" style="background:var(--bg-tertiary); padding:16px; border-radius:8px; border:1px solid var(--border-hover); margin-bottom:20px;">
          <div class="form-group">
            <label for="edit-direct-meter-serial">New Meter Number</label>
            <input type="text" id="edit-direct-meter-serial" placeholder="MET-XXXXXX">
          </div>
          <div class="form-group" style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
            <div>
              <label for="edit-direct-meter-type">Utility Type</label>
              <select id="edit-direct-meter-type">
                <option value="electricity">Electricity (kWh)</option>
                <option value="water">Water (m³)</option>
                <option value="gas">Gas (m³)</option>
                <option value="wifi">WiFi (Mbps)</option>
              </select>
            </div>
            <div>
              <label for="edit-direct-meter-reading">Initial Reading</label>
              <input type="number" id="edit-direct-meter-reading" min="0" value="0">
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" id="cancel-edit-btn">Cancel</button>
          <button type="submit" class="btn btn-primary">Save Changes</button>
        </div>
      </form>
    `;

    openModal(modalHtml, () => {
      document.getElementById('cancel-edit-btn').addEventListener('click', closeModal);

      const editMeterCheck = document.getElementById('edit-create-new-meter-check');
      const editCreationFields = document.getElementById('edit-new-meter-creation-fields');
      const editMeterSelect = document.getElementById('edit-meter');

      editMeterCheck.addEventListener('change', () => {
        if (editMeterCheck.checked) {
          editCreationFields.classList.remove('hidden');
          editMeterSelect.disabled = true;
          document.getElementById('edit-direct-meter-serial').required = true;
        } else {
          editCreationFields.classList.add('hidden');
          editMeterSelect.disabled = false;
          document.getElementById('edit-direct-meter-serial').required = false;
        }
      });

      document.getElementById('edit-customer-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const name = document.getElementById('edit-fullname').value.trim();
        const phone = document.getElementById('edit-phone').value.trim();
        const email = document.getElementById('edit-email').value.trim();
        const address = document.getElementById('edit-address').value.trim();
        
        const createDirectMeter = editMeterCheck.checked;
        const newMeterId = editMeterSelect.value;

        // 1. Update User Record
        update('users', user.id, { name, email });

        // 2. Update Customer Record
        update('customers', customerId, { phone, address });

        // 3. Update Meter Connections
        if (createDirectMeter) {
          const directSerial = document.getElementById('edit-direct-meter-serial').value.trim().toUpperCase();
          const directType = document.getElementById('edit-direct-meter-type').value;
          const directReading = parseInt(document.getElementById('edit-direct-meter-reading').value, 10) || 0;

          if (!directSerial) {
            showToast('Please provide a meter serial number.', 'danger');
            return;
          }

          const allMeters = getAll('meters');
          if (allMeters.some(m => m.meter_number === directSerial)) {
            showToast('Meter Number already exists.', 'danger');
            return;
          }

          // Unassign old meter if it existed
          const oldMeterId = currentMeter ? currentMeter.meter_id : null;
          if (oldMeterId) {
            update('meters', oldMeterId, { customer_id: null });
          }

          // Create and assign new meter
          const newMeterObj = add('meters', {
            meter_number: directSerial,
            utilityType: directType,
            installDate: new Date().toISOString().split('T')[0],
            customer_id: customerId,
            status: 'active'
          });

          add('meter_readings', {
            meter_id: newMeterObj.meter_id,
            month: 'Initial',
            unit_consumed: directReading
          });

          addNotification(user.id, `Meter ${directSerial} has been created and assigned to your account.`, 'success');
        } else {
          const oldMeterId = currentMeter ? currentMeter.meter_id : null;
          if (oldMeterId !== newMeterId) {
            // Unassign old meter if it existed
            if (oldMeterId) {
              update('meters', oldMeterId, { customer_id: null });
            }

            // Assign new meter if selected
            if (newMeterId) {
              update('meters', newMeterId, { customer_id: customerId });
            }
          }
        }

        showToast('Customer profile updated successfully.', 'success');
        closeModal();
        refreshCallback();
      });
    });
  },

  showDeleteCustomerModal(customerId, openModal, closeModal, showToast, refreshCallback) {
    const customer = getAll('customers').find(c => c.customer_id === customerId);
    const user = getAll('users').find(u => u.id === customer.user_id);

    const modalHtml = `
      <div class="modal-header">
        <h2 class="text-danger"><i class="fa-solid fa-triangle-exclamation"></i> Delete Customer Account?</h2>
      </div>
      <div style="font-size:0.9rem; line-height:1.5; margin-bottom:24px;">
        <p>Are you sure you want to permanently delete the customer account for <strong>${user.name}</strong> (@${user.username})?</p>
        <p class="text-muted" style="margin-top:12px; font-size:0.8rem;">This action will delete both the login user credentials and their customer profile record. Any assigned meters will be automatically unlinked.</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" id="cancel-delete-btn">Cancel</button>
        <button class="btn btn-danger" id="confirm-delete-btn">Confirm Delete</button>
      </div>
    `;

    openModal(modalHtml, () => {
      document.getElementById('cancel-delete-btn').addEventListener('click', closeModal);
      
      document.getElementById('confirm-delete-btn').addEventListener('click', () => {
        // 1. Remove User Account
        remove('users', user.id);

        // 2. Remove Customer Profile
        remove('customers', customerId);

        // 3. Unassign Meters
        const metersList = getAll('meters');
        const updatedMeters = metersList.map(m => {
          if (m.customer_id === customerId) {
            m.customer_id = null;
          }
          return m;
        });
        localStorage.setItem('utilis_db_meters', JSON.stringify(updatedMeters));

        showToast(`Customer account for ${user.name} has been deleted.`, 'warning');
        closeModal();
        refreshCallback();
      });
    });
  }
};
