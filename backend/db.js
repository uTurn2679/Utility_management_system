const mysql = require('mysql2/promise');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });

let pool = null;
let useFallback = false;
const DB_FILE = path.join(__dirname, 'data', 'db.json');

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

async function query(sql, params = []) {
  if (useFallback) return null;
  const [results] = await pool.query(sql, params);
  return results;
}

// Local File Database Helper Methods (Fallback)
function readLocalDatabase() {
  if (!fs.existsSync(DB_FILE)) {
    return {};
  }
  try {
    return JSON.parse(fs.readFileSync(DB_FILE, 'utf8'));
  } catch (err) {
    return {};
  }
}

function writeLocalDatabase(data) {
  const dir = path.dirname(DB_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2), 'utf8');
}

// Database Connection Initialization
async function initDB() {
  try {
    // 1. Try connecting to MySQL without database first to ensure it exists
    const conn = await mysql.createConnection({
      host: process.env.DB_HOST || 'localhost',
      port: process.env.DB_PORT || 3306,
      user: process.env.DB_USER || 'root',
      password: process.env.DB_PASSWORD || ''
    });
    await conn.query(`CREATE DATABASE IF NOT EXISTS \`${process.env.DB_NAME || 'utilis_db'}\``);
    await conn.end();

    // 2. Setup connection pool
    pool = mysql.createPool({
      host: process.env.DB_HOST || 'localhost',
      port: process.env.DB_PORT || 3306,
      user: process.env.DB_USER || 'root',
      password: process.env.DB_PASSWORD || '',
      database: process.env.DB_NAME || 'utilis_db',
      waitForConnections: true,
      connectionLimit: 10,
      queueLimit: 0
    });

    // Test pool connection
    const testConn = await pool.getConnection();
    testConn.release();
    console.log('✅ MySQL connection established successfully.');

    // 3. Run schema migrations
    const schemaPath = path.join(__dirname, 'schema.sql');
    if (fs.existsSync(schemaPath)) {
      const schemaSql = fs.readFileSync(schemaPath, 'utf8');
      const statements = schemaSql
        .split(';')
        .map(s => s.trim())
        .filter(s => s.length > 0);

      for (const statement of statements) {
        if (statement.toLowerCase().startsWith('use ')) continue;
        await pool.query(statement);
      }
      console.log('✅ MySQL schema checked and initialized.');
    }
  } catch (error) {
    console.warn('⚠️ MySQL connection failed. Error details:', error.message);
    console.warn('🔄 Falling back to JSON File Database (db.json). Please check backend/.env credentials.');
    useFallback = true;
  }
}

// Relational CRUD Operations mapped to MySQL
async function getFullDB() {
  if (useFallback) {
    return readLocalDatabase();
  }

  try {
    const tables = Object.keys(PK_MAP);
    const db = {};
    for (const table of tables) {
      const [rows] = await pool.query(`SELECT * FROM \`${table}\``);
      // For complaints and maintenance, comments field is stored as JSON string. Parse it back.
      if (table === 'complaints' || table === 'maintenance') {
        db[table] = rows.map(r => {
          if (r.comments && typeof r.comments === 'string') {
            try { r.comments = JSON.parse(r.comments); } catch(e) {}
          }
          return r;
        });
      } else {
        db[table] = rows;
      }
    }
    return db;
  } catch (error) {
    console.error('Error fetching full MySQL DB, falling back:', error.message);
    return readLocalDatabase();
  }
}

async function saveTable(table, data) {
  if (useFallback) {
    const db = readLocalDatabase();
    db[table] = data;
    writeLocalDatabase(db);
    return;
  }

  try {
    const pk = PK_MAP[table];
    // Delete existing rows
    await pool.query(`DELETE FROM \`${table}\``);

    if (data.length === 0) return;

    // Bulk insert rows
    const keys = Object.keys(data[0]);
    const columns = keys.map(k => `\`${k}\``).join(', ');
    const placeholders = keys.map(() => '?').join(', ');
    const sql = `INSERT INTO \`${table}\` (${columns}) VALUES (${placeholders})`;

    for (const item of data) {
      const values = keys.map(k => {
        if (k === 'comments' || typeof item[k] === 'object') {
          return JSON.stringify(item[k]);
        }
        return item[k];
      });
      await pool.query(sql, values);
    }
  } catch (error) {
    console.error(`Error saving table ${table} to MySQL:`, error.message);
  }
}

async function insertItem(table, item) {
  if (useFallback) {
    const db = readLocalDatabase();
    if (!db[table]) db[table] = [];
    db[table].push(item);
    writeLocalDatabase(db);
    return item;
  }

  try {
    const keys = Object.keys(item);
    const columns = keys.map(k => `\`${k}\``).join(', ');
    const placeholders = keys.map(() => '?').join(', ');
    const sql = `INSERT INTO \`${table}\` (${columns}) VALUES (${placeholders})`;
    
    const values = keys.map(k => {
      if (k === 'comments' || typeof item[k] === 'object') {
        return JSON.stringify(item[k]);
      }
      return item[k];
    });

    await pool.query(sql, values);
    return item;
  } catch (error) {
    console.error(`Error inserting item to ${table} in MySQL:`, error.message);
    throw error;
  }
}

async function updateItem(table, id, updatedFields) {
  if (useFallback) {
    const db = readLocalDatabase();
    const pk = PK_MAP[table];
    const index = db[table].findIndex(item => item[pk] === id);
    if (index !== -1) {
      db[table][index] = { ...db[table][index], ...updatedFields };
      writeLocalDatabase(db);
      return db[table][index];
    }
    return null;
  }

  try {
    const pk = PK_MAP[table];
    const keys = Object.keys(updatedFields);
    if (keys.length === 0) return null;

    const setClause = keys.map(k => `\`${k}\` = ?`).join(', ');
    const sql = `UPDATE \`${table}\` SET ${setClause} WHERE \`${pk}\` = ?`;

    const values = keys.map(k => {
      if (k === 'comments' || typeof updatedFields[k] === 'object') {
        return JSON.stringify(updatedFields[k]);
      }
      return updatedFields[k];
    });
    values.push(id);

    await pool.query(sql, values);
    
    // Retrieve and return updated item
    const [rows] = await pool.query(`SELECT * FROM \`${table}\` WHERE \`${pk}\` = ?`, [id]);
    if (rows[0] && table === 'complaints' && typeof rows[0].comments === 'string') {
      try { rows[0].comments = JSON.parse(rows[0].comments); } catch(e) {}
    }
    return rows[0] || null;
  } catch (error) {
    console.error(`Error updating item ${id} in ${table} in MySQL:`, error.message);
    throw error;
  }
}

async function deleteItem(table, id) {
  if (useFallback) {
    const db = readLocalDatabase();
    const pk = PK_MAP[table];
    const index = db[table].findIndex(item => item[pk] === id);
    if (index !== -1) {
      db[table].splice(index, 1);
      writeLocalDatabase(db);
      return true;
    }
    return false;
  }

  try {
    const pk = PK_MAP[table];
    const sql = `DELETE FROM \`${table}\` WHERE \`${pk}\` = ?`;
    await pool.query(sql, [id]);
    return true;
  } catch (error) {
    console.error(`Error deleting item ${id} from ${table} in MySQL:`, error.message);
    throw error;
  }
}

module.exports = {
  initDB,
  query,
  getFullDB,
  saveTable,
  insertItem,
  updateItem,
  deleteItem,
  useFallback: () => useFallback,
  getPool: () => pool
};
