const fs = require('fs');
const path = require('path');
const { initDB, query } = require('./db');

async function runMigration() {
  console.log('Starting migration from JSON to MySQL...');
  
  // Initialize tables first
  await initDB();

  const jsonDbPath = path.join(__dirname, 'data', 'db.json');
  if (!fs.existsSync(jsonDbPath)) {
    console.error('No db.json found at: ' + jsonDbPath);
    process.exit(1);
  }

  const jsonDb = JSON.parse(fs.readFileSync(jsonDbPath, 'utf8'));

  try {
    // 1. Users table
    if (jsonDb.users) {
      console.log(`Migrating ${jsonDb.users.length} users...`);
      for (const u of jsonDb.users) {
        await query(
          'INSERT INTO users (id, name, username, email, password, role, status) VALUES (?, ?, ?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE name=VALUES(name), email=VALUES(email), password=VALUES(password), status=VALUES(status)',
          [u.id, u.name, u.username, u.email, u.password, u.role, u.status || 'active']
        );
      }
    }

    // 2. Customers table
    if (jsonDb.customers) {
      console.log(`Migrating ${jsonDb.customers.length} customers...`);
      for (const c of jsonDb.customers) {
        await query(
          'INSERT INTO customers (customer_id, user_id, phone, address) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE phone=VALUES(phone), address=VALUES(address)',
          [c.customer_id, c.user_id, c.phone, c.address]
        );
      }
    }

    // 3. Meters table
    if (jsonDb.meters) {
      console.log(`Migrating ${jsonDb.meters.length} meters...`);
      for (const m of jsonDb.meters) {
        await query(
          'INSERT INTO meters (meter_id, customer_id, meter_number, utilityType, status, installDate) VALUES (?, ?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE customer_id=VALUES(customer_id), status=VALUES(status)',
          [m.meter_id, m.customer_id, m.meter_number, m.utilityType, m.status || 'active', m.installDate]
        );
      }
    }

    // 4. Readings table
    if (jsonDb.meter_readings) {
      console.log(`Migrating ${jsonDb.meter_readings.length} readings...`);
      for (const r of jsonDb.meter_readings) {
        await query(
          'INSERT INTO meter_readings (reading_id, meter_id, month, unit_consumed) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE unit_consumed=VALUES(unit_consumed)',
          [r.reading_id, r.meter_id, r.month, r.unit_consumed]
        );
      }
    }

    // 5. Bills table
    if (jsonDb.bills) {
      console.log(`Migrating ${jsonDb.bills.length} bills...`);
      for (const b of jsonDb.bills) {
        await query(
          'INSERT INTO bills (bill_id, customer_id, amount, due_date, status, billingMonth, billingYear, meterId, prevReading, currReading, consumption, tariffRate, createdAt, paymentDate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE amount=VALUES(amount), status=VALUES(status), paymentDate=VALUES(paymentDate)',
          [b.bill_id, b.customer_id, b.amount, b.due_date, b.status, b.billingMonth, b.billingYear, b.meterId, b.prevReading, b.currReading, b.consumption, b.tariffRate || 8, b.createdAt, b.paymentDate || null]
        );
      }
    }

    // 6. Payments table
    if (jsonDb.payments) {
      console.log(`Migrating ${jsonDb.payments.length} payments...`);
      for (const p of jsonDb.payments) {
        await query(
          'INSERT INTO payments (payment_id, bill_id, amount, payment_date, method, transactionId, status) VALUES (?, ?, ?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE status=VALUES(status)',
          [p.payment_id, p.bill_id, p.amount, p.payment_date, p.method, p.transactionId, p.status]
        );
      }
    }

    // 7. Complaints table
    if (jsonDb.complaints) {
      console.log(`Migrating ${jsonDb.complaints.length} complaints...`);
      for (const c of jsonDb.complaints) {
        await query(
          'INSERT INTO complaints (complaint_id, customer_id, subject, description, status, assignedTo, createdAt, comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE status=VALUES(status), assignedTo=VALUES(assignedTo), comments=VALUES(comments)',
          [c.complaint_id, c.customer_id, c.subject, c.description, c.status, c.assignedTo || null, c.createdAt, JSON.stringify(c.comments || [])]
        );
      }
    }

    // 8. Notifications table
    if (jsonDb.notifications) {
      console.log(`Migrating ${jsonDb.notifications.length} notifications...`);
      for (const n of jsonDb.notifications) {
        const notifId = n.id || `ntf-${Math.floor(100000 + Math.random() * 900000)}`;
        await query(
          'INSERT INTO notifications (id, userId, message, type, date, isRead) VALUES (?, ?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE isRead=VALUES(isRead)',
          [notifId, n.userId, n.message, n.type, n.date, n.isRead ? 1 : 0]
        );
      }
    }

    console.log('Migration completed successfully.');
    process.exit(0);
  } catch (error) {
    console.error('Migration failed:', error);
    process.exit(1);
  }
}

runMigration();
