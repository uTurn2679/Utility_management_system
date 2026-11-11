const mysql = require('mysql2/promise');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });

async function seed() {
  const connection = await mysql.createConnection({
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 3306,
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'utility_management'
  });

  console.log('Connected to MySQL database.');

  const customerId = 'cus-255352';

  // 1. Insert Meters
  const meters = [
    { id: 'met-elec-riya', num: 'MET-223344', type: 'electricity' },
    { id: 'met-water-riya', num: 'MET-334455', type: 'water' },
    { id: 'met-gas-riya', num: 'MET-445566', type: 'gas' }
  ];

  for (const m of meters) {
    await connection.query(
      `INSERT INTO meters (meter_id, customer_id, meter_number, utilityType, status, installDate)
       VALUES (?, ?, ?, ?, 'active', '2026-06-25')
       ON DUPLICATE KEY UPDATE customer_id=VALUES(customer_id)`,
      [m.id, customerId, m.num, m.type]
    );
    console.log(`Meter registered: ${m.id}`);
  }

  // 2. Insert Bills (June, May, April)
  const bills = [
    // June 2026 (Unpaid)
    { id: 'bil-wifi-riya-june', amount: 500, status: 'unpaid', month: 'June', year: '2026', meterId: 'met-149872', prev: 0, curr: 50, consumption: 50, rate: 10, created: '2026-06-25', paidDate: null },
    { id: 'bil-elec-riya-june', amount: 1125, status: 'unpaid', month: 'June', year: '2026', meterId: 'met-elec-riya', prev: 1200, curr: 1350, consumption: 150, rate: 7.5, created: '2026-06-25', paidDate: null },
    { id: 'bil-water-riya-june', amount: 600, status: 'unpaid', month: 'June', year: '2026', meterId: 'met-water-riya', prev: 350, curr: 390, consumption: 40, rate: 15, created: '2026-06-25', paidDate: null },
    { id: 'bil-gas-riya-june', amount: 480, status: 'unpaid', month: 'June', year: '2026', meterId: 'met-gas-riya', prev: 150, curr: 190, consumption: 40, rate: 12, created: '2026-06-25', paidDate: null },

    // May 2026 (Paid)
    { id: 'bil-wifi-riya-may', amount: 500, status: 'paid', month: 'May', year: '2026', meterId: 'met-149872', prev: 0, curr: 50, consumption: 50, rate: 10, created: '2026-05-25', paidDate: '2026-06-01' },
    { id: 'bil-elec-riya-may', amount: 900, status: 'paid', month: 'May', year: '2026', meterId: 'met-elec-riya', prev: 1080, curr: 1200, consumption: 120, rate: 7.5, created: '2026-05-25', paidDate: '2026-06-01' },
    { id: 'bil-water-riya-may', amount: 450, status: 'paid', month: 'May', year: '2026', meterId: 'met-water-riya', prev: 320, curr: 350, consumption: 30, rate: 15, created: '2026-05-25', paidDate: '2026-06-01' },
    { id: 'bil-gas-riya-may', amount: 360, status: 'paid', month: 'May', year: '2026', meterId: 'met-gas-riya', prev: 120, curr: 150, consumption: 30, rate: 12, created: '2026-05-25', paidDate: '2026-06-01' },

    // April 2026 (Paid)
    { id: 'bil-wifi-riya-april', amount: 500, status: 'paid', month: 'April', year: '2026', meterId: 'met-149872', prev: 0, curr: 50, consumption: 50, rate: 10, created: '2026-04-25', paidDate: '2026-05-02' },
    { id: 'bil-elec-riya-april', amount: 1050, status: 'paid', month: 'April', year: '2026', meterId: 'met-elec-riya', prev: 940, curr: 1080, consumption: 140, rate: 7.5, created: '2026-04-25', paidDate: '2026-05-02' },
    { id: 'bil-water-riya-april', amount: 480, status: 'paid', month: 'April', year: '2026', meterId: 'met-water-riya', prev: 288, curr: 320, consumption: 32, rate: 15, created: '2026-04-25', paidDate: '2026-05-02' },
    { id: 'bil-gas-riya-april', amount: 360, status: 'paid', month: 'April', year: '2026', meterId: 'met-gas-riya', prev: 90, curr: 120, consumption: 30, rate: 12, created: '2026-04-25', paidDate: '2026-05-02' }
  ];

  // First delete the temporary june bills we inserted earlier to avoid duplicates with different IDs
  await connection.query("DELETE FROM bills WHERE customer_id = ? AND bill_id IN ('bil-wifi-riya', 'bil-elec-riya', 'bil-water-riya', 'bil-gas-riya')", [customerId]);

  for (const b of bills) {
    await connection.query(
      `INSERT INTO bills (bill_id, customer_id, amount, due_date, status, billingMonth, billingYear, meterId, prevReading, currReading, consumption, tariffRate, createdAt, paymentDate)
       VALUES (?, ?, ?, '2026-07-15', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
       ON DUPLICATE KEY UPDATE amount=VALUES(amount), status=VALUES(status), paymentDate=VALUES(paymentDate)`,
      [b.id, customerId, b.amount, b.status, b.month, b.year, b.meterId, b.prev, b.curr, b.consumption, b.rate, b.created, b.paidDate]
    );
    console.log(`Bill registered: ${b.id}`);
  }

  console.log('Seeding completed successfully.');
  await connection.end();
}

seed().catch(err => console.error(err));
