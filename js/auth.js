import { getAll, add, addNotification } from './db.js';

const SESSION_KEY = 'utilis_session_user';

// Check if user is currently logged in
export function getCurrentUser() {
  const sessionUser = sessionStorage.getItem(SESSION_KEY);
  return sessionUser ? JSON.parse(sessionUser) : null;
}

// Log in user
export function login(username, password) {
  const users = getAll('users');
  const user = users.find(u => (u.username === username || u.email === username) && u.password === password);

  if (!user) {
    throw new Error('Invalid username or password.');
  }

  let customerId = null;
  let meterId = null;

  // Retrieve customer data if role is customer
  if (user.role === 'customer') {
    const customers = getAll('customers');
    const customer = customers.find(c => c.user_id === user.id);
    if (customer) {
      customerId = customer.customer_id;
      const meters = getAll('meters');
      const meter = meters.find(m => m.customer_id === customerId);
      if (meter) {
        meterId = meter.meter_id;
      }
    }
  }

  // Set session
  const sessionUser = {
    id: user.id,
    username: user.username,
    name: user.name,
    role: user.role,
    email: user.email,
    customerId: customerId,
    meterId: meterId
  };
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(sessionUser));
  return sessionUser;
}

// Register a customer
export function register(name, username, email, password, meterNumber = '', phone = '', address = '') {
  const users = getAll('users');
  const meters = getAll('meters');

  // Validations
  if (users.some(u => u.username === username)) {
    throw new Error('Username is already taken.');
  }

  if (users.some(u => u.email === email)) {
    throw new Error('Email is already registered.');
  }

  let meterId = null;

  // If a meter serial is provided, try to find and link it
  if (meterNumber && meterNumber.trim() !== '') {
    const meter = meters.find(m => m.meter_number.toUpperCase() === meterNumber.trim().toUpperCase());
    if (!meter) {
      throw new Error(`Meter Number ${meterNumber} not found. Please verify the serial number.`);
    }
    if (meter.customer_id) {
      throw new Error(`Meter Number ${meterNumber} is already assigned to another customer.`);
    }
    meterId = meter.meter_id;
  }

  // 1. Create user
  const newUser = {
    name,
    username,
    email,
    password,
    role: 'customer'
  };
  const createdUser = add('users', newUser);

  // 2. Create customer
  const newCustomer = {
    user_id: createdUser.id,
    phone: phone || 'Not Provided',
    address: address || 'Not Provided'
  };
  const createdCustomer = add('customers', newCustomer);

  // 3. Link meter to customer if found
  if (meterId) {
    const metersList = getAll('meters');
    const mIndex = metersList.findIndex(m => m.meter_id === meterId);
    if (mIndex !== -1) {
      metersList[mIndex].customer_id = createdCustomer.customer_id;
      localStorage.setItem('utilis_db_meters', JSON.stringify(metersList));
    }
  }

  // Send admin notification
  const admins = users.filter(u => u.role === 'admin');
  admins.forEach(admin => {
    addNotification(admin.id, `New customer registered: ${name} (${username})`, 'info');
  });

  return createdUser;
}

// Log out user
export function logout() {
  sessionStorage.removeItem(SESSION_KEY);
  window.location.hash = '';
  window.location.reload();
}
