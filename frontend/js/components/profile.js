import { getAll, getById, update } from '../db.js';

export const ProfileView = {
  render(container, user, showToast) {
    const customer = getAll('customers').find(c => c.customer_id === user.customerId);
    const meter = getAll('meters').find(m => m.customer_id === user.customerId);
    
    container.innerHTML = `
      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:24px;">
        <!-- Left Side: Profile Details & Update form -->
        <div class="content-card">
          <div class="content-card-header">
            <h2><i class="fa-solid fa-user-gear"></i> Account Profile Settings</h2>
          </div>
          <form id="profile-update-form">
            <div class="form-group">
              <label>Full Name</label>
              <input type="text" value="${user.name}" disabled style="opacity:0.7;">
            </div>
            <div class="form-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
              <div>
                <label>Username</label>
                <input type="text" value="${user.username}" disabled style="opacity:0.7;">
              </div>
              <div>
                <label>Email Address</label>
                <input type="email" value="${user.email}" disabled style="opacity:0.7;">
              </div>
            </div>
            <div class="form-group">
              <label for="profile-phone">Phone Number</label>
              <input type="text" id="profile-phone" value="${customer ? customer.phone : ''}" required>
            </div>
            <div class="form-group">
              <label for="profile-address">Home Address</label>
              <input type="text" id="profile-address" value="${customer ? customer.address : ''}" required>
            </div>
            <button type="submit" class="btn btn-primary" style="margin-top:10px;">Update Profile Details</button>
          </form>
        </div>

        <!-- Right Side: Assigned Meter Parameters -->
        <div class="content-card">
          <div class="content-card-header">
            <h2><i class="fa-solid fa-gauge-high"></i> Meter Allocation Status</h2>
          </div>
          ${meter ? `
            <div style="display:flex; flex-direction:column; gap:20px; padding: 10px 0;">
              <div style="display:flex; justify-content:space-between; border-bottom: 1px solid var(--border-color); padding-bottom:12px;">
                <span class="text-secondary">Meter Serial Number:</span>
                <strong>${meter.meter_number}</strong>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom: 1px solid var(--border-color); padding-bottom:12px;">
                <span class="text-secondary">Utility Category:</span>
                <span class="badge badge-info">${meter.utilityType.toUpperCase()}</span>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom: 1px solid var(--border-color); padding-bottom:12px;">
                <span class="text-secondary">Meter Allocation Status:</span>
                <span class="badge badge-${meter.status === 'active' ? 'success' : 'warning'}">${meter.status.toUpperCase()}</span>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom: 1px solid var(--border-color); padding-bottom:12px;">
                <span class="text-secondary">Installation Date:</span>
                <span>${meter.installDate}</span>
              </div>
            </div>
          ` : `
            <div style="text-align:center; padding:60px 0; color:var(--text-muted);">
              <i class="fa-solid fa-gauge-simple-min" style="font-size:3rem; margin-bottom:16px;"></i>
              <p>No utility meter is currently assigned to this account.</p>
              <p style="font-size:0.8rem; margin-top:8px;">Please contact administration to request a connection.</p>
            </div>
          `}
        </div>
      </div>
    `;

    // Handle form submit
    const form = document.getElementById('profile-update-form');
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const phone = document.getElementById('profile-phone').value.trim();
        const address = document.getElementById('profile-address').value.trim();

        if (customer) {
          update('customers', customer.customer_id, { phone, address });
          showToast('Profile details updated successfully', 'success');
        }
      });
    }
  }
};
