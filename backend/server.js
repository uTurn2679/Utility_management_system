const express = require('express');
const cors = require('cors');
const { initDB, getFullDB, saveTable, insertItem, updateItem, deleteItem } = require('./db');
const { setPool, notifyNewBill, checkAndNotifyUpcomingBills } = require('./notificationHelper');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

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

// Endpoints
app.get('/api/db', async (req, res) => {
  try {
    const db = await getFullDB();
    res.json(db);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Update entire table (e.g. for re-assigning meter list directly in localStorage helper)
app.post('/api/table/:table', async (req, res) => {
  try {
    const { table } = req.params;
    await saveTable(table, req.body);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/send-bill-reminder', async (req, res) => {
  try {
    const { billId } = req.body;
    const { getPool } = require('./db');
    const pool = getPool();
    
    // Fetch bill details
    const [billRows] = await pool.query('SELECT * FROM bills WHERE bill_id = ?', [billId]);
    if (billRows.length === 0) {
      return res.status(404).json({ error: 'Bill not found' });
    }
    const bill = billRows[0];
    
    // Fetch customer and user details
    const [custRows] = await pool.query('SELECT * FROM customers WHERE customer_id = ?', [bill.customer_id]);
    if (custRows.length === 0) {
      return res.status(404).json({ error: 'Customer not found' });
    }
    
    const [userRows] = await pool.query('SELECT * FROM users WHERE id = ?', [custRows[0].user_id]);
    if (userRows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    const email = userRows[0].email;
    const name = userRows[0].name;
    
    const [meterRows] = await pool.query('SELECT utilityType FROM meters WHERE meter_id = ?', [bill.meterId]);
    const utilityType = meterRows.length > 0 ? meterRows[0].utilityType : 'Utility';
    
    const subject = `URGENT: Unpaid Bill Reminder - ${utilityType.toUpperCase()} - ${bill.billingMonth} ${bill.billingYear}`;
    const html = `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ff5e62; border-radius: 8px;">
        <h2 style="color: #ff5e62; text-align: center;">Unpaid Utility Bill Notice</h2>
        <p>Dear <strong>${name}</strong>,</p>
        <p>This is a notice that your utility bill for <strong>${bill.billingMonth} ${bill.billingYear}</strong> remains unpaid.</p>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
          <tr style="background-color: #f8f9fa;">
            <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Invoice ID</th>
            <td style="padding: 10px; border: 1px solid #e0e0e0;">${bill.bill_id}</td>
          </tr>
          <tr>
            <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Utility Type</th>
            <td style="padding: 10px; border: 1px solid #e0e0e0;">${utilityType.toUpperCase()}</td>
          </tr>
          <tr style="background-color: #f8f9fa; font-weight: bold;">
            <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Amount Due</th>
            <td style="padding: 10px; border: 1px solid #e0e0e0; color: #ff5e62;">৳${bill.amount}</td>
          </tr>
          <tr>
            <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Due Date</th>
            <td style="padding: 10px; border: 1px solid #e0e0e0; font-weight: bold; color: #ff5e62;">${bill.due_date}</td>
          </tr>
        </table>
        
        <p style="text-align: center; margin-top: 30px;">
          <a href="http://localhost:8080/#/public-bill-view?id=${bill.bill_id}" style="background-color: #ff5e62; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Pay Bill Now</a>
        </p>
        
        <hr style="border: 0; border-top: 1px solid #e0e0e0; margin-top: 30px;">
        <p style="font-size: 0.8rem; color: #888; text-align: center;">Please ignore this if you have already completed the payment.</p>
      </div>
    `;
    
    const { sendMail } = require('./emailService');
    const result = await sendMail(email, subject, html);
    
    res.json({ success: true, email, result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/run-due-reminders', async (req, res) => {
  try {
    const count = await checkAndNotifyUpcomingBills();
    res.json({ success: true, count, message: `Upcoming due alerts check complete. Emails sent: ${count}` });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/email-logs', (req, res) => {
  const path = require('path');
  const fs = require('fs');
  const JSON_LOG = path.join(__dirname, 'data', 'sent_emails.json');
  if (fs.existsSync(JSON_LOG)) {
    try {
      const logs = JSON.parse(fs.readFileSync(JSON_LOG, 'utf8'));
      res.json(logs);
    } catch (e) {
      res.json([]);
    }
  } else {
    res.json([]);
  }
});

// Add Item
app.post('/api/:table', async (req, res) => {
  try {
    const { table } = req.params;
    const item = req.body;

    const pkName = PK_MAP[table] || 'id';
    
    // Check if item has ID, if not assign one
    if (!item[pkName]) {
      const prefix = table.substring(0, 3);
      item[pkName] = prefix + '-' + Math.floor(100000 + Math.random() * 900000);
    }

    const inserted = await insertItem(table, item);
    
    // Trigger email notification if a new bill is generated
    if (table === 'bills') {
      notifyNewBill(inserted).catch(err => console.error('Error sending bill email:', err.message));
    }

    res.status(201).json(inserted);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Update Item
app.put('/api/:table/:id', async (req, res) => {
  try {
    const { table, id } = req.params;
    const updatedFields = req.body;

    const updated = await updateItem(table, id, updatedFields);
    if (updated) {
      res.json(updated);
    } else {
      res.status(404).json({ error: `Item with id ${id} not found in ${table}` });
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Delete Item
app.delete('/api/:table/:id', async (req, res) => {
  try {
    const { table, id } = req.params;
    const deleted = await deleteItem(table, id);
    if (deleted) {
      res.json({ success: true });
    } else {
      res.status(404).json({ error: `Item with id ${id} not found in ${table}` });
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});



// Initialize database schema and then start the server
initDB().then(() => {
  const { getPool } = require('./db');
  const pool = getPool();
  if (pool) {
    setPool(pool);
    // Run upcoming bill due reminder checks on startup
    checkAndNotifyUpcomingBills().catch(e => console.error('Upcoming bills check error:', e.message));
    // Set a recurring check every 12 hours
    setInterval(() => {
      checkAndNotifyUpcomingBills().catch(e => console.error('Upcoming bills check error:', e.message));
    }, 12 * 60 * 60 * 1000);
  }

  app.listen(PORT, () => {
    console.log(`Backend server running at http://localhost:${PORT}`);
  });
});
