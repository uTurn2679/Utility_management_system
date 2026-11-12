import { getAll, getNotificationsForUser } from '../db.js';

export const DashboardView = {
  render(container, user, showToast) {
    if (user.role === 'admin') {
      this.renderAdmin(container, user);
    } else if (user.role === 'employee') {
      this.renderEmployee(container, user);
    } else {
      this.renderCustomer(container, user);
    }
  },

  renderAdmin(container, user) {
    const customers = getAll('customers');
    const users = getAll('users');
    const activeCustomers = customers.filter(c => {
      const u = users.find(usr => usr.id === c.user_id);
      return u && u.status !== 'inactive';
    }).length;

    const meters = getAll('meters');
    const bills = getAll('bills');
    const complaints = getAll('complaints');

    // Calculate totals
    const unpaidBills = bills.filter(b => b.status === 'unpaid' || b.status === 'overdue');
    const totalUnpaidAmount = unpaidBills.reduce((sum, b) => sum + b.amount, 0);

    const paidBills = bills.filter(b => b.status === 'paid');
    const totalCollected = paidBills.reduce((sum, b) => sum + b.amount, 0);

    const pendingComplaints = complaints.filter(c => c.status === 'pending').length;

    container.innerHTML = `
      <div class="card-grid">
        <div class="metric-card">
          <div class="metric-details">
            <h3>Active Customers</h3>
            <div class="metric-val">${activeCustomers}</div>
          </div>
          <div class="metric-icon"><i class="fa-solid fa-users"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>Revenue Collected</h3>
            <div class="metric-val">৳${totalCollected.toLocaleString()}</div>
          </div>
          <div class="metric-icon"><i class="fa-solid fa-money-bill-trend-up"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>Unpaid Outstandings</h3>
            <div class="metric-val">৳${totalUnpaidAmount.toLocaleString()}</div>
          </div>
          <div class="metric-icon"><i class="fa-solid fa-file-invoice-dollar"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>Pending Complaints</h3>
            <div class="metric-val">${pendingComplaints}</div>
          </div>
          <div class="metric-icon"><i class="fa-solid fa-circle-exclamation"></i></div>
        </div>
      </div>

      <div class="chart-row">
        <div class="content-card">
          <div class="content-card-header">
            <h2><i class="fa-solid fa-chart-column"></i> Revenue vs Collection Status</h2>
          </div>
          <div class="chart-container" style="position: relative; height:300px; width:100%">
            <canvas id="revenueChart"></canvas>
          </div>
        </div>

        <div class="content-card">
          <div class="content-card-header">
            <h2><i class="fa-solid fa-gauge"></i> Meter Categories</h2>
          </div>
          <div class="utility-summary-list">
            <div class="utility-summary-item electricity">
              <div class="info">
                <div class="icon"><i class="fa-solid fa-bolt"></i></div>
                <div class="details">
                  <h4>Electricity</h4>
                  <span>Active Meters</span>
                </div>
              </div>
              <div class="value">
                <h5>${meters.filter(m => m.utilityType === 'electricity').length}</h5>
              </div>
            </div>
            <div class="utility-summary-item water">
              <div class="info">
                <div class="icon"><i class="fa-solid fa-droplet"></i></div>
                <div class="details">
                  <h4>Water</h4>
                  <span>Active Meters</span>
                </div>
              </div>
              <div class="value">
                <h5>${meters.filter(m => m.utilityType === 'water').length}</h5>
              </div>
            </div>
            <div class="utility-summary-item gas">
              <div class="info">
                <div class="icon"><i class="fa-solid fa-fire"></i></div>
                <div class="details">
                  <h4>Natural Gas</h4>
                  <span>Active Meters</span>
                </div>
              </div>
              <div class="value">
                <h5>${meters.filter(m => m.utilityType === 'gas').length}</h5>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    // Initialize Chart.js
    setTimeout(() => {
      const ctx = document.getElementById('revenueChart').getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Paid Bills', 'Unpaid Bills'],
          datasets: [{
            label: 'Amount (BDT ৳)',
            data: [totalCollected, totalUnpaidAmount],
            backgroundColor: ['#10b981', '#ef4444'],
            borderColor: ['#10b981', '#ef4444'],
            borderWidth: 1,
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#94a3b8' }
            },
            x: {
              grid: { display: false },
              ticks: { color: '#94a3b8' }
            }
          }
        }
      });
    }, 50);
  },

  renderEmployee(container, user) {
    const meters = getAll('meters');
    const complaints = getAll('complaints');
    const assignedComplaints = complaints.filter(c => c.assignedTo === user.id);
    const activeMeters = meters.filter(m => m.status === 'active').length;

    container.innerHTML = `
      <div class="card-grid">
        <div class="metric-card">
          <div class="metric-details">
            <h3>Meters Registered</h3>
            <div class="metric-val">${meters.length}</div>
          </div>
          <div class="metric-icon"><i class="fa-solid fa-gauge-high"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>Active Meters</h3>
            <div class="metric-val">${activeMeters}</div>
          </div>
          <div class="metric-icon"><i class="fa-solid fa-circle-check"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>Assigned Complaints</h3>
            <div class="metric-val">${assignedComplaints.length}</div>
          </div>
          <div class="metric-icon"><i class="fa-solid fa-list-check"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>Pending Tasks</h3>
            <div class="metric-val">${assignedComplaints.filter(c => c.status !== 'resolved').length}</div>
          </div>
          <div class="metric-icon"><i class="fa-solid fa-clock-rotate-left"></i></div>
        </div>
      </div>

      <div class="chart-row" style="grid-template-columns: 1fr;">
        <div class="content-card">
          <div class="content-card-header">
            <h2><i class="fa-solid fa-clock-rotate-left"></i> Assigned Complaints Status</h2>
          </div>
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Topic</th>
                  <th>Customer</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                ${assignedComplaints.length === 0 ? `<tr><td colspan="5" class="text-muted text-center" style="text-align:center;">No complaints assigned.</td></tr>` : 
                  assignedComplaints.map(c => {
                    const custRecord = getAll('customers').find(cr => cr.customer_id === c.customer_id);
                    const cust = custRecord ? getAll('users').find(u => u.id === custRecord.user_id) : null;
                    return `
                      <tr>
                        <td><strong>${c.subject}</strong></td>
                        <td>${cust ? cust.name : 'Unknown'}</td>
                        <td>${c.createdAt}</td>
                        <td><span class="badge badge-${c.status === 'resolved' ? 'success' : c.status === 'in-progress' ? 'warning' : 'danger'}">${c.status}</span></td>
                        <td><a href="#/complaints" class="btn btn-secondary" style="padding: 4px 8px; font-size: 0.8rem;">View Details</a></td>
                      </tr>
                    `;
                  }).join('')
                }
              </tbody>
            </table>
          </div>
        </div>
      </div>
    `;
  },

  renderCustomer(container, user) {
    const meters = getAll('meters');
    const bills = getAll('bills').filter(b => b.customer_id === user.customerId);
    const complaints = getAll('complaints').filter(c => c.customer_id === user.customerId);
    const readings = getAll('meter_readings');

    const userMeter = meters.find(m => m.customer_id === user.customerId);
    const meterReadings = userMeter ? readings.filter(r => r.meter_id === userMeter.meter_id) : [];
    const currentReading = meterReadings.length > 0 ? Math.max(...meterReadings.map(r => r.unit_consumed)) : 0;

    const unpaidBills = bills.filter(b => b.status === 'unpaid' || b.status === 'overdue');
    const totalDue = unpaidBills.reduce((sum, b) => sum + b.amount, 0);

    container.innerHTML = `
      <div class="card-grid">
        <div class="metric-card">
          <div class="metric-details">
            <h3>My Meter Status</h3>
            <div class="metric-val">${userMeter ? userMeter.status.toUpperCase() : 'N/A'}</div>
          </div>
          <div class="metric-icon"><i class="fa-solid fa-gauge-high"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>Current Reading</h3>
            <div class="metric-val">${currentReading} ${userMeter ? (userMeter.utilityType === 'electricity' ? 'kWh' : 'm³') : ''}</div>
          </div>
          <div class="metric-icon"><i class="fa-solid fa-chart-line"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>Outstanding Bills</h3>
            <div class="metric-val">৳${totalDue.toLocaleString()}</div>
          </div>
          <div class="metric-icon"><i class="fa-solid fa-wallet"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>My Complaints</h3>
            <div class="metric-val">${complaints.length}</div>
          </div>
          <div class="metric-icon"><i class="fa-solid fa-circle-question"></i></div>
        </div>
      </div>

      <div class="chart-row">
        <div class="content-card">
          <div class="content-card-header">
            <h2><i class="fa-solid fa-chart-line"></i> My Consumption History</h2>
          </div>
          <div class="chart-container" style="position: relative; height:300px; width:100%">
            <canvas id="consumptionChart"></canvas>
          </div>
        </div>

        <div class="content-card">
          <div class="content-card-header">
            <h2><i class="fa-solid fa-info-circle"></i> Utility Profile</h2>
          </div>
          <div class="utility-summary-list">
            <div class="utility-summary-item ${userMeter ? userMeter.utilityType : 'electricity'}">
              <div class="info">
                <div class="icon">
                  <i class="fa-solid ${userMeter?.utilityType === 'water' ? 'fa-droplet' : userMeter?.utilityType === 'gas' ? 'fa-fire' : 'fa-bolt'}"></i>
                </div>
                <div class="details">
                  <h4>${userMeter ? userMeter.utilityType.toUpperCase() : 'NO METER'}</h4>
                  <span>Assigned Meter Number</span>
                </div>
              </div>
              <div class="value">
                <h5>${userMeter ? userMeter.meter_number : 'N/A'}</h5>
              </div>
            </div>
            <div style="margin-top: 10px; font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">
              <p><strong>Note:</strong> Billing cycles generate on the 25th of every month. Payments made after the due date will incur a 5% late fee penalty.</p>
            </div>
          </div>
        </div>
      </div>
    `;

    // Initialize consumption chart
    if (bills.length > 0) {
      setTimeout(() => {
        const sortedBills = [...bills].sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
        const labels = sortedBills.map(b => `${b.billingMonth} ${b.billingYear}`);
        const data = sortedBills.map(b => b.consumption);

        const ctx = document.getElementById('consumptionChart').getContext('2d');
        new Chart(ctx, {
          type: 'line',
          data: {
            labels: labels,
            datasets: [{
              label: 'Consumption (' + (userMeter ? (userMeter.utilityType === 'electricity' ? 'kWh' : 'm³') : 'units') + ')',
              data: data,
              borderColor: '#00f2fe',
              backgroundColor: 'rgba(0, 242, 254, 0.1)',
              borderWidth: 2,
              fill: true,
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                ticks: { color: '#94a3b8' }
              },
              x: {
                grid: { display: false },
                ticks: { color: '#94a3b8' }
              }
            }
          }
        });
      }, 50);
    } else {
      setTimeout(() => {
        const ctx = document.getElementById('consumptionChart').getContext('2d');
        ctx.font = "14px Outfit";
        ctx.fillStyle = "#64748b";
        ctx.fillText("No consumption history found.", 50, 150);
      }, 50);
    }
  }
};
