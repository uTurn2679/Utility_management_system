import { getAll, add, update, addNotification } from '../db.js';

export const MaintenanceView = {
  render(container, user, showToast, openModal, closeModal) {
    if (user.role === 'customer') {
      this.renderCustomerView(container, user, showToast, openModal, closeModal);
    } else {
      this.renderStaffView(container, user, showToast, openModal, closeModal);
    }
  },

  renderCustomerView(container, user, showToast, openModal, closeModal) {
    const requests = getAll('maintenance').filter(r => r.customer_id === user.customerId);

    container.innerHTML = `
      <div class="filter-row">
        <h2>Maintenance Requests</h2>
        <button class="btn btn-primary" id="new-request-btn">
          <i class="fa-solid fa-screwdriver-wrench"></i> Lodge New Request
        </button>
      </div>

      <div class="content-card">
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Description</th>
                <th>Filed Date</th>
                <th>Status</th>
                <th>Assigned Technician</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody id="maintenance-body">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
    `;

    const tbody = document.getElementById('maintenance-body');
    if (requests.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-muted" style="text-align:center; padding: 20px;">No maintenance requests filed yet.</td></tr>`;
    } else {
      tbody.innerHTML = requests.reverse().map(r => {
        const tech = r.assigned_to ? getAll('users').find(u => u.id === r.assigned_to) : null;
        const techText = tech ? tech.name : '<span class="text-muted">Unassigned</span>';
        
        let typeIcon = 'fa-circle-question';
        let typeColor = 'var(--primary)';
        if (r.request_type === 'Meter Problem') { typeIcon = 'fa-gauge-high'; typeColor = '#00f2fe'; }
        else if (r.request_type === 'Line Problem') { typeIcon = 'fa-plug'; typeColor = '#f5af19'; }
        else if (r.request_type === 'Water Leakage') { typeIcon = 'fa-droplet'; typeColor = '#3a7bd5'; }
        else if (r.request_type === 'Gas Leakage') { typeIcon = 'fa-fire'; typeColor = '#f857a6'; }

        let badgeClass = 'danger';
        if (r.status === 'resolved') badgeClass = 'success';
        if (r.status === 'assigned') badgeClass = 'warning';

        return `
          <tr>
            <td>
              <span style="display:flex; align-items:center; gap:8px;">
                <i class="fa-solid ${typeIcon}" style="color:${typeColor}; font-size:1.1rem;"></i>
                <strong>${r.request_type}</strong>
              </span>
            </td>
            <td><span class="text-muted">${r.description.substring(0, 50)}${r.description.length > 50 ? '...' : ''}</span></td>
            <td>${r.createdAt}</td>
            <td><span class="badge badge-${badgeClass}">${r.status.toUpperCase()}</span></td>
            <td>${techText}</td>
            <td>
              <button class="btn btn-secondary view-request-btn" data-id="${r.maintenance_id}" style="padding:6px 12px; font-size:0.75rem;">
                View Details
              </button>
            </td>
          </tr>
        `;
      }).join('');

      tbody.querySelectorAll('.view-request-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.showDetailsModal(btn.dataset.id, user, openModal, closeModal, showToast, () => {
            this.renderCustomerView(container, user, showToast, openModal, closeModal);
          });
        });
      });
    }

    document.getElementById('new-request-btn').addEventListener('click', () => {
      this.showLodgeModal(user, openModal, closeModal, showToast, () => {
        this.renderCustomerView(container, user, showToast, openModal, closeModal);
      });
    });
  },

  renderStaffView(container, user, showToast, openModal, closeModal) {
    const list = getAll('maintenance');
    const customers = getAll('customers');
    const users = getAll('users');

    // Employees (Technicians) only see their assigned requests, Admins see all
    const filteredList = user.role === 'employee' ? list.filter(r => r.assigned_to === user.id) : list;

    container.innerHTML = `
      <div class="filter-row">
        <div class="search-wrapper">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input type="text" id="maintenance-search" placeholder="Search by customer name...">
        </div>
        <div class="filter-actions">
          <select id="maintenance-status-filter">
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="assigned">Assigned</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      <div class="content-card">
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Request Type</th>
                <th>Details</th>
                <th>Date Filed</th>
                <th>Status</th>
                <th>Assigned Technician</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody id="staff-maintenance-body">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
    `;

    const populateTable = () => {
      const searchTerm = document.getElementById('maintenance-search').value.toLowerCase();
      const statusFilter = document.getElementById('maintenance-status-filter').value;
      const tbody = document.getElementById('staff-maintenance-body');

      const filtered = filteredList.filter(r => {
        const customer = customers.find(c => c.customer_id === r.customer_id);
        const custUser = customer ? users.find(u => u.id === customer.user_id) : null;
        const matchesSearch = custUser ? custUser.name.toLowerCase().includes(searchTerm) : false;
        const matchesStatus = statusFilter === '' || r.status === statusFilter;
        return matchesSearch && matchesStatus;
      }).reverse();

      if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-muted" style="text-align:center; padding:20px;">No maintenance requests found.</td></tr>`;
        return;
      }

      tbody.innerHTML = filtered.map(r => {
        const customer = customers.find(c => c.customer_id === r.customer_id);
        const custUser = customer ? users.find(u => u.id === customer.user_id) : null;
        const tech = r.assigned_to ? users.find(u => u.id === r.assigned_to) : null;
        const techText = tech ? tech.name : '<span class="text-muted">Unassigned</span>';

        let typeIcon = 'fa-circle-question';
        let typeColor = 'var(--primary)';
        if (r.request_type === 'Meter Problem') { typeIcon = 'fa-gauge-high'; typeColor = '#00f2fe'; }
        else if (r.request_type === 'Line Problem') { typeIcon = 'fa-plug'; typeColor = '#f5af19'; }
        else if (r.request_type === 'Water Leakage') { typeIcon = 'fa-droplet'; typeColor = '#3a7bd5'; }
        else if (r.request_type === 'Gas Leakage') { typeIcon = 'fa-fire'; typeColor = '#f857a6'; }

        let badgeClass = 'danger';
        if (r.status === 'resolved') badgeClass = 'success';
        if (r.status === 'assigned') badgeClass = 'warning';

        return `
          <tr>
            <td>
              <strong>${custUser ? custUser.name : 'Unknown'}</strong><br>
              <small class="text-muted">Cust ID: ${r.customer_id}</small>
            </td>
            <td>
              <span style="display:flex; align-items:center; gap:8px;">
                <i class="fa-solid ${typeIcon}" style="color:${typeColor}; font-size:1.1rem;"></i>
                <strong>${r.request_type}</strong>
              </span>
            </td>
            <td><span class="text-muted">${r.description.substring(0, 50)}${r.description.length > 50 ? '...' : ''}</span></td>
            <td>${r.createdAt}</td>
            <td><span class="badge badge-${badgeClass}">${r.status.toUpperCase()}</span></td>
            <td>${techText}</td>
            <td>
              <button class="btn btn-secondary view-request-btn" data-id="${r.maintenance_id}" style="padding:6px 12px; font-size:0.75rem;">
                Manage
              </button>
            </td>
          </tr>
        `;
      }).join('');

      tbody.querySelectorAll('.view-request-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.showDetailsModal(btn.dataset.id, user, openModal, closeModal, showToast, () => {
            this.renderStaffView(container, user, showToast, openModal, closeModal);
          });
        });
      });
    };

    populateTable();
    document.getElementById('maintenance-search').addEventListener('input', populateTable);
    document.getElementById('maintenance-status-filter').addEventListener('change', populateTable);
  },

  showLodgeModal(user, openModal, closeModal, showToast, refreshCallback) {
    const modalHtml = `
      <div class="modal-header">
        <h2>Lodge Maintenance Request</h2>
      </div>
      <form id="lodge-maintenance-form">
        <div class="form-group">
          <label for="maintenance-type">Request Type</label>
          <select id="maintenance-type" required>
            <option value="Meter Problem">Meter Problem</option>
            <option value="Line Problem">Line Problem</option>
            <option value="Water Leakage">Water Leakage</option>
            <option value="Gas Leakage">Gas Leakage</option>
          </select>
        </div>
        <div class="form-group">
          <label for="maintenance-desc">Description / Details</label>
          <textarea id="maintenance-desc" rows="4" placeholder="Explain the maintenance issue in detail..." required></textarea>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" id="cancel-maintenance-btn">Cancel</button>
          <button type="submit" class="btn btn-primary">Submit Request</button>
        </div>
      </form>
    `;

    openModal(modalHtml, () => {
      document.getElementById('cancel-maintenance-btn').addEventListener('click', closeModal);

      document.getElementById('lodge-maintenance-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const type = document.getElementById('maintenance-type').value;
        const desc = document.getElementById('maintenance-desc').value;

        add('maintenance', {
          customer_id: user.customerId,
          request_type: type,
          description: desc,
          status: 'pending',
          assigned_to: null,
          createdAt: new Date().toISOString().split('T')[0],
          comments: []
        });

        // Notify Admins
        getAll('users').filter(u => u.role === 'admin').forEach(adm => {
          addNotification(adm.id, `New maintenance request (${type}) from ${user.name}`, 'warning');
        });

        showToast('Maintenance request lodged successfully', 'success');
        closeModal();
        refreshCallback();
      });
    });
  },

  showDetailsModal(id, user, openModal, closeModal, showToast, refreshCallback) {
    const req = getAll('maintenance').find(r => r.maintenance_id === id);
    const customer = getAll('customers').find(c => c.customer_id === req.customer_id);
    const custUser = customer ? getAll('users').find(u => u.id === customer.user_id) : null;
    const technicians = getAll('users').filter(u => u.role === 'employee');

    const modalHtml = `
      <div class="modal-header">
        <h2>Maintenance Request Details</h2>
      </div>
      <div style="font-size:0.85rem; display:flex; flex-direction:column; gap:16px; max-height:70vh; overflow-y:auto;">
        <div style="background:var(--bg-tertiary); padding:16px; border-radius:8px; border:1px solid var(--border-color)">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <span class="badge badge-info">${req.request_type}</span>
            <span class="badge badge-${req.status === 'resolved' ? 'success' : req.status === 'assigned' ? 'warning' : 'danger'}">${req.status.toUpperCase()}</span>
          </div>
          <p style="color:var(--text-secondary); line-height:1.4; margin-bottom:12px;">${req.description}</p>
          <div style="font-size:0.75rem; color:var(--text-muted)">
            Filed by: ${custUser ? custUser.name : 'Unknown'} | Date: ${req.createdAt}
          </div>
        </div>

        ${user.role !== 'customer' ? `
          <form id="update-maintenance-form" style="display:grid; grid-template-columns:1fr 1fr; gap:12px; background:var(--bg-tertiary); padding:16px; border-radius:8px; border:1px solid var(--border-color)">
            <div>
              <label style="font-size:0.75rem; font-weight:600; color:var(--text-secondary)">Request Status</label>
              <select id="maintenance-status-select" style="padding:6px; font-size:0.8rem; margin-top:4px;">
                <option value="pending" ${req.status === 'pending' ? 'selected' : ''}>Pending</option>
                <option value="assigned" ${req.status === 'assigned' ? 'selected' : ''}>Assigned</option>
                <option value="resolved" ${req.status === 'resolved' ? 'selected' : ''}>Resolved</option>
              </select>
            </div>
            ${user.role === 'admin' ? `
              <div>
                <label style="font-size:0.75rem; font-weight:600; color:var(--text-secondary)">Assign Technician</label>
                <select id="maintenance-tech-select" style="padding:6px; font-size:0.8rem; margin-top:4px;">
                  <option value="">-- Unassigned --</option>
                  ${technicians.map(t => `
                    <option value="${t.id}" ${req.assigned_to === t.id ? 'selected' : ''}>${t.name}</option>
                  `).join('')}
                </select>
              </div>
            ` : '<div></div>'}
            <div style="grid-column:span 2; text-align:right; margin-top:8px;">
              <button type="submit" class="btn btn-primary" style="padding:6px 12px; font-size:0.75rem;">Apply Update</button>
            </div>
          </form>
        ` : ''}

        <div>
          <h4 style="font-size:0.9rem; margin-bottom:8px;"><i class="fa-solid fa-comments"></i> Logs & Activity Comments</h4>
          <div style="display:flex; flex-direction:column; gap:8px; max-height:150px; overflow-y:auto; margin-bottom:12px;" id="comments-list">
            ${(req.comments || []).length === 0 ? `<p class="text-muted" style="font-size:0.8rem; padding:8px 0;">No comments logged yet.</p>` : 
              req.comments.map(c => `
                <div style="background:rgba(255,255,255,0.02); padding:8px 12px; border-radius:6px; border:1px solid var(--border-color)">
                  <div style="display:flex; justify-content:space-between; font-size:0.75rem; font-weight:600; margin-bottom:4px;">
                    <span>${c.author}</span>
                    <span class="text-muted">${c.date}</span>
                  </div>
                  <p style="font-size:0.8rem; color:var(--text-secondary);">${c.text}</p>
                </div>
              `).join('')
            }
          </div>

          <form id="add-req-comment-form" style="display:flex; gap:8px;">
            <input type="text" id="new-req-comment-text" placeholder="Add comment/note..." required style="padding:8px 12px; font-size:0.8rem;">
            <button type="submit" class="btn btn-secondary" style="padding:8px 16px; font-size:0.8rem;">Post</button>
          </form>
        </div>
      </div>
      <div class="modal-footer" style="margin-top:20px;">
        <button class="btn btn-secondary" id="close-req-modal">Close</button>
      </div>
    `;

    openModal(modalHtml, () => {
      document.getElementById('close-req-modal').addEventListener('click', closeModal);

      // Handle comments form
      document.getElementById('add-req-comment-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const text = document.getElementById('new-req-comment-text').value.trim();
        if (!text) return;

        const newComment = {
          author: user.name,
          text,
          date: new Date().toISOString().split('T')[0]
        };

        const updatedComments = [...(req.comments || []), newComment];
        update('maintenance', id, { comments: updatedComments });
        showToast('Comment added', 'success');

        // Notify client if staff added it
        if (user.role !== 'customer' && custUser) {
          addNotification(custUser.id, `Staff comment on request: "${text.substring(0, 30)}..."`, 'info');
        }

        closeModal();
        refreshCallback();
        setTimeout(() => this.showDetailsModal(id, user, openModal, closeModal, showToast, refreshCallback), 200);
      });

      // Handle updates
      const updateForm = document.getElementById('update-maintenance-form');
      if (updateForm) {
        updateForm.addEventListener('submit', (e) => {
          e.preventDefault();
          const status = document.getElementById('maintenance-status-select').value;
          const updates = { status };

          const techSelect = document.getElementById('maintenance-tech-select');
          if (techSelect) {
            updates.assigned_to = techSelect.value || null;
            if (updates.assigned_to && updates.status === 'pending') {
              updates.status = 'assigned'; // Auto progress status
            }
          }

          update('maintenance', id, updates);
          showToast('Request updated successfully', 'success');

          // Notify customer
          if (custUser) {
            addNotification(custUser.id, `Your maintenance request status is now: ${updates.status.toUpperCase()}`, 'info');
          }

          // Notify assigned technician
          if (updates.assigned_to && updates.assigned_to !== req.assigned_to) {
            addNotification(updates.assigned_to, `New maintenance request assigned: "${req.request_type}"`, 'warning');
          }

          closeModal();
          refreshCallback();
        });
      }
    });
  }
};
