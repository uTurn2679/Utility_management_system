-- Create Database if not exists
CREATE DATABASE IF NOT EXISTS utilis_db;
USE utilis_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL,
  status VARCHAR(50) DEFAULT 'active'
) ENGINE=InnoDB;

-- 2. Customers Table
CREATE TABLE IF NOT EXISTS customers (
  customer_id VARCHAR(50) PRIMARY KEY,
  user_id VARCHAR(50) NOT NULL,
  phone VARCHAR(50) NOT NULL,
  address TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. Meters Table
CREATE TABLE IF NOT EXISTS meters (
  meter_id VARCHAR(50) PRIMARY KEY,
  customer_id VARCHAR(50) NULL,
  meter_number VARCHAR(100) UNIQUE NOT NULL,
  utilityType VARCHAR(50) NOT NULL,
  status VARCHAR(50) DEFAULT 'active',
  installDate VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- 4. Meter Readings Table
CREATE TABLE IF NOT EXISTS meter_readings (
  reading_id VARCHAR(50) PRIMARY KEY,
  meter_id VARCHAR(50) NOT NULL,
  month VARCHAR(50) NOT NULL,
  unit_consumed INT NOT NULL,
  FOREIGN KEY (meter_id) REFERENCES meters(meter_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. Bills Table
CREATE TABLE IF NOT EXISTS bills (
  bill_id VARCHAR(50) PRIMARY KEY,
  customer_id VARCHAR(50) NOT NULL,
  amount DOUBLE NOT NULL,
  due_date VARCHAR(50) NOT NULL,
  status VARCHAR(50) NOT NULL,
  billingMonth VARCHAR(50) NOT NULL,
  billingYear VARCHAR(50) NOT NULL,
  meterId VARCHAR(50) NOT NULL,
  prevReading INT NOT NULL,
  currReading INT NOT NULL,
  consumption INT NOT NULL,
  tariffRate DOUBLE NOT NULL,
  createdAt VARCHAR(50) NOT NULL,
  paymentDate VARCHAR(50) NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
  FOREIGN KEY (meterId) REFERENCES meters(meter_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 6. Payments Table
CREATE TABLE IF NOT EXISTS payments (
  payment_id VARCHAR(50) PRIMARY KEY,
  bill_id VARCHAR(50) NOT NULL,
  amount DOUBLE NOT NULL,
  payment_date VARCHAR(50) NOT NULL,
  method VARCHAR(50) NOT NULL,
  transactionId VARCHAR(255) NOT NULL,
  status VARCHAR(50) NOT NULL,
  FOREIGN KEY (bill_id) REFERENCES bills(bill_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. Complaints Table
CREATE TABLE IF NOT EXISTS complaints (
  complaint_id VARCHAR(50) PRIMARY KEY,
  customer_id VARCHAR(50) NOT NULL,
  subject VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  status VARCHAR(50) NOT NULL,
  assignedTo VARCHAR(50) NULL,
  createdAt VARCHAR(50) NOT NULL,
  comments JSON NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 8. Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
  id VARCHAR(50) PRIMARY KEY,
  userId VARCHAR(50) NOT NULL,
  message TEXT NOT NULL,
  type VARCHAR(50) NOT NULL,
  date VARCHAR(50) NOT NULL,
  isRead TINYINT(1) DEFAULT 0,
  FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 9. Maintenance Table
CREATE TABLE IF NOT EXISTS maintenance (
  maintenance_id VARCHAR(50) PRIMARY KEY,
  customer_id VARCHAR(50) NOT NULL,
  request_type VARCHAR(100) NOT NULL,
  description TEXT NOT NULL,
  status VARCHAR(50) NOT NULL,
  assigned_to VARCHAR(50) NULL,
  createdAt VARCHAR(50) NOT NULL,
  comments JSON NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
) ENGINE=InnoDB;
