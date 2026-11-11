const API_URL = (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && window.location.port === '8080')
  ? 'http://localhost:5000/api'
  : '/api';
let cachedDB = {};

export const TARIFF_RATES = {
  electricity: { name: 'Electricity', unit: 'kWh', rate: 7.5, baseCharge: 50 },
  water: { name: 'Water', unit: 'm³', rate: 15.0, baseCharge: 30 },
  gas: { name: 'Gas', unit: 'm³', rate: 12.0, baseCharge: 40 },
  wifi: { name: 'WiFi', unit: 'Mbps', rate: 10.0, baseCharge: 300 }
};

const PK_MAP = {
  users: 'id',
  customers: 'customer_id',
  meters: 'meter_id',
  meter_readings: 'reading_id',
  bills: 'bill_id',
  payments: 'payment_id',
  complaints: 'complaint_id',
  notifications: 'id',
  maintenance: 'maintenance_id'
};

// Async initialization function called at app startup
export async function initDBCache() {
  try {
    const res = await fetch(`${API_URL}/db`);
    if (!res.ok) throw new Error('Network response was not ok');
    cachedDB = await res.json();
    console.log('Database cache initialized successfully from backend.');
  } catch (error) {
    console.error('Error fetching database from backend:', error);
    // Fallback: use localStorage if backend is down
    cachedDB = {};
    for (const key of Object.keys(PK_MAP)) {
      const data = localStorage.getItem('utilis_db_' + key);
      cachedDB[key] = data ? JSON.parse(data) : [];
    }
  }
}

// Low-level DB fetching helper
export function getTable(table) {
  return cachedDB[table] || [];
}

// Low-level DB saving helper
export function saveTable(table, data) {
  cachedDB[table] = data;
  
  // Sync to backend
  fetch(`${API_URL}/table/${table}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).catch(err => console.error(`Error syncing table ${table} to backend:`, err));
}

// Fetch all elements in a table
export function getAll(table) {
  return getTable(table);
}

// Fetch by primary key helper
export function getById(table, id) {
  const data = getTable(table);
  const pkName = PK_MAP[table] || 'id';
  return data.find(item => item[pkName] === id) || null;
}

// Add element with PK assignment
export function add(table, item) {
  const data = getTable(table);
  const pkName = PK_MAP[table] || 'id';
  const prefix = table.substring(0, 3);
  const newId = prefix + '-' + Math.floor(100000 + Math.random() * 900000);
  const newItem = { [pkName]: newId, ...item };
  
  data.push(newItem);
  cachedDB[table] = data;

  // Sync to backend asynchronously
  fetch(`${API_URL}/${table}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(newItem)
  }).catch(err => console.error(`Error adding item to ${table}:`, err));

  return newItem;
}

// Update table element helper
export function update(table, id, updatedFields) {
  const data = getTable(table);
  const pkName = PK_MAP[table] || 'id';
  const index = data.findIndex(item => item[pkName] === id);
  if (index !== -1) {
    data[index] = { ...data[index], ...updatedFields };
    cachedDB[table] = data;

    // Sync to backend asynchronously
    fetch(`${API_URL}/${table}/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updatedFields)
    }).catch(err => console.error(`Error updating item ${id} in ${table}:`, err));

    return data[index];
  }
  return null;
}

// Remove table element helper
export function remove(table, id) {
  const data = getTable(table);
  const pkName = PK_MAP[table] || 'id';
  const index = data.findIndex(item => item[pkName] === id);
  if (index !== -1) {
    data.splice(index, 1);
    cachedDB[table] = data;

    // Sync to backend asynchronously
    fetch(`${API_URL}/${table}/${id}`, {
      method: 'DELETE'
    }).catch(err => console.error(`Error deleting item ${id} from ${table}:`, err));

    return true;
  }
  return false;
}

// Notification System Helpers
export function addNotification(userId, message, type = 'info') {
  const notif = {
    userId,
    message,
    type,
    date: new Date().toISOString().split('T')[0],
    isRead: false
  };
  return add('notifications', notif);
}

export function getNotificationsForUser(userId) {
  const notifs = getTable('notifications');
  return notifs.filter(n => n.userId === userId).reverse();
}

export function markAllNotificationsRead(userId) {
  const notifs = getTable('notifications');
  const updated = notifs.map(n => {
    if (n.userId === userId) {
      n.isRead = true;
    }
    return n;
  });
  saveTable('notifications', updated);
}

export function clearNotificationsForUser(userId) {
  const notifs = getTable('notifications');
  const filtered = notifs.filter(n => n.userId !== userId);
  saveTable('notifications', filtered);
}
