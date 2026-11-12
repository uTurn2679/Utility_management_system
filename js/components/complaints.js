import { getAll, add, update, addNotification } from '../db.js';

export const ComplaintsView = {
  render(container, user, showToast, openModal, closeModal) {
    if (user.role === 'customer') {
      this.renderCustomerComplaints(container, user, showToast, openModal, closeModal);
    } else {
      this.renderStaffComplaints(container, user, showToast, openModal, closeModal);
    }
  },

  renderCustomerComplaints(container, user, showToast, openModal, closeModal) {
    const complaints = getAll('complaints').filter(c => c.customer_id === user.customerId);

    container.innerHTML = `
      <div class="filter-row">
        <h2>My Complaints & Tickets</h2>
        <button class="btn btn-primary" id="file-complaint-btn">
          <i class="fa-solid fa-circle-plus"></i> Lodge New Complaint
        </button>
      </div>

      <div class="content-card">
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Complaint Subject</th>
                <th>Category</th>
                <th>Filed Date</th>
                <th>Status</th>
                <th>Assigned Agent</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody id="cust-complaints-body">
              <!-- Filled by JS -->
            </tbody>
          </table>
        </div>
      </div>
    `;

    const tbody = document.getElementById('cust-complaints-body');
    if (complaints.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-muted" style="text-align:center; padding: 20px;">No complaints submitted yet.</td></tr>`;
    } else {
      tbody.innerHTML = complaints.reverse().map(c => {
        const agent = c.assignedTo ? getAll('users').find(u => u.id === c.assignedTo) : null;
        const agentText = agent ? agent.name : '<span class="text-muted">Unassigned</span>';
        let badgeClass = 'warning';
        if (c.status === 'solved') badgeClass = 'success';
        if (c.status === 'pending') badgeClass = 'danger';

        return `
          <tr>
            <td><strong>${c.subject}</strong></td>
            <td><span class="badge badge-info">${(c.category || 'general').toUpperCase()}</span></td>
            <td>${c.createdAt}</td>
            <td><span class="badge badge-${badgeClass}">${c.status}</span></td>
            <td>${agentText}</td>
            <td>
              <button class="btn btn-secondary view-complaint-btn" data-id="${c.complaint_id}" style="padding:6px 12px; font-size:0.75rem;">
                View Log
              </button>
            </td>
          </tr>
        `;
      }).join('');

      tbody.querySelectorAll('.view-complaint-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.showComplaintDetailsModal(btn.dataset.id, user, openModal, closeModal, showToast, () => {
            this.renderCustomerComplaints(container, user, showToast, openModal, closeModal);
          });
        });
      });
    }

    document.getElementById('file-complaint-btn').addEventListener('click', () => {
      this.showFileComplaintModal(user, openModal, closeModal, showToast, () => {
        this.renderCustomerComplaints(container, user, showToast, openModal, closeModal);
      });
    });
  },

  renderStaffComplaints(container, user, showToast, openModal, closeModal) {
    const complaints = getAll('complaints');
    const customers = getAll('customers');
    const users = getAll('users');

    // Employees only see their assigned complaints
    const list = user.role === 'employee' ? complaints.filter(c => c.assignedTo === user.id) : complaints;

    container.innerHTML = `
      <div class="filter-row">
        <div class="search-wrapper">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input type="text" id="complaint-search" placeholder="Search complaints...">
        </div>
        <div class="filter-actions">
          <select id="complaint-status-filter">
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="solved">Solved</option>
          </select>
        </div>
      </div>

      <div class="content-card">
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Complaint Details</th>
                <th>Category</th>
                <th>Date Filed</th>
                <th>Status</th>
                <th>Assigned Agent</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody id="staff-complaints-body">
              <!-- Filled by JS -->
            </tbody>
          </table>
        </div>
      </div>
    `;

    const populateTable = () => {
      const searchTerm = document.getElementById('complaint-search').value.toLowerCase();
      const statusFilter = document.getElementById('complaint-status-filter').value;
      const tbody = document.getElementById('staff-complaints-body');

      const filtered = list.filter(c => {
        const customer = customers.find(cust => cust.customer_id === c.customer_id);
        const custUser = customer ? users.find(u => u.id === customer.user_id) : null;
        
        const matchesSearch = c.subject.toLowerCase().includes(searchTerm) || (custUser ? custUser.name.toLowerCase().includes(searchTerm) : false);
        const matchesStatus = statusFilter === '' || c.status === statusFilter;
        return matchesSearch && matchesStatus;
      }).reverse();

      if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-muted" style="text-align:center;">No complaints found.</td></tr>`;
        return;
      }

      tbody.innerHTML = filtered.map(c => {
        const customer = customers.find(cust => cust.customer_id === c.customer_id);
        const custUser = customer ? users.find(u => u.id === customer.user_id) : null;
        const agent = c.assignedTo ? users.find(u => u.id === c.assignedTo) : null;
        const agentText = agent ? agent.name : '<span class="text-muted">Unassigned</span>';

        let statusClass = 'warning';
        if (c.status === 'solved') statusClass = 'success';
        if (c.status === 'pending') statusClass = 'danger';

        return `
          <tr>
            <td>
              <strong>${custUser ? custUser.name : 'Deleted Customer'}</strong><br>
              <small class="text-muted">Cust ID: ${c.customer_id}</small>
            </td>
            <td>
              <div style="font-weight:600;">${c.subject}</div>
              <small class="text-muted">${c.description.substring(0, 50)}${c.description.length > 50 ? '...' : ''}</small>
            </td>
            <td><span class="badge badge-info">${(c.category || 'general').toUpperCase()}</span></td>
            <td>${c.createdAt}</td>
            <td><span class="badge badge-${statusClass}">${c.status}</span></td>
            <td>${agentText}</td>
            <td>
              <button class="btn btn-secondary view-complaint-btn" data-id="${c.complaint_id}" style="padding:6px 12px; font-size:0.75rem;">
                Manage
              </button>
            </td>
          </tr>
        `;
      }).join('');

      tbody.querySelectorAll('.view-complaint-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.showComplaintDetailsModal(btn.dataset.id, user, openModal, closeModal, showToast, () => {
            this.renderStaffComplaints(container, user, showToast, openModal, closeModal);
          });
        });
      });
    };

    populateTable();

    document.getElementById('complaint-search').addEventListener('input', populateTable);
    document.getElementById('complaint-status-filter').addEventListener('change', populateTable);
  },

  showFileComplaintModal(user, openModal, closeModal, showToast, refreshCallback) {
    const modalHtml = `
      <div class="modal-header">
        <h2>File Support Ticket / Complaint</h2>
      </div>
      <form id="lodge-complaint-form">
        <div class="form-group">
          <label for="complaint-title">Subject / Title</label>
          <input type="text" id="complaint-title" placeholder="e.g. Unusually high water bill" required>
        </div>
        <div class="form-group">
          <label for="complaint-cat">Category</label>
          <select id="complaint-cat" required>
            <option value="billing">Billing Dispute</option>
            <option value="meter">Meter Malfunction / Display flickering</option>
            <option value="connection">Disconnection / Connection Issues</option>
            <option value="other">Other Request</option>
          </select>
        </div>
        <div class="form-group">
          <label for="complaint-desc">Details / Description</label>
          <textarea id="complaint-desc" rows="4" placeholder="Detail your issue here..." required></textarea>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" id="cancel-lodge-btn">Cancel</button>
          <button type="submit" class="btn btn-primary">Submit Ticket</button>
        </div>
      </form>
    `;

    openModal(modalHtml, () => {
      document.getElementById('cancel-lodge-btn').addEventListener('click', closeModal);

      document.getElementById('lodge-complaint-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const subject = document.getElementById('complaint-title').value;
        const category = document.getElementById('complaint-cat').value;
        const description = document.getElementById('complaint-desc').value;

        add('complaints', {
          customer_id: user.customerId,
          subject: subject,
          category,
          description,
          status: 'pending',
          assignedTo: null,
          createdAt: new Date().toISOString().split('T')[0],
          comments: []
        });

        // Notify admins
        const usersList = getAll('users');
        usersList.filter(u => u.role === 'admin').forEach(adm => {
          addNotification(adm.id, `New ticket from ${user.name}: "${subject}"`, 'warning');
        });

        showToast('Complaint filed successfully. Support will contact you shortly.', 'success');
        closeModal();
        refreshCallback();
      });
    });
  },

  showComplaintDetailsModal(complaintId, user, openModal, closeModal, showToast, refreshCallback) {
    const complaint = getAll('complaints').find(c => c.complaint_id === complaintId);
    const customer = getAll('customers').find(c => c.customer_id === complaint.customer_id);
    const custUser = customer ? getAll('users').find(u => u.id === customer.user_id) : null;
    const employees = getAll('users').filter(u => u.role === 'employee');

    const modalHtml = `
      <div class="modal-header">
        <h2>Manage Support Ticket</h2>
      </div>
      <div style="font-size:0.85rem; display:flex; flex-direction:column; gap:16px; max-height: 70vh; overflow-y:auto;">
        <!-- Ticket Info -->
        <div style="background:var(--bg-tertiary); padding:16px; border-radius:8px; border:1px solid var(--border-color)">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <span class="badge badge-info">${(complaint.category || 'general').toUpperCase()}</span>
            <span class="badge badge-${complaint.status === 'solved' ? 'success' : complaint.status === 'processing' ? 'warning' : 'danger'}">${complaint.status}</span>
          </div>
          <h3 style="font-size:1.05rem; font-weight:700; margin-bottom:8px;">${complaint.subject}</h3>
          <p style="color:var(--text-secondary); line-height:1.4;">${complaint.description}</p>
          <div style="margin-top:12px; font-size:0.75rem; color:var(--text-muted);">
            Filed by: ${custUser ? custUser.name : 'Deleted User'} | Date: ${complaint.createdAt}
          </div>
        </div>

        <!-- Admin Only: Assignment & Status Changer -->
        ${user.role !== 'customer' ? `
          <form id="update-ticket-form" style="display:grid; grid-template-columns:1fr 1fr; gap:12px; background:var(--bg-tertiary); padding:16px; border-radius:8px; border:1px solid var(--border-color)">
            <div>
              <label style="font-size:0.75rem; font-weight:600; color:var(--text-secondary);">Ticket Status</label>
              <select id="ticket-status-select" style="padding:6px; font-size:0.8rem; margin-top:4px;">
                <option value="pending" ${complaint.status === 'pending' ? 'selected' : ''}>Pending</option>
                <option value="processing" ${complaint.status === 'processing' ? 'selected' : ''}>Processing</option>
                <option value="solved" ${complaint.status === 'solved' ? 'selected' : ''}>Solved</option>
              </select>
            </div>
            ${user.role === 'admin' ? `
              <div>
                <label style="font-size:0.75rem; font-weight:600; color:var(--text-secondary);">Assign Agent</label>
                <select id="ticket-agent-select" style="padding:6px; font-size:0.8rem; margin-top:4px;">
                  <option value="">-- Unassigned --</option>
                  ${employees.map(emp => `
                    <option value="${emp.id}" ${complaint.assignedTo === emp.id ? 'selected' : ''}>${emp.name}</option>
                  `).join('')}
                </select>
              </div>
            ` : '<div></div>'}
            <div style="grid-column: span 2; text-align:right; margin-top:8px;">
              <button type="submit" class="btn btn-primary" style="padding:6px 12px; font-size:0.75rem;">Apply Update</button>
            </div>
          </form>
        ` : ''}

        <!-- Ticket Comments/Activity -->
        <div>
          <h4 style="font-size:0.9rem; margin-bottom:8px;"><i class="fa-solid fa-comments"></i> Logs & Activity Comments</h4>
          <div style="display:flex; flex-direction:column; gap:8px; max-height:150px; overflow-y:auto; margin-bottom:12px;" id="comments-list">
            ${(complaint.comments || []).length === 0 ? `<p class="text-muted" style="font-size:0.8rem; padding:8px 0;">No comments logged yet.</p>` : 
              complaint.comments.map(c => `
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

          <!-- Add Comment Form -->
          <form id="add-comment-form" style="display:flex; gap:8px;">
            <input type="text" id="new-comment-text" placeholder="Add comment/note..." required style="padding:8px 12px; font-size:0.8rem;">
            <button type="submit" class="btn btn-secondary" style="padding:8px 16px; font-size:0.8rem;">Post</button>
          </form>
        </div>
      </div>
      <div class="modal-footer" style="margin-top:20px;">
        <button class="btn btn-secondary" id="close-ticket-modal">Close</button>
      </div>
    `;

    openModal(modalHtml, () => {
      document.getElementById('close-ticket-modal').addEventListener('click', closeModal);

      // Handle comments form
      document.getElementById('add-comment-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const text = document.getElementById('new-comment-text').value.trim();
        if (!text) return;

        const date = new Date().toISOString().split('T')[0];
        const newComment = {
          author: user.name,
          text,
          date
        };

        const updatedComments = [...(complaint.comments || []), newComment];
        update('complaints', complaintId, { comments: updatedComments });
        showToast('Comment added', 'success');

        // Notify client if staff added it
        if (user.role !== 'customer') {
          addNotification(customer.user_id, `Staff added a comment to your ticket "${complaint.subject}": "${text.substring(0, 30)}..."`, 'info');
        }

        // Close and re-open modal to refresh logs easily
        closeModal();
        refreshCallback();
        setTimeout(() => this.showComplaintDetailsModal(complaintId, user, openModal, closeModal, showToast, refreshCallback), 200);
      });

      // Handle status/agent update form
      const updateForm = document.getElementById('update-ticket-form');
      if (updateForm) {
        updateForm.addEventListener('submit', (e) => {
          e.preventDefault();
          const status = document.getElementById('ticket-status-select').value;
          const updates = { status };

          const agentSelect = document.getElementById('ticket-agent-select');
          if (agentSelect) {
            updates.assignedTo = agentSelect.value || null;
          }

          update('complaints', complaintId, updates);
          showToast('Ticket updated successfully', 'success');

          // Notify customer
          addNotification(customer.user_id, `Your ticket "${complaint.subject}" status is now: ${status.toUpperCase()}`, 'info');

          // Notify assigned employee
          if (updates.assignedTo && updates.assignedTo !== complaint.assignedTo) {
            addNotification(updates.assignedTo, `You have been assigned a new ticket: "${complaint.subject}"`, 'warning');
          }

          closeModal();
          refreshCallback();
        });
      }
    });
  }
};
