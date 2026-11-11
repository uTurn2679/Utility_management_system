import { getAll, add, update, addNotification } from '../db.js';

export const PaymentsView = {
  render(container, user, showToast, openModal, closeModal) {
    if (user.role === 'admin') {
      this.renderAdminPortal(container, user, showToast, openModal, closeModal);
    } else {
      this.renderCustomerPortal(container, user, showToast, openModal, closeModal);
    }
  },

  renderAdminPortal(container, user, showToast, openModal, closeModal) {
    const payments = getAll('payments');
    const bills = getAll('bills');
    const customers = getAll('customers');
    const users = getAll('users');

    const totalCollected = payments.reduce((sum, p) => sum + p.amount, 0);

    container.innerHTML = `
      <div class="card-grid">
        <div class="metric-card">
          <div class="metric-details">
            <h3>Total Transactions</h3>
            <div class="metric-val">${payments.length}</div>
          </div>
          <div class="metric-icon"><i class="fa-solid fa-list-check"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>Total Revenue</h3>
            <div class="metric-val">৳${totalCollected.toLocaleString()}</div>
          </div>
          <div class="metric-icon" style="color:var(--success)"><i class="fa-solid fa-money-bill-trend-up"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>Card Collections</h3>
            <div class="metric-val">৳${payments.filter(p => p.method === 'card').reduce((sum, p) => sum + p.amount, 0).toLocaleString()}</div>
          </div>
          <div class="metric-icon" style="color:var(--info)"><i class="fa-solid fa-credit-card"></i></div>
        </div>
        <div class="metric-card">
          <div class="metric-details">
            <h3>Mobile Wallet Pay</h3>
            <div class="metric-val">৳${payments.filter(p => p.method === 'bkash').reduce((sum, p) => sum + p.amount, 0).toLocaleString()}</div>
          </div>
          <div class="metric-icon" style="color:#e21a64;"><i class="fa-solid fa-mobile-screen-button"></i></div>
        </div>
      </div>

      <div class="filter-row">
        <div class="search-wrapper">
          <i class="fa-solid fa-magnifying-glass"></i>
          <input type="text" id="admin-payment-search" placeholder="Search transaction ID or customer...">
        </div>
        <div class="filter-actions">
          <select id="admin-payment-method-filter">
            <option value="">All Methods</option>
            <option value="card">Card</option>
            <option value="bkash">bKash</option>
            <option value="cash">Cash</option>
          </select>
        </div>
      </div>

      <div class="content-card">
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Txn Ref / Date</th>
                <th>Bill Reference</th>
                <th>Customer</th>
                <th>Amount</th>
                <th>Method</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="admin-payments-body">
              <!-- Filled dynamically by JS -->
            </tbody>
          </table>
        </div>
      </div>
    `;

    const populateTable = () => {
      const searchTerm = document.getElementById('admin-payment-search').value.toLowerCase();
      const methodFilter = document.getElementById('admin-payment-method-filter').value;
      const tbody = document.getElementById('admin-payments-body');

      const filtered = payments.filter(p => {
        const bill = bills.find(b => b.bill_id === p.bill_id);
        const customer = bill ? customers.find(c => c.customer_id === bill.customer_id) : null;
        const custUser = customer ? users.find(u => u.id === customer.user_id) : null;

        const matchesSearch = p.transactionId.toLowerCase().includes(searchTerm) || 
                              (custUser ? custUser.name.toLowerCase().includes(searchTerm) : false) || 
                              p.bill_id.toLowerCase().includes(searchTerm);
        const matchesMethod = methodFilter === '' || p.method === methodFilter;
        return matchesSearch && matchesMethod;
      }).reverse();

      if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-muted" style="text-align:center;">No payment records found.</td></tr>`;
        return;
      }

      tbody.innerHTML = filtered.map(p => {
        const bill = bills.find(b => b.bill_id === p.bill_id);
        const customer = bill ? customers.find(c => c.customer_id === bill.customer_id) : null;
        const custUser = customer ? users.find(u => u.id === customer.user_id) : null;
        const status = p.status || 'verified';
        const statusClass = status === 'verified' ? 'success' : 'warning';
        
        const actionBtn = status === 'pending' ? `
          <button class="btn btn-primary verify-payment-btn" data-id="${p.payment_id}" style="padding:6px 12px; font-size:0.75rem;">
            <i class="fa-solid fa-clipboard-check"></i> Verify
          </button>
        ` : `
          <span class="text-muted" style="font-size:0.85rem;"><i class="fa-solid fa-circle-check" style="color:var(--success)"></i> Verified</span>
        `;

        return `
          <tr>
            <td>
              <strong>${p.transactionId}</strong><br>
              <small class="text-muted">${p.payment_date}</small>
            </td>
            <td>
              <strong>${p.bill_id}</strong><br>
              <small class="text-muted">${bill ? `${bill.billingMonth} ${bill.billingYear}` : 'Utility Bill'}</small>
            </td>
            <td>
              <div>${custUser ? custUser.name : 'Unknown'}</div>
              <small class="text-muted">Cust ID: ${bill ? bill.customer_id : 'N/A'}</small>
            </td>
            <td><strong>৳${p.amount}</strong></td>
            <td><span class="badge badge-${p.method === 'cash' ? 'warning' : 'success'}">${p.method.toUpperCase()}</span></td>
            <td><span class="badge badge-${statusClass}">${status.toUpperCase()}</span></td>
            <td>${actionBtn}</td>
          </tr>
        `;
      }).join('');

      tbody.querySelectorAll('.verify-payment-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.showVerifyPaymentModal(btn.dataset.id, openModal, closeModal, showToast, () => {
            this.renderAdminPortal(container, user, showToast, openModal, closeModal);
          });
        });
      });
    };

    populateTable();

    document.getElementById('admin-payment-search').addEventListener('input', populateTable);
    document.getElementById('admin-payment-method-filter').addEventListener('change', populateTable);
  },

  renderCustomerPortal(container, user, showToast, openModal, closeModal) {
    const bills = getAll('bills').filter(b => b.customer_id === user.customerId && (b.status === 'unpaid' || b.status === 'overdue'));
    const payments = getAll('payments').filter(p => {
      const bill = getAll('bills').find(b => b.bill_id === p.bill_id);
      return bill && bill.customer_id === user.customerId;
    });

    container.innerHTML = `
      <div style="display:grid; grid-template-columns: 1.5fr 1fr; gap:24px;">
        <!-- Left Side: Unpaid Bills -->
        <div>
          <h2 style="font-size:1.15rem; margin-bottom:16px;"><i class="fa-solid fa-credit-card"></i> Outstanding Bills</h2>
          <div class="content-card">
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Cycle</th>
                    <th>Due Date</th>
                    <th>Consumption</th>
                    <th>Amount</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody id="unpaid-bills-body">
                  <!-- Filled by JS -->
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Right Side: Recent Transactions -->
        <div>
          <h2 style="font-size:1.15rem; margin-bottom:16px;"><i class="fa-solid fa-clock-rotate-left"></i> Transaction History</h2>
          <div class="content-card">
            <div class="table-responsive" style="max-height: 400px;">
              <table class="data-table" style="font-size:0.8rem;">
                <thead>
                  <tr>
                    <th>Txn ID / Date</th>
                    <th>Amount</th>
                    <th>Method</th>
                  </tr>
                </thead>
                <tbody>
                  ${payments.length === 0 ? `<tr><td colspan="3" class="text-muted text-center" style="text-align:center; padding: 20px;">No transaction logs.</td></tr>` : 
                    payments.map(p => `
                      <tr>
                        <td>
                          <strong>${p.transactionId}</strong><br>
                          <small class="text-muted">${p.payment_date}</small>
                        </td>
                        <td>৳${p.amount}</td>
                        <td><span class="badge badge-success">${p.method.toUpperCase()}</span></td>
                      </tr>
                    `).join('')
                  }
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    `;

    const tbody = document.getElementById('unpaid-bills-body');
    if (bills.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="text-muted" style="text-align:center; padding: 20px;">All bills are fully paid. Awesome!</td></tr>`;
    } else {
      tbody.innerHTML = bills.map(b => `
        <tr>
          <td><strong>${b.billingMonth} ${b.billingYear}</strong></td>
          <td>${b.due_date}</td>
          <td>${b.consumption} units</td>
          <td><strong>৳${b.amount}</strong></td>
          <td>
            <button class="btn btn-primary pay-trigger-btn" data-id="${b.bill_id}" style="padding:6px 12px; font-size:0.75rem;">
              Proceed
            </button>
          </td>
        </tr>
      `).join('');

      tbody.querySelectorAll('.pay-trigger-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          this.showPaymentGatewayModal(btn.dataset.id, openModal, closeModal, showToast, () => {
            this.renderCustomerPortal(container, user, showToast, openModal, closeModal);
          });
        });
      });
    }
  },

  showPaymentGatewayModal(billId, openModal, closeModal, showToast, refreshCallback) {
    const bill = getAll('bills').find(b => b.bill_id === billId);

    const modalHtml = `
      <div class="modal-header">
        <h2>Secure Payment Gateway</h2>
      </div>
      <div style="font-size:0.9rem; margin-bottom:20px; border-bottom:1px solid var(--border-color); padding-bottom:16px;">
        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
          <span class="text-muted">Paying Bill:</span>
          <strong>${bill.billingMonth} ${bill.billingYear}</strong>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:1.1rem; font-weight:700;">
          <span>Total Amount:</span>
          <span style="color:var(--primary)">৳${bill.amount.toLocaleString()}</span>
        </div>
      </div>

      <!-- Payment Method Selection -->
      <div class="payment-selector">
        <div class="payment-method-card active" id="method-card" data-method="card">
          <i class="fa-solid fa-credit-card"></i>
          <div>Credit / Debit Card</div>
        </div>
        <div class="payment-method-card" id="method-bkash" data-method="bkash">
          <i class="fa-solid fa-mobile-screen-button"></i>
          <div>bKash / Mobile Pay</div>
        </div>
      </div>

      <!-- Card input block -->
      <div id="card-gateway-panel">
        <div class="credit-card-ui">
          <div class="chip"></div>
          <div class="card-num" id="preview-card-num">•••• •••• •••• ••••</div>
          <div class="card-meta">
            <div>
              CARDHOLDER NAME
              <h6 id="preview-card-name">JOHN DOE</h6>
            </div>
            <div>
              EXPIRES
              <h6 id="preview-card-expiry">MM/YY</h6>
            </div>
          </div>
        </div>

        <form id="card-payment-form">
          <div class="form-group">
            <label>Cardholder Name</label>
            <input type="text" id="card-name" placeholder="John Doe" required>
          </div>
          <div class="form-group">
            <label>Card Number</label>
            <input type="text" id="card-num" placeholder="4111 2222 3333 4444" maxlength="19" required>
          </div>
          <div class="form-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
            <div>
              <label>Expiry Date</label>
              <input type="text" id="card-expiry" placeholder="MM/YY" maxlength="5" required>
            </div>
            <div>
              <label>CVV</label>
              <input type="password" id="card-cvv" placeholder="•••" maxlength="3" required>
            </div>
          </div>
          <button type="submit" class="btn btn-primary btn-block">Confirm Payment ৳${bill.amount}</button>
        </form>
      </div>

      <!-- bKash input block -->
      <div id="bkash-gateway-panel" class="hidden">
        <div style="background-color:#e21a64; color:white; padding:16px; border-radius:8px; display:flex; align-items:center; gap:12px; margin-bottom:20px;">
          <i class="fa-solid fa-wallet" style="font-size:2rem;"></i>
          <div>
            <h4 style="font-weight:700;">bKash Account Payment</h4>
            <span style="font-size:0.8rem; opacity:0.8;">Verification code will be sent to the phone.</span>
          </div>
        </div>
        <form id="bkash-payment-form">
          <div class="form-group">
            <label>bKash Mobile Number</label>
            <input type="text" id="bkash-phone" placeholder="017XXXXXXXX" maxlength="11" required>
          </div>
          <div class="form-group">
            <label>Verification Code (OTP)</label>
            <input type="text" id="bkash-otp" placeholder="XXXXXX" maxlength="6" required>
          </div>
          <div class="form-group">
            <label>bKash PIN</label>
            <input type="password" id="bkash-pin" placeholder="•••••" maxlength="5" required>
          </div>
          <button type="submit" class="btn btn-primary btn-block" style="background:#e21a64; border:none; color:white;">Pay with bKash ৳${bill.amount}</button>
        </form>
      </div>

      <!-- Processing state -->
      <div id="payment-processing-panel" class="hidden" style="text-align:center; padding:40px 0;">
        <i class="fa-solid fa-spinner fa-spin-pulse" style="font-size:3.5rem; color:var(--primary); margin-bottom:20px;"></i>
        <h3>Authorizing Transaction...</h3>
        <p class="text-muted" style="font-size:0.85rem; margin-top:8px;">Please do not close this window or reload the page.</p>
      </div>
    `;

    openModal(modalHtml, () => {
      const cardPanel = document.getElementById('card-gateway-panel');
      const bkashPanel = document.getElementById('bkash-gateway-panel');
      const processingPanel = document.getElementById('payment-processing-panel');
      const cardMethod = document.getElementById('method-card');
      const bkashMethod = document.getElementById('method-bkash');

      cardMethod.addEventListener('click', () => {
        cardMethod.classList.add('active');
        bkashMethod.classList.remove('active');
        cardPanel.classList.remove('hidden');
        bkashPanel.classList.add('hidden');
      });

      bkashMethod.addEventListener('click', () => {
        bkashMethod.classList.add('active');
        cardMethod.classList.remove('active');
        bkashPanel.classList.remove('hidden');
        cardPanel.classList.add('hidden');
      });

      const nameInput = document.getElementById('card-name');
      const numInput = document.getElementById('card-num');
      const expiryInput = document.getElementById('card-expiry');

      nameInput.addEventListener('input', (e) => {
        document.getElementById('preview-card-name').textContent = e.target.value.toUpperCase() || 'JOHN DOE';
      });

      numInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
        let matches = value.match(/\d{4,16}/g);
        let match = matches && matches[0] || '';
        let parts = [];

        for (let i=0, len=match.length; i<len; i+=4) {
          parts.push(match.substring(i, i+4));
        }

        if (parts.length > 0) {
          e.target.value = parts.join(' ');
        } else {
          e.target.value = value;
        }

        document.getElementById('preview-card-num').textContent = e.target.value || '•••• •••• •••• ••••';
      });

      expiryInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
        if (value.length >= 2) {
          e.target.value = value.substring(0,2) + '/' + value.substring(2,4);
        } else {
          e.target.value = value;
        }
        document.getElementById('preview-card-expiry').textContent = e.target.value || 'MM/YY';
      });

      const handlePaymentSuccess = (methodName) => {
        cardPanel.classList.add('hidden');
        bkashPanel.classList.add('hidden');
        processingPanel.classList.remove('hidden');

        setTimeout(() => {
          const txnId = 'TXN-' + Math.floor(10000000 + Math.random() * 90000000);
          const today = new Date().toISOString().split('T')[0];

          add('payments', {
            bill_id: bill.bill_id,
            amount: bill.amount,
            payment_date: today,
            method: methodName,
            transactionId: txnId,
            status: 'pending'
          });

          update('bills', bill.bill_id, {
            status: 'paid',
            paymentDate: today
          });

          const customer = getAll('customers').find(c => c.customer_id === bill.customer_id);
          if (customer) {
            addNotification(customer.user_id, `Payment of ৳${bill.amount} received via ${methodName.toUpperCase()} for ${bill.billingMonth} ${bill.billingYear} bill. Trans-ID: ${txnId}`, 'success');
          }

          showToast('Payment successful!', 'success');
          closeModal();
          refreshCallback();
        }, 1500);
      };

      document.getElementById('card-payment-form').addEventListener('submit', (e) => {
        e.preventDefault();
        handlePaymentSuccess('card');
      });

      document.getElementById('bkash-payment-form').addEventListener('submit', (e) => {
        e.preventDefault();
        handlePaymentSuccess('bkash');
      });
    });
  },

  showVerifyPaymentModal(paymentId, openModal, closeModal, showToast, refreshCallback) {
    const payment = getAll('payments').find(p => p.payment_id === paymentId);
    if (!payment) return;

    const bill = getAll('bills').find(b => b.bill_id === payment.bill_id);
    const customer = getAll('customers').find(c => c.customer_id === (bill ? bill.customer_id : ''));
    const custUser = customer ? getAll('users').find(u => u.id === customer.user_id) : null;

    const modalHtml = `
      <div class="modal-header">
        <h2>Verify Payment Transaction</h2>
      </div>
      <div style="font-size:0.9rem; margin-bottom:20px; line-height: 1.6;">
        <div style="display:flex; justify-content:space-between; margin-bottom:8px; border-bottom: 1px solid var(--border-color); padding-bottom: 6px;">
          <span class="text-muted">Transaction ID:</span>
          <strong>${payment.transactionId}</strong>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <span class="text-muted">Customer Name:</span>
          <strong>${custUser ? custUser.name : 'Unknown'}</strong>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <span class="text-muted">Utility Bill:</span>
          <strong>${bill ? `${bill.billingMonth} ${bill.billingYear}` : 'N/A'} (ID: ${payment.bill_id})</strong>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <span class="text-muted">Payment Method:</span>
          <span class="badge badge-success">${payment.method.toUpperCase()}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <span class="text-muted">Payment Date:</span>
          <strong>${payment.payment_date}</strong>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:1.1rem; font-weight:700; margin-top:12px; border-top: 2px dashed var(--border-color); padding-top: 10px;">
          <span>Amount Paid:</span>
          <span style="color:var(--primary)">৳${payment.amount.toLocaleString()}</span>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" id="cancel-verify-btn">Cancel</button>
        <button type="button" class="btn btn-primary" id="confirm-verify-btn">Confirm & Verify</button>
      </div>
    `;

    openModal(modalHtml, () => {
      document.getElementById('cancel-verify-btn').addEventListener('click', closeModal);
      document.getElementById('confirm-verify-btn').addEventListener('click', () => {
        update('payments', paymentId, { status: 'verified' });
        showToast('Payment transaction verified successfully!', 'success');
        closeModal();
        refreshCallback();
      });
    });
  }
};
