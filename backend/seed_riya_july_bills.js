const mysql = require('mysql2/promise');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });

async function seedJulyBills() {
  const connection = await mysql.createConnection({
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 3306,
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'utility_management'
  });

  console.log('Connected to MySQL database.');

  const customerId = 'cus-255352'; // Riya's customer ID

  // July 2026 Unpaid Bills
  const bills = [
    {
      id: 'bil-wifi-riya-july-new',
      amount: 500,
      status: 'unpaid',
      month: 'July',
      year: '2026',
      meterId: 'met-149872', // Wifi meter
      prev: 700,
      curr: 750,
      consumption: 50,
      rate: 10,
      created: '2026-07-14',
      dueDate: '2026-08-15'
    },
    {
      id: 'bil-water-riya-july-new',
      amount: 600,
      status: 'unpaid',
      month: 'July',
      year: '2026',
      meterId: 'met-water-riya', // Water meter
      prev: 390,
      curr: 430,
      consumption: 40,
      rate: 15,
      created: '2026-07-14',
      dueDate: '2026-08-15'
    },
    {
      id: 'bil-gas-riya-july-new',
      amount: 480,
      status: 'unpaid',
      month: 'July',
      year: '2026',
      meterId: 'met-gas-riya', // Gas meter
      prev: 190,
      curr: 230,
      consumption: 40,
      rate: 12,
      created: '2026-07-14',
      dueDate: '2026-08-15'
    }
  ];

  for (const b of bills) {
    await connection.query(
      `INSERT INTO bills (bill_id, customer_id, amount, due_date, status, billingMonth, billingYear, meterId, prevReading, currReading, consumption, tariffRate, createdAt, paymentDate)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
       ON DUPLICATE KEY UPDATE amount=VALUES(amount), status=VALUES(status), due_date=VALUES(due_date), prevReading=VALUES(prevReading), currReading=VALUES(currReading), consumption=VALUES(consumption), tariffRate=VALUES(tariffRate)`,
      [b.id, customerId, b.amount, b.dueDate, b.status, b.month, b.year, b.meterId, b.prev, b.curr, b.consumption, b.rate, b.created]
    );
    console.log(`Unpaid July bill registered: ${b.id} for utility type ${b.meterId}`);
  }

  console.log('July unpaid bills seeding completed successfully.');
  await connection.end();
}

seedJulyBills().catch(err => {
  console.error('Error seeding July bills:', err);
  process.exit(1);
});
