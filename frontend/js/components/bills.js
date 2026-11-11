import { getAll, add, update, remove, addNotification, TARIFF_RATES } from '../db.js';

export const BillsView = {
  render(container, user, showToast, openModal, closeModal) {
    if (user.role === 'customer') {
      this.renderCustomerBills(container, user, showToast, openModal, closeModal);
    } else {
      this.renderStaffBills(container, user, showToast, openModal, closeModal);
    }
  },

  renderCustomerBills(container, user, showToast, openModal, closeModal) {
    const bills = getAll('bills').filter(b => b.customer_id === user.customerId);

    container.innerHTML = `
      <div class="filter-row">
        <div class="search-wrapper">
          <i class="fa-solid fa-filter"></i>
          <select id="bill-status-filter" style="padding-left: 40px; width:100%;">
            <option value="">All Payment Statuses</option>
            <option value="paid">Paid</option>
            <option value="unpaid">Unpaid</option>
            <option value="overdue">Overdue</option>
          </select>
        </div>
        <div>
          <span class="text-muted" style="margin-right:16px;">
            Total Bills: <strong>${bills.length}</strong>
          </span>
        </div>
      </div>

      <div class="content-card">
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Billing Cycle</th>
                <th>Meter Readings</th>
                <th>Consumption</th>
                <th>Rate Applied</th>
                <th>Total Bill</th>
                <th>Due Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="bills-table-body">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
    `;

    const populateTable = () => {
      const statusFilter = document.getElementById('bill-status-filter').value;
      const tbody = document.getElementById('bills-table-body');

      const filtered = bills.filter(b => {
        return statusFilter === '' || b.status === statusFilter;
      }).reverse();

      if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-muted" style="text-align:center;">No bills found.</td></tr>`;
        return;
      }

      tbody.innerHTML = filtered.map(b => {
        const meter = getAll('meters').find(m => m.meter_id === b.meterId);
        const unit = meter ? (meter.utilityType === 'electricity' ? 'kWh' : meter.utilityType === 'wifi' ? 'Mbps' : 'm³') : 'units';
        const typeLabel = meter ? meter.utilityType.toUpperCase() : 'Utility';

        return `
          <tr>
            <td>
              <div style="font-weight:600;">${b.billingMonth} ${b.billingYear}</div>
              <span class="badge badge-info" style="font-size:0.65rem;">${typeLabel}</span>
            </td>
            <td>${b.prevReading} &rarr; ${b.currReading}</td>
            <td><strong>${b.consumption}</strong> ${unit}</td>
            <td>৳${b.tariffRate || 8} / unit</td>
            <td><strong>৳${b.amount}</strong></td>
            <td>${b.due_date}</td>
            <td><span class="badge badge-${b.status === 'paid' ? 'success' : b.status === 'unpaid' ? 'danger' : 'warning'}">${b.status}</span></td>
            <td>
              <div class="action-btn-group">
                ${b.status !== 'paid' ? `
                  <a href="#/payments" class="btn btn-primary" style="padding:6px 12px; font-size:0.75rem;">Pay Now</a>
                ` : `
                  <button class="btn btn-secondary view-receipt-btn" data-id="${b.bill_id}" style="padding:6px 12px; font-size:0.75rem;">
                    <i class="fa-solid fa-file-invoice"></i> Receipt
                  </button>
                `}
              </div>
            </td>
          </tr>
        `;
      }).join('');

      tbody.querySelectorAll('.view-receipt-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.showReceiptModal(btn.dataset.id, openModal, closeModal);
        });
      });
    };

    populateTable();

    document.getElementById('bill-status-filter').addEventListener('change', populateTable);
  },

  renderStaffBills(container, user, showToast, openModal, closeModal) {
    const bills = getAll('bills');
    const customers = getAll('customers');
    const users = getAll('users');

    container.innerHTML = `
      <div class="filter-row">
        <div class="search-wrapper">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input type="text" id="bill-search" placeholder="Search by customer name...">
        </div>
        <div class="filter-actions">
          <select id="bill-month-filter">
            <option value="">All Months</option>
            <option value="January">January</option>
            <option value="February">February</option>
            <option value="March">March</option>
            <option value="April">April</option>
            <option value="May">May</option>
            <option value="June">June</option>
            <option value="July">July</option>
            <option value="August">August</option>
            <option value="September">September</option>
            <option value="October">October</option>
            <option value="November">November</option>
            <option value="December">December</option>
          </select>
          <select id="bill-status-filter">
            <option value="">All Statuses</option>
            <option value="paid">Paid</option>
            <option value="unpaid">Unpaid</option>
            <option value="overdue">Overdue</option>
          </select>
          <button class="btn btn-secondary" id="auto-generate-bills-btn">
            <i class="fa-solid fa-wand-magic-sparkles"></i> Auto Generate Bills
          </button>
          <button class="btn btn-secondary" id="send-due-reminders-btn" style="background: linear-gradient(135deg, #f5af19, #f12711); color: white; border: none;">
            <i class="fa-solid fa-bell"></i> Send Gmail Reminders
          </button>
          <button class="btn btn-secondary" id="view-email-logs-btn" style="background: linear-gradient(135deg, #00c6ff, #0072ff); color: white; border: none;">
            <i class="fa-solid fa-clock-rotate-left"></i> Email Logs
          </button>
          <button class="btn btn-primary" id="generate-bill-btn">
            <i class="fa-solid fa-calculator"></i> Generate Bill
          </button>
        </div>
      </div>

      <div class="content-card">
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Billing Cycle</th>
                <th>Meter Readings</th>
                <th>Consumption</th>
                <th>Total Bill</th>
                <th>Due Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="staff-bills-table-body">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
    `;

    const populateTable = () => {
      const searchTerm = document.getElementById('bill-search').value.toLowerCase();
      const monthFilter = document.getElementById('bill-month-filter').value;
      const statusFilter = document.getElementById('bill-status-filter').value;
      const tbody = document.getElementById('staff-bills-table-body');

      const filtered = bills.filter(b => {
        const customer = customers.find(c => c.customer_id === b.customer_id);
        const custUser = customer ? users.find(u => u.id === customer.user_id) : null;
        const matchesSearch = custUser ? custUser.name.toLowerCase().includes(searchTerm) : false;
        const matchesMonth = monthFilter === '' || b.billingMonth === monthFilter;
        const matchesStatus = statusFilter === '' || b.status === statusFilter;
        return matchesSearch && matchesMonth && matchesStatus;
      }).reverse();

      if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-muted" style="text-align:center;">No billing records found.</td></tr>`;
        return;
      }

      tbody.innerHTML = filtered.map(b => {
        const customer = customers.find(c => c.customer_id === b.customer_id);
        const custUser = customer ? users.find(u => u.id === customer.user_id) : null;
        const meter = getAll('meters').find(m => m.meter_id === b.meterId);
        const unit = meter ? (meter.utilityType === 'electricity' ? 'kWh' : meter.utilityType === 'wifi' ? 'Mbps' : 'm³') : 'units';
        const typeLabel = meter ? meter.utilityType.toUpperCase() : 'Utility';

        return `
          <tr>
            <td>
              <div style="font-weight:600;">${custUser ? custUser.name : 'Unknown'}</div>
              <small class="text-muted">Cust ID: ${b.customer_id}</small>
            </td>
            <td>
              <strong>${b.billingMonth} ${b.billingYear}</strong><br>
              <span class="badge badge-info" style="font-size:0.6rem;">${typeLabel}</span>
            </td>
            <td>${b.prevReading} &rarr; ${b.currReading}</td>
            <td><strong>${b.consumption}</strong> ${unit}</td>
            <td><strong>৳${b.amount}</strong></td>
            <td>${b.due_date}</td>
            <td><span class="badge badge-${b.status === 'paid' ? 'success' : b.status === 'unpaid' ? 'danger' : 'warning'}">${b.status}</span></td>
            <td>
              <div class="action-btn-group">
                <button class="btn-icon-only view-receipt-btn" data-id="${b.bill_id}" title="View Receipt/Details">
                  <i class="fa-solid fa-file-invoice"></i>
                </button>
                <button class="btn-icon-only edit-bill-btn" data-id="${b.bill_id}" title="Edit Bill" style="color:var(--primary);">
                  <i class="fa-solid fa-pen-to-square"></i>
                </button>
                <button class="btn-icon-only danger delete-bill-btn" data-id="${b.bill_id}" title="Delete Bill">
                  <i class="fa-solid fa-trash-can"></i>
                </button>
                ${b.status !== 'paid' ? `
                  <button class="btn-icon-only send-reminder-btn" data-id="${b.bill_id}" title="Send Email Reminder" style="color: #ff5e62;">
                    <i class="fa-solid fa-envelope"></i>
                  </button>
                  <button class="btn-icon-only success mark-paid-btn" data-id="${b.bill_id}" title="Mark Paid">
                    <i class="fa-solid fa-circle-check"></i>
                  </button>
                ` : ''}
              </div>
            </td>
          </tr>
        `;
      }).join('');

      tbody.querySelectorAll('.view-receipt-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.showReceiptModal(btn.dataset.id, openModal, closeModal);
        });
      });

      tbody.querySelectorAll('.edit-bill-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.showEditBillModal(btn.dataset.id, openModal, closeModal, showToast, () => {
            this.renderStaffBills(container, user, showToast, openModal, closeModal);
          });
        });
      });

      tbody.querySelectorAll('.delete-bill-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.showDeleteBillModal(btn.dataset.id, openModal, closeModal, showToast, () => {
            this.renderStaffBills(container, user, showToast, openModal, closeModal);
          });
        });
      });

      tbody.querySelectorAll('.mark-paid-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const bId = btn.dataset.id;
          const today = new Date().toISOString().split('T')[0];
          update('bills', bId, { status: 'paid', paymentDate: today });
          showToast('Bill marked as Paid successfully', 'success');

          const targetBill = bills.find(b => b.bill_id === bId);
          add('payments', {
            bill_id: bId,
            amount: targetBill.amount,
            payment_date: today,
            method: 'cash',
            transactionId: 'TXN-CASH' + Math.floor(100000 + Math.random() * 900000),
            status: 'verified'
          });

          const customer = customers.find(c => c.customer_id === targetBill.customer_id);
          if (customer) {
            addNotification(customer.user_id, `Your bill of ৳${targetBill.amount} for ${targetBill.billingMonth} ${targetBill.billingYear} has been marked as PAID.`, 'success');
          }

          this.renderStaffBills(container, user, showToast, openModal, closeModal);
        });
      });

      tbody.querySelectorAll('.send-reminder-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const billId = btn.dataset.id;
          showToast('Sending email reminder...', 'info');

          fetch('http://localhost:5000/api/send-bill-reminder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ billId })
          })
          .then(res => {
            if (!res.ok) throw new Error('API server returned error status');
            return res.json();
          })
          .then(data => {
            if (data.success) {
              showToast(`Unpaid bill reminder email sent to ${data.email}`, 'success');
            } else {
              showToast('Failed to send email: ' + (data.error || 'unknown error'), 'danger');
            }
          })
          .catch(err => {
            console.error(err);
            showToast('Failed to send email reminder', 'danger');
          });
        });
      });
    };

    populateTable();

    document.getElementById('bill-search').addEventListener('input', populateTable);
    document.getElementById('bill-month-filter').addEventListener('change', populateTable);
    document.getElementById('bill-status-filter').addEventListener('change', populateTable);

    document.getElementById('generate-bill-btn').addEventListener('click', () => {
      this.showGenerateBillModal(openModal, closeModal, showToast, () => {
        this.renderStaffBills(container, user, showToast, openModal, closeModal);
      });
    });

    document.getElementById('auto-generate-bills-btn').addEventListener('click', () => {
      this.autoGenerateBillsBatch(showToast, () => {
        this.renderStaffBills(container, user, showToast, openModal, closeModal);
      });
    });

    document.getElementById('send-due-reminders-btn').addEventListener('click', () => {
      showToast('Running upcoming due alerts scan...', 'info');
      fetch('http://localhost:5000/api/run-due-reminders', {
        method: 'POST'
      })
      .then(res => {
        if (!res.ok) throw new Error('API server returned error status');
        return res.json();
      })
      .then(data => {
        if (data.success) {
          showToast(`Gmail Alerts Sent: ${data.count} notifications dispatched.`, 'success');
        } else {
          showToast('Failed to run due alerts check', 'danger');
        }
      })
      .catch(err => {
        console.error(err);
        showToast('Failed to connect to backend server', 'danger');
      });
    });

    document.getElementById('view-email-logs-btn').addEventListener('click', () => {
      this.showEmailLogsModal(openModal, closeModal, showToast);
    });
  },

  autoGenerateBillsBatch(showToast, refreshCallback) {
    const meters = getAll('meters');
    const readings = getAll('meter_readings');
    const bills = getAll('bills');
    const customers = getAll('customers');

    let count = 0;

    meters.forEach(meter => {
      if (!meter.customer_id) return; // skip unassigned

      // Find all readings for this meter
      const mReadings = readings.filter(r => r.meter_id === meter.meter_id);
      if (mReadings.length < 2) return; // skip if not enough readings

      // Sort by reading value or insert order
      // We can use the order in array or create date if available. Since seeded in order, let's sort by reading_id suffix or index:
      const sortedReads = [...mReadings].sort((a, b) => {
        const idA = parseInt(a.reading_id.split('-')[1], 10) || 0;
        const idB = parseInt(b.reading_id.split('-')[1], 10) || 0;
        return idA - idB;
      });

      // Get latest two readings
      const r1 = sortedReads[sortedReads.length - 2];
      const r2 = sortedReads[sortedReads.length - 1];

      const billingMonth = r2.month;
      const billingYear = '2026';

      // Check if a bill is already generated for this customer, meter, and billing cycle
      const billExists = bills.some(b => 
        b.customer_id === meter.customer_id && 
        b.billingMonth === billingMonth && 
        b.billingYear === billingYear &&
        b.meterId === meter.meter_id
      );

      if (!billExists) {
        const consumption = r2.unit_consumed - r1.unit_consumed;
        if (consumption > 0) {
          const rate = 8; // Rate = 8 BDT/unit
          const amount = consumption * rate;

          // Calculate due date (15 days from today)
          const due = new Date();
          due.setDate(due.getDate() + 15);
          const dueDateString = due.toISOString().split('T')[0];

          add('bills', {
            customer_id: meter.customer_id,
            amount: amount,
            due_date: dueDateString,
            status: 'unpaid',
            billingMonth: billingMonth,
            billingYear: billingYear,
            meterId: meter.meter_id,
            prevReading: r1.unit_consumed,
            currReading: r2.unit_consumed,
            consumption,
            tariffRate: rate,
            createdAt: new Date().toISOString().split('T')[0]
          });

          // Notify customer
          const customer = customers.find(c => c.customer_id === meter.customer_id);
          if (customer) {
            addNotification(customer.user_id, `Auto-generated Bill of ৳${amount} for ${billingMonth} ${billingYear} is now available. Due: ${dueDateString}.`, 'warning');
          }

          count++;
        }
      }
    });

    if (count > 0) {
      showToast(`Successfully auto-generated ${count} billing invoices!`, 'success');
      refreshCallback();
    } else {
      showToast('No outstanding readings found to generate new bills.', 'info');
    }
  },

  showGenerateBillModal(openModal, closeModal, showToast, refreshCallback) {
    const customers = getAll('customers');
    const users = getAll('users');
    const meters = getAll('meters');
    const readings = getAll('meter_readings');

    const billedCustomers = customers;

    const modalHtml = `
      <div class="modal-header">
        <h2>Generate Utility Bill</h2>
      </div>
      <form id="generate-bill-form">
        <div class="form-group">
          <label for="bill-customer-input">Select Customer</label>
          <input type="text" id="bill-customer-input" list="customers-datalist" placeholder="Type customer name or ID..." required autocomplete="off" style="width:100%; padding:10px 16px; background:var(--bg-secondary); border:1px solid var(--border-color); border-radius:8px; color:var(--text-primary);">
          <datalist id="customers-datalist">
            ${billedCustomers.map(c => {
              const u = users.find(usr => usr.id === c.user_id);
              return `<option value="${u ? u.name : 'Unknown'} (${c.customer_id})"></option>`;
            }).join('')}
          </datalist>
        </div>
        <div id="no-meter-section" class="hidden" style="background:var(--bg-tertiary); padding:12px; border-radius:8px; margin-bottom:16px; border:1px solid var(--border-color)">
          <p style="font-size:0.85rem; color:var(--warning); margin-bottom:8px; font-weight:600;"><i class="fa-solid fa-triangle-exclamation"></i> Customer has no active meter. Create one below:</p>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px;">
            <div>
              <label style="font-size:0.75rem; font-weight:600;">Utility Type</label>
              <select id="new-meter-type" style="width:100%; padding:6px; border-radius:4px; background:var(--bg-secondary); color:var(--text-primary); border:1px solid var(--border-color);">
                <option value="">-- Select Type --</option>
                <option value="electricity">Electricity</option>
                <option value="water">Water</option>
                <option value="gas">Gas</option>
                <option value="wifi">WiFi</option>
              </select>
            </div>
            <div>
              <label style="font-size:0.75rem; font-weight:600;">Meter Number</label>
              <input type="text" id="new-meter-number" readonly style="width:100%; padding:6px; border-radius:4px; background:var(--bg-secondary); color:var(--text-primary); border:1px solid var(--border-color);">
            </div>
          </div>
        </div>
        <div id="meter-info-section" class="hidden" style="background:var(--bg-tertiary); padding:12px; border-radius:8px; margin-bottom:16px; border:1px solid var(--border-color)">
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:0.85rem;">
            <div><strong>Meter Number:</strong> <span id="bill-meter-serial"></span></div>
            <div><strong>Utility Type:</strong> <span id="bill-meter-type"></span></div>
            <div><strong>Previous Reading:</strong> <span id="bill-prev-reading"></span></div>
          </div>
        </div>
        <div class="form-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
          <div>
            <label for="bill-curr-reading">Current Reading</label>
            <input type="number" id="bill-curr-reading" required disabled>
          </div>
          <div>
            <label for="bill-rate">Rate (৳/Unit)</label>
            <input type="number" id="bill-rate" value="8" min="1" required disabled>
          </div>
        </div>
        <div class="form-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
          <div>
            <label for="bill-month">Billing Month</label>
            <select id="bill-month" required>
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
            <label for="bill-year">Billing Year</label>
            <input type="number" id="bill-year" value="2026" min="2020" max="2050" required>
          </div>
        </div>
        <div id="calculation-preview-section" class="hidden" style="background:var(--bg-tertiary); padding:12px; border-radius:8px; margin-bottom:16px; border:1px solid var(--border-color); font-size:0.9rem;">
          <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
            <span>Consumed Units:</span>
            <strong id="preview-consumed">0</strong>
          </div>
          <div style="display:flex; justify-content:space-between; font-weight:700;">
            <span>Total Payable Amount:</span>
            <span style="color:var(--primary)">৳<span id="preview-amount">0</span></span>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" id="cancel-gen-btn">Cancel</button>
          <button type="submit" class="btn btn-primary" id="calculate-btn" disabled>Generate</button>
        </div>
      </form>
    `;

    openModal(modalHtml, () => {
      const custInput = document.getElementById('bill-customer-input');
      const meterSection = document.getElementById('meter-info-section');
      const noMeterSection = document.getElementById('no-meter-section');
      const newMeterType = document.getElementById('new-meter-type');
      const newMeterNumber = document.getElementById('new-meter-number');
      const calcSection = document.getElementById('calculation-preview-section');
      const serialSpan = document.getElementById('bill-meter-serial');
      const typeSpan = document.getElementById('bill-meter-type');
      const prevSpan = document.getElementById('bill-prev-reading');
      const currInput = document.getElementById('bill-curr-reading');
      const rateInput = document.getElementById('bill-rate');
      const previewConsumed = document.getElementById('preview-consumed');
      const previewAmount = document.getElementById('preview-amount');
      const calculateBtn = document.getElementById('calculate-btn');

      let activeMeter = null;

      const updateCalculations = () => {
        const prev = parseInt(prevSpan.textContent, 10) || 0;
        const curr = parseInt(currInput.value, 10) || 0;
        const rate = parseInt(rateInput.value, 10) || 8;
        
        const consumption = curr >= prev ? curr - prev : 0;
        const total = consumption * rate;

        previewConsumed.textContent = consumption;
        previewAmount.textContent = total.toLocaleString();

        if (consumption > 0) {
          calcSection.classList.remove('hidden');
        } else {
          calcSection.classList.add('hidden');
        }
      };

      currInput.addEventListener('input', updateCalculations);
      rateInput.addEventListener('input', updateCalculations);

      const getSelectedCustomerId = () => {
        const val = custInput.value.trim().toLowerCase();
        if (!val) return null;

        // 1. Try to parse "(cus-XXXX)" format
        const match = val.match(/\((cus-[^)]+)\)/i);
        if (match) return match[1].toLowerCase();

        // 2. Try to match exact customer ID (e.g. "cus-1")
        const directCust = customers.find(c => c.customer_id.toLowerCase() === val);
        if (directCust) return directCust.customer_id;

        // 3. Try to match by customer name (case-insensitive)
        const matchByName = customers.find(c => {
          const u = users.find(usr => usr.id === c.user_id);
          return u && u.name.toLowerCase() === val;
        });
        if (matchByName) return matchByName.customer_id;

        // 4. Try to match by username
        const matchByUsername = customers.find(c => {
          const u = users.find(usr => usr.id === c.user_id);
          return u && u.username.toLowerCase() === val;
        });
        if (matchByUsername) return matchByUsername.customer_id;

        return null;
      };

      const handleCustomerChange = () => {
        const cId = getSelectedCustomerId();
        if (!cId) {
          meterSection.classList.add('hidden');
          noMeterSection.classList.add('hidden');
          calcSection.classList.add('hidden');
          currInput.disabled = true;
          rateInput.disabled = true;
          calculateBtn.disabled = true;
          return;
        }

        activeMeter = meters.find(m => m.customer_id === cId);

        if (!activeMeter) {
          noMeterSection.classList.remove('hidden');
          meterSection.classList.add('hidden');
          calcSection.classList.add('hidden');
          currInput.disabled = true;
          rateInput.disabled = true;
          calculateBtn.disabled = true;

          // Pre-generate a meter number
          const randMeterNum = 'MTR-' + Math.floor(100000 + Math.random() * 900000);
          newMeterNumber.value = randMeterNum;
          newMeterType.value = '';
          return;
        }

        noMeterSection.classList.add('hidden');
        const meterReadings = readings.filter(r => r.meter_id === activeMeter.meter_id);
        const prevReading = meterReadings.length > 0 ? Math.max(...meterReadings.map(r => r.unit_consumed)) : 0;

        serialSpan.textContent = activeMeter.meter_number;
        typeSpan.textContent = activeMeter.utilityType.toUpperCase();
        prevSpan.textContent = prevReading;

        currInput.disabled = false;
        currInput.min = prevReading;
        currInput.value = prevReading + 150; // default 150 units consumed in example
        rateInput.disabled = false;
        calculateBtn.disabled = false;
        meterSection.classList.remove('hidden');
        updateCalculations();
      };

      custInput.addEventListener('input', handleCustomerChange);

      newMeterType.addEventListener('change', () => {
        const type = newMeterType.value;
        if (!type) {
          meterSection.classList.add('hidden');
          calcSection.classList.add('hidden');
          currInput.disabled = true;
          rateInput.disabled = true;
          calculateBtn.disabled = true;
          return;
        }

        serialSpan.textContent = newMeterNumber.value;
        typeSpan.textContent = type.toUpperCase();
        prevSpan.textContent = 0;

        currInput.disabled = false;
        currInput.min = 0;
        currInput.value = 100; // default for new meter
        rateInput.disabled = false;
        calculateBtn.disabled = false;
        meterSection.classList.remove('hidden');
        updateCalculations();
      });

      document.getElementById('cancel-gen-btn').addEventListener('click', closeModal);

      document.getElementById('generate-bill-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const cId = getSelectedCustomerId();
        if (!cId) {
          showToast('Please select a valid customer from the suggestions.', 'danger');
          return;
        }

        // On-the-fly meter creation
        if (!activeMeter) {
          const type = newMeterType.value;
          const serial = newMeterNumber.value;
          if (!type) {
            showToast('Please select a utility type for the new meter.', 'danger');
            return;
          }
          activeMeter = add('meters', {
            meter_number: serial,
            utilityType: type,
            customer_id: cId,
            installationDate: new Date().toISOString().split('T')[0],
            status: 'active'
          });
          showToast(`New ${type.toUpperCase()} meter registered successfully for customer.`, 'success');
        }

        const currReading = parseInt(currInput.value, 10);
        
        const meterReadings = readings.filter(r => r.meter_id === activeMeter.meter_id);
        const prevReading = meterReadings.length > 0 ? Math.max(...meterReadings.map(r => r.unit_consumed)) : 0;
        
        const month = document.getElementById('bill-month').value;
        const year = document.getElementById('bill-year').value;
        const rate = parseInt(rateInput.value, 10) || 8;

        if (currReading < prevReading) {
          showToast('Current reading cannot be lower than previous reading.', 'danger');
          return;
        }

        const consumption = currReading - prevReading;
        const amount = consumption * rate;

        const due = new Date();
        due.setDate(due.getDate() + 15);
        const dueDateString = due.toISOString().split('T')[0];

        // 1. Create Bill record
        add('bills', {
          customer_id: cId,
          amount: amount,
          due_date: dueDateString,
          status: 'unpaid',
          billingMonth: month,
          billingYear: year,
          meterId: activeMeter.meter_id,
          prevReading,
          currReading,
          consumption,
          tariffRate: rate,
          createdAt: new Date().toISOString().split('T')[0]
        });

        // 2. Insert new entry in meter_readings table
        add('meter_readings', {
          meter_id: activeMeter.meter_id,
          month: month,
          unit_consumed: currReading
        });

        const customer = customers.find(c => c.customer_id === cId);
        if (customer) {
          addNotification(customer.user_id, `A new bill of ৳${amount} for ${month} ${year} has been generated. Due: ${dueDateString}.`, 'warning');
        }

        showToast('Bill generated and reading logged successfully.', 'success');
        closeModal();
        refreshCallback();
      });
    });
  },

  showReceiptModal(billId, openModal, closeModal) {
    const bill = getAll('bills').find(b => b.bill_id === billId);
    const customer = getAll('customers').find(c => c.customer_id === bill.customer_id);
    const custUser = customer ? getAll('users').find(u => u.id === customer.user_id) : null;
    const meter = getAll('meters').find(m => m.meter_id === bill.meterId);
    const datePaidText = bill.paymentDate ? `<tr><td><strong>Payment Date:</strong></td><td>${bill.paymentDate}</td></tr>` : '';

    const modalHtml = `
      <div class="modal-header" style="border-bottom: 2px dashed var(--border-color); padding-bottom: 12px;">
        <h2 style="display:flex; justify-content:space-between; align-items:center; width:100%;">
          <span>Utility Invoice</span>
          <span class="badge badge-${bill.status === 'paid' ? 'success' : 'danger'}" style="font-size:0.75rem;">${bill.status.toUpperCase()}</span>
        </h2>
      </div>
      <div style="font-family: var(--font-secondary); padding: 10px 0; font-size: 0.85rem;">
        <table style="width:100%; border-collapse:collapse; margin-bottom: 20px; line-height: 1.6;">
          <tr>
            <td><strong>Invoice ID:</strong></td>
            <td>${bill.bill_id}</td>
          </tr>
          <tr>
            <td><strong>Customer Name:</strong></td>
            <td>${custUser ? custUser.name : 'N/A'}</td>
          </tr>
          <tr>
            <td><strong>Email Address:</strong></td>
            <td>${custUser ? custUser.email : 'N/A'}</td>
          </tr>
          <tr>
            <td><strong>Meter Number:</strong></td>
            <td>${meter ? `${meter.meter_number} (${meter.utilityType.toUpperCase()})` : 'N/A'}</td>
          </tr>
          <tr>
            <td><strong>Billing Period:</strong></td>
            <td>${bill.billingMonth} ${bill.billingYear}</td>
          </tr>
          <tr>
            <td><strong>Due Date:</strong></td>
            <td>${bill.due_date}</td>
          </tr>
          ${datePaidText}
        </table>

        <div style="border-top:1px solid var(--border-color); border-bottom:1px solid var(--border-color); padding: 12px 0; margin-bottom:20px;">
          <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span>Reading: ${bill.prevReading} &rarr; ${bill.currReading}</span>
            <span><strong>${bill.consumption} ${meter?.utilityType === 'electricity' ? 'kWh' : meter?.utilityType === 'wifi' ? 'Mbps' : 'm³'}</strong></span>
          </div>
          <div style="display:flex; justify-content:space-between;">
            <span>Rate Cost (৳${bill.tariffRate || 8} / unit)</span>
            <span>৳${(bill.consumption * (bill.tariffRate || 8)).toFixed(2)}</span>
          </div>
        </div>

        <div style="display:flex; justify-content:space-between; font-size:1.15rem; font-weight:700; margin-bottom: 20px;">
          <span>Net Payable Amount:</span>
          <span>৳${bill.amount.toLocaleString()}</span>
        </div>

        <div style="display:flex; flex-direction:column; align-items:center; gap:8px; margin-top:20px; padding:12px; background:rgba(255,255,255,0.02); border-radius:8px; border:1px solid var(--border-color); text-align:center;">
          <img src="https://api.qrserver.com/v1/create-qr-code/?size=130x130&data=${encodeURIComponent(window.location.origin + window.location.pathname + '#/public-bill-view?id=' + bill.bill_id)}" alt="Invoice QR Code" style="border: 4px solid #fff; border-radius: 6px; width: 130px; height: 130px;">
          <span style="font-size:0.75rem; color:var(--text-muted);"><i class="fa-solid fa-qrcode"></i> Scan to verify digital bill details</span>
        </div>
      </div>
      <div class="modal-footer" style="border-top: 1px solid var(--border-color); padding-top: 12px;">
        <button class="btn btn-secondary" onclick="window.print()" style="gap:4px;"><i class="fa-solid fa-print"></i> Print</button>
        <button class="btn btn-primary" id="close-receipt-btn">Done</button>
      </div>
    `;

    openModal(modalHtml, () => {
      document.getElementById('close-receipt-btn').addEventListener('click', closeModal);
    });
  },

  showEditBillModal(billId, openModal, closeModal, showToast, refreshCallback) {
    const bill = getAll('bills').find(b => b.bill_id === billId);
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    
    const modalHtml = `
      <div class="modal-header">
        <h2>Edit Bill Details</h2>
      </div>
      <form id="edit-bill-form">
        <div class="form-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
          <div>
            <label for="edit-bill-month">Billing Month</label>
            <select id="edit-bill-month" required>
              ${months.map(m => `<option value="${m}" ${bill.billingMonth === m ? 'selected' : ''}>${m}</option>`).join('')}
            </select>
          </div>
          <div>
            <label for="edit-bill-year">Billing Year</label>
            <input type="number" id="edit-bill-year" value="${bill.billingYear}" min="2020" max="2050" required>
          </div>
        </div>
        <div class="form-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
          <div>
            <label for="edit-bill-prev">Previous Reading</label>
            <input type="number" id="edit-bill-prev" value="${bill.prevReading || 0}" required>
          </div>
          <div>
            <label for="edit-bill-curr">Current Reading</label>
            <input type="number" id="edit-bill-curr" value="${bill.currReading || 0}" required>
          </div>
        </div>
        <div class="form-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
          <div>
            <label for="edit-bill-rate">Rate (৳/Unit)</label>
            <input type="number" id="edit-bill-rate" value="${bill.tariffRate || 8}" min="1" required>
          </div>
          <div>
            <label for="edit-bill-amount">Bill Amount (৳)</label>
            <input type="number" id="edit-bill-amount" value="${bill.amount}" required>
          </div>
        </div>
        <div class="form-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
          <div>
            <label for="edit-bill-due">Due Date</label>
            <input type="date" id="edit-bill-due" value="${bill.due_date}" required>
          </div>
          <div>
            <label for="edit-bill-status">Payment Status</label>
            <select id="edit-bill-status" required>
              <option value="unpaid" ${bill.status === 'unpaid' ? 'selected' : ''}>Unpaid</option>
              <option value="paid" ${bill.status === 'paid' ? 'selected' : ''}>Paid</option>
              <option value="overdue" ${bill.status === 'overdue' ? 'selected' : ''}>Overdue</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" id="cancel-edit-bill-btn">Cancel</button>
          <button type="submit" class="btn btn-primary">Save Changes</button>
        </div>
      </form>
    `;
    
    openModal(modalHtml, () => {
      const monthSelect = document.getElementById('edit-bill-month');
      const yearInput = document.getElementById('edit-bill-year');
      const prevInput = document.getElementById('edit-bill-prev');
      const currInput = document.getElementById('edit-bill-curr');
      const rateInput = document.getElementById('edit-bill-rate');
      const amountInput = document.getElementById('edit-bill-amount');
      const dueInput = document.getElementById('edit-bill-due');
      const statusSelect = document.getElementById('edit-bill-status');

      const updateCalculatedAmount = () => {
        const prev = parseFloat(prevInput.value) || 0;
        const curr = parseFloat(currInput.value) || 0;
        const rate = parseFloat(rateInput.value) || 8;
        if (curr >= prev) {
          amountInput.value = (curr - prev) * rate;
        }
      };

      prevInput.addEventListener('input', updateCalculatedAmount);
      currInput.addEventListener('input', updateCalculatedAmount);
      rateInput.addEventListener('input', updateCalculatedAmount);

      document.getElementById('cancel-edit-bill-btn').addEventListener('click', closeModal);
      
      document.getElementById('edit-bill-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const month = monthSelect.value;
        const year = yearInput.value;
        const prevReading = parseInt(prevInput.value, 10);
        const currReading = parseInt(currInput.value, 10);
        const rate = parseFloat(rateInput.value);
        const amount = parseFloat(amountInput.value);
        const due_date = dueInput.value;
        const status = statusSelect.value;

        if (currReading < prevReading) {
          showToast('Current reading cannot be lower than previous reading.', 'danger');
          return;
        }

        const consumption = currReading - prevReading;

        // Find the original corresponding reading in meter_readings table
        const readings = getAll('meter_readings');
        const reading = readings.find(r => r.meter_id === bill.meterId && r.month === bill.billingMonth && r.unit_consumed === bill.currReading);

        if (reading) {
          update('meter_readings', reading.reading_id, {
            month: month,
            unit_consumed: currReading
          });
        }

        update('bills', billId, {
          billingMonth: month,
          billingYear: year,
          prevReading,
          currReading,
          consumption,
          tariffRate: rate,
          amount,
          due_date,
          status
        });

        showToast('Bill details and readings updated successfully.', 'success');
        closeModal();
        refreshCallback();
      });
    });
  },

  showDeleteBillModal(billId, openModal, closeModal, showToast, refreshCallback) {
    const modalHtml = `
      <div class="modal-header">
        <h2 class="text-danger"><i class="fa-solid fa-trash"></i> Delete Bill?</h2>
      </div>
      <div style="font-size:0.9rem; line-height:1.5; margin-bottom:24px;">
        <p>Are you sure you want to permanently delete the bill <strong>${billId}</strong>?</p>
        <p class="text-muted" style="margin-top:8px;">This will remove the bill records and corresponding readings from the database.</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" id="cancel-del-bill-btn">Cancel</button>
        <button class="btn btn-danger" id="confirm-del-bill-btn">Confirm Delete</button>
      </div>
     `;
    openModal(modalHtml, () => {
      document.getElementById('cancel-del-bill-btn').addEventListener('click', closeModal);
      document.getElementById('confirm-del-bill-btn').addEventListener('click', () => {
        const bill = getAll('bills').find(b => b.bill_id === billId);
        if (bill) {
          const readings = getAll('meter_readings');
          const reading = readings.find(r => r.meter_id === bill.meterId && r.month === bill.billingMonth && r.unit_consumed === bill.currReading);
          if (reading) {
            remove('meter_readings', reading.reading_id);
          }
        }
        remove('bills', billId);
        showToast('Bill deleted successfully.', 'success');
        closeModal();
        refreshCallback();
      });
    });
  },

  showEmailLogsModal(openModal, closeModal, showToast) {
    showToast('Loading sent email logs...', 'info');
    fetch('http://localhost:5000/api/email-logs')
      .then(res => res.json())
      .then(logs => {
        const sortedLogs = [...logs].reverse();
        const logsHtml = sortedLogs.length === 0 
          ? `<p class="text-muted" style="text-align:center; padding: 24px;">No sent email logs found.</p>`
          : `
            <div style="max-height: 400px; overflow-y: auto; border: 1px solid var(--border-color); border-radius: 8px;">
              <table class="data-table" style="width:100%; border-collapse:collapse; font-size:0.85rem;">
                <thead>
                  <tr style="position: sticky; top:0; background: var(--bg-tertiary);">
                    <th style="padding: 10px;">Recipient</th>
                    <th style="padding: 10px;">Subject</th>
                    <th style="padding: 10px;">Sent Time</th>
                    <th style="padding: 10px;">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  ${sortedLogs.map(l => `
                    <tr style="border-bottom: 1px solid var(--border-color);">
                      <td style="padding: 10px; font-weight:600;">${l.to}</td>
                      <td style="padding: 10px;">${l.subject}</td>
                      <td style="padding: 10px; font-size:0.75rem; color:var(--text-muted);">${new Date(l.sentAt).toLocaleString()}</td>
                      <td style="padding: 10px;">
                        <div class="action-btn-group">
                          <button class="btn btn-primary preview-email-btn" data-id="${l.id}" style="padding:4px 8px; font-size:0.7rem;">
                            <i class="fa-solid fa-eye"></i> View
                          </button>
                          ${l.etherealUrl ? `
                            <a href="${l.etherealUrl}" target="_blank" class="btn btn-secondary" style="padding:4px 8px; font-size:0.7rem; background: #5a52ff; color:white; border:none; text-decoration:none;">
                              <i class="fa-solid fa-external-link"></i> Live
                            </a>
                          ` : ''}
                        </div>
                      </td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          `;

        const modalHtml = `
          <div class="modal-header">
            <h2>Sent Gmail Reminders Log</h2>
          </div>
          <div style="padding: 10px 0;">
            ${logsHtml}
          </div>
          <div class="modal-footer" style="margin-top:16px;">
            <button class="btn btn-secondary" id="close-email-logs-btn">Close</button>
          </div>
        `;

        openModal(modalHtml, () => {
          document.getElementById('close-email-logs-btn').addEventListener('click', closeModal);
          
          document.querySelectorAll('.preview-email-btn').forEach(btn => {
            btn.addEventListener('click', () => {
              const logId = btn.dataset.id;
              const selectedLog = sortedLogs.find(l => l.id === logId);
              if (selectedLog) {
                const escapeHtml = (str) => {
                  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
                };
                
                const previewHtml = `
                  <div class="modal-header">
                    <h2>Email Content Preview</h2>
                  </div>
                  <div style="padding: 10px 0;">
                    <div style="margin-bottom:12px; font-size:0.85rem; line-height:1.6;">
                      <div><strong>To:</strong> ${selectedLog.to}</div>
                      <div><strong>Subject:</strong> ${selectedLog.subject}</div>
                      <div><strong>Sent At:</strong> ${new Date(selectedLog.sentAt).toLocaleString()}</div>
                    </div>
                    <iframe srcdoc="${escapeHtml(selectedLog.html)}" style="width:100%; height:400px; border:1px solid var(--border-color); background:white; border-radius:8px;"></iframe>
                  </div>
                  <div class="modal-footer" style="margin-top:16px;">
                    <button class="btn btn-secondary" id="close-email-preview-btn">Back to Logs</button>
                  </div>
                `;
                
                openModal(previewHtml, () => {
                  document.getElementById('close-email-preview-btn').addEventListener('click', () => {
                    this.showEmailLogsModal(openModal, closeModal, showToast);
                  });
                });
              }
            });
          });
        });
      })
      .catch(err => {
        console.error(err);
        showToast('Failed to load email logs.', 'danger');
      });
  }
};
