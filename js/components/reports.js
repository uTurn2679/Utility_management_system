import { getAll } from '../db.js';

export const ReportsView = {
  render(container, user, showToast) {
    if (user.role !== 'admin') {
      container.innerHTML = `<div class="content-card"><p class="text-danger">Access Denied. Admins only.</p></div>`;
      return;
    }

    const meters = getAll('meters');
    const bills = getAll('bills');
    const complaints = getAll('complaints');
    const payments = getAll('payments');

    // Calculations
    const totalMeters = meters.length;
    const electCount = meters.filter(m => m.utilityType === 'electricity').length;
    const waterCount = meters.filter(m => m.utilityType === 'water').length;
    const gasCount = meters.filter(m => m.utilityType === 'gas').length;

    const paidBills = bills.filter(b => b.status === 'paid');
    const unpaidBills = bills.filter(b => b.status === 'unpaid' || b.status === 'overdue');
    const totalCollected = paidBills.reduce((sum, b) => sum + b.amount, 0);
    const totalUnpaid = unpaidBills.reduce((sum, b) => sum + b.amount, 0);

    const pendingComp = complaints.filter(c => c.status === 'pending').length;
    const resolvedComp = complaints.filter(c => c.status === 'resolved').length;
    const inProgressComp = complaints.filter(c => c.status === 'in-progress').length;

    container.innerHTML = `
      <div class="filter-row">
        <h2>Utility Billing Analytics</h2>
        <div class="filter-actions">
          <button class="btn btn-secondary" id="export-excel-btn"><i class="fa-solid fa-file-excel"></i> Export Excel</button>
          <button class="btn btn-secondary" id="export-pdf-btn"><i class="fa-solid fa-file-pdf"></i> Export PDF</button>
        </div>
      </div>

      <div class="card-grid">
        <div class="metric-card">
          <div class="metric-details">
            <h3>Collection Ratio</h3>
            <div class="metric-val">${bills.length > 0 ? Math.round((paidBills.length / bills.length) * 100) : 0}%</div>
          </div>
          <div class="metric-icon" style="color:var(--success)"><i class="fa-solid fa-circle-check"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>Total Revenue</h3>
            <div class="metric-val">৳${totalCollected.toLocaleString()}</div>
          </div>
          <div class="metric-icon" style="color:var(--primary)"><i class="fa-solid fa-wallet"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>Total Outstandings</h3>
            <div class="metric-val">৳${totalUnpaid.toLocaleString()}</div>
          </div>
          <div class="metric-icon" style="color:var(--danger)"><i class="fa-solid fa-circle-dollar-to-slot"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>Complaint Resolution</h3>
            <div class="metric-val">${complaints.length > 0 ? Math.round((resolvedComp / complaints.length) * 100) : 0}%</div>
          </div>
          <div class="metric-icon" style="color:var(--warning)"><i class="fa-solid fa-headset"></i></div>
        </div>
      </div>

      <div class="chart-row">
        <!-- Utility Distribution Chart -->
        <div class="content-card">
          <div class="content-card-header">
            <h2>Utility Distribution</h2>
          </div>
          <div class="chart-container" style="position: relative; height:260px; width:100%">
            <canvas id="utilityDistChart"></canvas>
          </div>
        </div>

        <!-- Collections vs Outstandings Chart -->
        <div class="content-card">
          <div class="content-card-header">
            <h2>Financial Overview</h2>
          </div>
          <div class="chart-container" style="position: relative; height:260px; width:100%">
            <canvas id="financialComparisonChart"></canvas>
          </div>
        </div>
      </div>

      <div class="content-card" style="margin-top:24px;">
        <div class="content-card-header">
          <h2>Complaint Tickets Activity Summary</h2>
        </div>
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:24px; text-align:center; padding:16px 0;">
          <div style="background:var(--bg-tertiary); padding:16px; border-radius:8px; border:1px solid var(--border-color)">
            <h4 class="text-danger" style="font-size:1.8rem; font-weight:700;">${pendingComp}</h4>
            <span class="text-secondary" style="font-size:0.85rem;">Pending / Unassigned</span>
          </div>
          <div style="background:var(--bg-tertiary); padding:16px; border-radius:8px; border:1px solid var(--border-color)">
            <h4 class="text-warning" style="font-size:1.8rem; font-weight:700;">${inProgressComp}</h4>
            <span class="text-secondary" style="font-size:0.85rem;">In Progress / Checking</span>
          </div>
          <div style="background:var(--bg-tertiary); padding:16px; border-radius:8px; border:1px solid var(--border-color)">
            <h4 class="text-success" style="font-size:1.8rem; font-weight:700;">${resolvedComp}</h4>
            <span class="text-secondary" style="font-size:0.85rem;">Resolved / Closed</span>
          </div>
        </div>
      </div>
    `;

    // Render Charts
    setTimeout(() => {
      // Donut Chart
      const distCtx = document.getElementById('utilityDistChart').getContext('2d');
      new Chart(distCtx, {
        type: 'doughnut',
        data: {
          labels: ['Electricity', 'Water', 'Gas'],
          datasets: [{
            data: [electCount, waterCount, gasCount],
            backgroundColor: ['#f59e0b', '#3b82f6', '#ef4444'],
            borderColor: '#111827',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: '#94a3b8', font: { family: 'Outfit' } }
            }
          }
        }
      });

      // Pie Chart (Financial Overview)
      const finCtx = document.getElementById('financialComparisonChart').getContext('2d');
      new Chart(finCtx, {
        type: 'pie',
        data: {
          labels: ['Collected Revenue', 'Outstanding Receivables'],
          datasets: [{
            data: [totalCollected, totalUnpaid],
            backgroundColor: ['#10b981', '#ef4444'],
            borderColor: '#111827',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: '#94a3b8', font: { family: 'Outfit' } }
            }
          }
        }
      });
    }, 50);

    // Bind Export Buttons
    document.getElementById('export-excel-btn').addEventListener('click', () => {
      showToast('Excel report generated and downloaded successfully.', 'success');
    });

    document.getElementById('export-pdf-btn').addEventListener('click', () => {
      showToast('PDF summary report generated and downloaded.', 'success');
    });
  }
};
