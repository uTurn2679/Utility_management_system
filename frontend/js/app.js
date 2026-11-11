// ==========================================================================
// SPA APPLICATION LIFE CYCLE & ROUTER CONTROLLER (UI DESIGN)
// ==========================================================================

import { getCurrentUser, login, register, logout } from './auth.js';
import { initDBCache, getAll, getNotificationsForUser, markAllNotificationsRead, clearNotificationsForUser } from './db.js';

// Import Views
import { DashboardView } from './components/dashboard.js';
import { CustomersView } from './components/customers.js';
import { MetersView } from './components/meters.js';
import { BillsView } from './components/bills.js';
import { PaymentsView } from './components/payments.js';
import { ComplaintsView } from './components/complaints.js';
import { ProfileView } from './components/profile.js';
import { ReportsView } from './components/reports.js';
import { MaintenanceView } from './components/maintenance.js';
import { GisView } from './components/gis.js';

// Route Definitions Registry
const VIEWS = {
  dashboard: { component: DashboardView, roles: ['admin', 'employee', 'customer'] },
  customers: { component: CustomersView, roles: ['admin'] },
  meters: { component: MetersView, roles: ['admin', 'employee'] },
  bills: { component: BillsView, roles: ['admin', 'employee', 'customer'] },
  payments: { component: PaymentsView, roles: ['customer'] },
  'admin-payments': { component: PaymentsView, roles: ['admin'] },
  complaints: { component: ComplaintsView, roles: ['admin', 'employee', 'customer'] },
  profile: { component: ProfileView, roles: ['customer'] },
  reports: { component: ReportsView, roles: ['admin'] },
  maintenance: { component: MaintenanceView, roles: ['admin', 'employee', 'customer'] },
  gis: { component: GisView, roles: ['admin'] }
};

// Application state tracker
let currentUser = null;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', async () => {
  await initDBCache();
  currentUser = getCurrentUser();
  initApp();
});

function initApp() {
  setupGlobalDate();

  if (!currentUser) {
    showAuthPortal();
  } else {
    showDashboardPortal();
  }
}

// Set up UI Date
function setupGlobalDate() {
  const dateSpan = document.getElementById('header-current-date');
  if (dateSpan) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    dateSpan.textContent = new Date().toLocaleDateString('en-US', options);
  }
}

/* ==========================================================================
   AUTHENTICATION & LANDING PAGE WIRING
   ========================================================================== */
function showAuthPortal() {
  document.getElementById('auth-view').classList.remove('hidden');
  document.getElementById('app-view').classList.add('hidden');

  // Landing Page Tabs Switching
  const btnHome = document.getElementById('btn-tab-home');
  const btnAbout = document.getElementById('btn-tab-about');
  const btnContact = document.getElementById('btn-tab-contact');

  const secHome = document.getElementById('section-home');
  const secAbout = document.getElementById('section-about');
  const secContact = document.getElementById('section-contact');

  const switchTab = (activeBtn, activeSec) => {
    [btnHome, btnAbout, btnContact].forEach(b => b.classList.remove('active'));
    [secHome, secAbout, secContact].forEach(s => s.classList.add('hidden'));

    activeBtn.classList.add('active');
    activeSec.classList.remove('hidden');
  };

  btnHome.addEventListener('click', () => switchTab(btnHome, secHome));
  btnAbout.addEventListener('click', () => switchTab(btnAbout, secAbout));
  btnContact.addEventListener('click', () => switchTab(btnContact, secContact));

  // Hero section buttons
  document.getElementById('hero-learn-more-btn').addEventListener('click', () => btnAbout.click());
  document.getElementById('hero-get-started-btn').addEventListener('click', () => {
    document.getElementById('auth-modal-overlay').classList.remove('hidden');
  });

  // Modal actions
  const authModal = document.getElementById('auth-modal-overlay');
  document.getElementById('open-login-modal-btn').addEventListener('click', () => {
    authModal.classList.remove('hidden');
  });
  document.getElementById('close-auth-modal-btn').addEventListener('click', () => {
    authModal.classList.add('hidden');
  });

  // Toggle Password Visibilities
  setupPasswordToggle('toggle-login-password', 'login-password');
  setupPasswordToggle('toggle-reg-password', 'reg-password');

  // Form toggle switches
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const authTitle = document.getElementById('auth-title');
  const authSubtitle = document.getElementById('auth-subtitle');
  const switchLink = document.getElementById('auth-switch-link');
  const switchText = document.getElementById('auth-switch-text');

  switchLink.addEventListener('click', (e) => {
    e.preventDefault();
    if (loginForm.classList.contains('hidden')) {
      loginForm.classList.remove('hidden');
      registerForm.classList.add('hidden');
      authTitle.textContent = 'Welcome Back';
      authSubtitle.textContent = 'Sign in to access your utility dashboard';
      switchText.textContent = "Don't have an account?";
      switchLink.textContent = 'Sign Up';
    } else {
      loginForm.classList.add('hidden');
      registerForm.classList.remove('hidden');
      authTitle.textContent = 'Create Account';
      authSubtitle.textContent = 'Register to monitor meters and pay bills';
      switchText.textContent = 'Already have an account?';
      switchLink.textContent = 'Sign In';
    }
  });

  // Public Contact Form submit
  document.getElementById('public-contact-form').addEventListener('submit', (e) => {
    e.preventDefault();
    showToast('Your message has been sent successfully. We will get back to you!', 'success');
    document.getElementById('public-contact-form').reset();
  });

  // Login Submit
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const pass = document.getElementById('login-password').value;

    try {
      currentUser = login(username, pass);
      authModal.classList.add('hidden');
      showToast('Logged in successfully', 'success');
      showDashboardPortal();
    } catch (err) {
      showToast(err.message, 'danger');
    }
  });

  // Register Submit
  registerForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('reg-fullname').value.trim();
    const username = document.getElementById('reg-username').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const phone = document.getElementById('reg-phone').value.trim();
    const address = document.getElementById('reg-address').value.trim();
    const meterSerial = document.getElementById('reg-meter').value.trim();

    try {
      register(name, username, email, password, meterSerial, phone, address);
      showToast('Registration successful! Please sign in.', 'success');
      switchLink.click();
    } catch (err) {
      showToast(err.message, 'danger');
    }
  });
}

function setupPasswordToggle(btnId, inputId) {
  const btn = document.getElementById(btnId);
  const input = document.getElementById(inputId);
  if (btn && input) {
    btn.addEventListener('click', () => {
      const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
      input.setAttribute('type', type);
      const icon = btn.querySelector('i');
      icon.classList.toggle('fa-eye');
      icon.classList.toggle('fa-eye-slash');
    });
  }
}

/* ==========================================================================
   DASHBOARD PORTAL WIRING
   ========================================================================== */
function showDashboardPortal() {
  document.getElementById('auth-view').classList.add('hidden');
  document.getElementById('app-view').classList.remove('hidden');

  // Load User Details
  document.getElementById('user-display-name').textContent = currentUser.name;
  document.getElementById('user-role-badge').textContent = currentUser.role;
  document.getElementById('user-avatar-initial').textContent = currentUser.name.charAt(0).toUpperCase();

  // Populate Sidebar Links Based on Roles
  populateSidebar();

  // Setup Notifications & Bell
  initNotifications();

  // Wire Sidebar Actions (mobile toggle)
  setupSidebarToggles();

  // Logout listener
  document.getElementById('logout-btn').addEventListener('click', () => {
    logout();
  });

  // Start Router listeners
  window.addEventListener('hashchange', handleRouting);

  // Set default initial view
  if (!window.location.hash) {
    window.location.hash = '#/dashboard';
  } else {
    handleRouting();
  }
}

// Side bar builder based on roles
function populateSidebar() {
  const menu = document.getElementById('sidebar-menu');
  let links = [
    { name: 'Dashboard', hash: '#/dashboard', icon: 'fa-chart-pie', roles: ['admin', 'employee', 'customer'] },
    { name: 'Customers', hash: '#/customers', icon: 'fa-users', roles: ['admin'] },
    { name: 'Meters', hash: '#/meters', icon: 'fa-gauge-high', roles: ['admin', 'employee'] },
    { name: 'Bills', hash: '#/bills', icon: 'fa-file-invoice-dollar', roles: ['admin', 'employee', 'customer'] },
    { name: 'My Payments', hash: '#/payments', icon: 'fa-credit-card', roles: ['customer'] },
    { name: 'Manage Payments', hash: '#/admin-payments', icon: 'fa-file-shield', roles: ['admin'] },
    { name: 'Complaints', hash: '#/complaints', icon: 'fa-circle-question', roles: ['admin', 'employee', 'customer'] },
    { name: 'Maintenance Requests', hash: '#/maintenance', icon: 'fa-screwdriver-wrench', roles: ['admin', 'employee', 'customer'] },
    { name: 'GIS Analytics', hash: '#/gis', icon: 'fa-map-location-dot', roles: ['admin'] },
    { name: 'Profile', hash: '#/profile', icon: 'fa-user-gear', roles: ['customer'] },
    { name: 'Reports', hash: '#/reports', icon: 'fa-chart-line', roles: ['admin'] }
  ];

  menu.innerHTML = links
    .filter(link => link.roles.includes(currentUser.role))
    .map(link => `
      <li>
        <a href="${link.hash}" class="nav-link" id="nav-${link.hash.substring(2)}">
          <i class="fa-solid ${link.icon}"></i>
          <span>${link.name}</span>
        </a>
      </li>
    `).join('');
}

// Sidebar responsiveness togglers
function setupSidebarToggles() {
  const sidebar = document.querySelector('.sidebar');
  const toggleBtn = document.getElementById('toggle-sidebar');
  const closeBtn = document.getElementById('close-sidebar');

  toggleBtn.addEventListener('click', () => {
    sidebar.classList.add('active');
  });

  closeBtn.addEventListener('click', () => {
    sidebar.classList.remove('active');
  });

  // Auto close sidebar on nav link click (mobile responsive workflow)
  document.getElementById('sidebar-menu').addEventListener('click', (e) => {
    if (e.target.closest('.nav-link')) {
      sidebar.classList.remove('active');
    }
  });
}

// Notifications trigger dropdown handler
function initNotifications() {
  const bell = document.getElementById('notif-bell-btn');
  const countBadge = document.getElementById('notif-count');
  const dropdown = document.getElementById('notif-dropdown');
  const list = document.getElementById('notif-list');
  const clearBtn = document.getElementById('clear-notifs-btn');

  const updateNotifBadge = () => {
    const listData = getNotificationsForUser(currentUser.id);
    const unread = listData.filter(n => !n.isRead).length;

    if (unread > 0) {
      countBadge.textContent = unread;
      countBadge.classList.remove('hidden');
    } else {
      countBadge.classList.add('hidden');
    }

    if (listData.length === 0) {
      list.innerHTML = `<div class="notif-empty">No notifications yet.</div>`;
      return;
    }

    list.innerHTML = listData.map(n => {
      let icon = 'info';
      if (n.type === 'success') icon = 'circle-check';
      if (n.type === 'warning') icon = 'triangle-exclamation';

      return `
        <div class="notif-item ${n.isRead ? '' : 'unread'}" style="${n.isRead ? '' : 'background-color:rgba(0, 242, 254, 0.03)'}">
          <div class="notif-icon ${n.type}"><i class="fa-solid fa-${icon}"></i></div>
          <div class="notif-body">
            <p>${n.message}</p>
            <span>${n.date}</span>
          </div>
        </div>
      `;
    }).join('');
  };

  updateNotifBadge();

  // Toggle notifications display
  bell.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('hidden');
    if (!dropdown.classList.contains('hidden')) {
      // Mark all read
      markAllNotificationsRead(currentUser.id);
      updateNotifBadge();
    }
  });

  document.addEventListener('click', () => {
    dropdown.classList.add('hidden');
  });

  clearBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    clearNotificationsForUser(currentUser.id);
    updateNotifBadge();
    showToast('Notifications cleared', 'info');
  });
}

/* ==========================================================================
   ROUTING DISPATCHER
   ========================================================================== */
function handleRouting() {
  const rawHash = window.location.hash;

  if (rawHash && rawHash.startsWith('#/public-bill-view')) {
    // Hide standard views
    document.getElementById('auth-view').classList.add('hidden');
    document.getElementById('app-view').classList.add('hidden');
    
    const container = document.getElementById('public-bill-view-container');
    const body = document.getElementById('public-bill-body');
    container.classList.remove('hidden');
    
    let billId = '';
    const parts = rawHash.split('?');
    if (parts.length > 1) {
      const queryStr = parts[1];
      const params = new URLSearchParams(queryStr);
      billId = params.get('id');
    }
    
    const bills = getAll('bills');
    const bill = bills.find(b => b.bill_id === billId);
    
    if (!bill) {
      body.innerHTML = `
        <div style="text-align:center; padding:30px;">
          <i class="fa-solid fa-triangle-exclamation text-danger" style="font-size:3rem; margin-bottom:16px;"></i>
          <h3>Invoice Not Found</h3>
          <p class="text-muted" style="margin-top:8px;">The requested invoice ID (${billId || 'N/A'}) could not be verified.</p>
        </div>
      `;
      return;
    }
    
    const customer = getAll('customers').find(c => c.customer_id === bill.customer_id);
    const custUser = customer ? getAll('users').find(u => u.id === customer.user_id) : null;
    const meter = getAll('meters').find(m => m.meter_id === bill.meterId);
    
    body.innerHTML = `
      <div class="modal-header" style="border-bottom: 2px dashed var(--border-color); padding-bottom: 12px; margin-bottom: 16px;">
        <h2 style="display:flex; justify-content:space-between; align-items:center; width:100%;">
          <span>Utility Invoice Details</span>
          <span class="badge badge-${bill.status === 'paid' ? 'success' : 'danger'}" style="font-size:0.75rem;">${bill.status.toUpperCase()}</span>
        </h2>
      </div>
      <div style="font-family: var(--font-secondary); font-size: 0.85rem; line-height: 1.6;">
        <table style="width:100%; border-collapse:collapse; margin-bottom: 20px;">
          <tr>
            <td style="padding:4px 0;"><strong>Invoice ID:</strong></td>
            <td style="padding:4px 0;">${bill.bill_id}</td>
          </tr>
          <tr>
            <td style="padding:4px 0;"><strong>Customer Name:</strong></td>
            <td style="padding:4px 0;">${custUser ? custUser.name : 'N/A'}</td>
          </tr>
          <tr>
            <td style="padding:4px 0;"><strong>Meter Number:</strong></td>
            <td style="padding:4px 0;">${meter ? `${meter.meter_number} (${meter.utilityType.toUpperCase()})` : 'N/A'}</td>
          </tr>
          <tr>
            <td style="padding:4px 0;"><strong>Billing Period:</strong></td>
            <td style="padding:4px 0;">${bill.billingMonth} ${bill.billingYear}</td>
          </tr>
          <tr>
            <td style="padding:4px 0;"><strong>Due Date:</strong></td>
            <td style="padding:4px 0;">${bill.due_date}</td>
          </tr>
          ${bill.paymentDate ? `<tr><td style="padding:4px 0;"><strong>Payment Date:</strong></td><td style="padding:4px 0;">${bill.paymentDate}</td></tr>` : ''}
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

        <div style="display:flex; justify-content:space-between; font-size:1.15rem; font-weight:700;">
          <span>Net Payable Amount:</span>
          <span>৳${bill.amount.toLocaleString()}</span>
        </div>
      </div>
    `;
    return;
  } else {
    const pubContainer = document.getElementById('public-bill-view-container');
    if (pubContainer) pubContainer.classList.add('hidden');
  }

  if (!currentUser) return;

  let path = 'dashboard';

  if (rawHash && rawHash.startsWith('#/')) {
    path = rawHash.substring(2);
  }

  if (path.includes('?')) {
    path = path.split('?')[0];
  }

  // Highlight Active Link in Navbar sidebar
  document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
  const activeLink = document.getElementById(`nav-${path}`);
  if (activeLink) activeLink.classList.add('active');

  const container = document.getElementById('main-content');
  const titleHeader = document.getElementById('page-title');

  // Verify routing matching rules & permissions
  const route = VIEWS[path];
  if (route) {
    // Check permission boundaries
    if (!route.roles.includes(currentUser.role)) {
      titleHeader.textContent = 'Access Denied';
      container.innerHTML = `
        <div class="content-card" style="text-align:center; padding: 60px 24px;">
          <i class="fa-solid fa-triangle-exclamation" style="font-size:4rem; color:var(--danger); margin-bottom:16px;"></i>
          <h2>Permission Denied</h2>
          <p class="text-muted" style="margin-top:8px;">Your account role (${currentUser.role.toUpperCase()}) is not authorized to access the requested module: <strong>#/${path}</strong>.</p>
        </div>
      `;
      return;
    }

    let cleanTitle = path.replace('-', ' ');
    titleHeader.textContent = cleanTitle.charAt(0).toUpperCase() + cleanTitle.slice(1);
    container.innerHTML = `<div style="text-align:center; padding:100px 0;"><i class="fa-solid fa-spinner fa-spin-pulse" style="font-size:2.5rem; color:var(--primary)"></i></div>`;
    
    setTimeout(() => {
      route.component.render(container, currentUser, showToast, openModal, closeModal);
    }, 150);
  } else {
    titleHeader.textContent = '404 - Not Found';
    container.innerHTML = `
      <div class="content-card" style="text-align:center; padding: 60px 24px;">
        <i class="fa-solid fa-face-frown" style="font-size:4rem; color:var(--text-muted); margin-bottom:16px;"></i>
        <h2>Page Not Found</h2>
        <p class="text-muted" style="margin-top:8px; margin-bottom:20px;">The resource you requested doesn't exist.</p>
        <a href="#/dashboard" class="btn btn-primary">Return Home</a>
      </div>
    `;
  }
}

/* ==========================================================================
   GLOBAL UI HELPER ACTIONS (MODALS & TOASTS)
   ========================================================================== */
export function openModal(htmlContent, setupEventsCallback) {
  const overlay = document.getElementById('modal-overlay');
  const body = document.getElementById('modal-body');
  const closeBtn = document.getElementById('modal-close-btn');

  body.innerHTML = htmlContent;
  overlay.classList.remove('hidden');

  const hideModal = () => {
    overlay.classList.add('hidden');
    body.innerHTML = '';
  };

  closeBtn.onclick = hideModal;

  if (setupEventsCallback) {
    setupEventsCallback();
  }
}

export function closeModal() {
  document.getElementById('modal-overlay').classList.add('hidden');
  document.getElementById('modal-body').innerHTML = '';
}

export function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  let icon = 'info';
  if (type === 'success') icon = 'circle-check';
  if (type === 'warning') icon = 'triangle-exclamation';
  if (type === 'danger') icon = 'circle-xmark';

  toast.innerHTML = `
    <i class="fa-solid fa-${icon} toast-icon"></i>
    <span class="toast-message">${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}
