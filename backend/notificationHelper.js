const { sendMail } = require('./emailService');
const mysql = require('mysql2/promise');
const fs = require('fs');
const path = require('path');

// Helper to get MySQL pool (uses existing pool if available, otherwise creates one)
let poolReference = null;
function setPool(pool) {
  poolReference = pool;
}

async function getCustomerEmailAndName(customerId) {
  if (!poolReference) return null;
  try {
    const [custRows] = await poolReference.query('SELECT * FROM customers WHERE customer_id = ?', [customerId]);
    if (custRows.length === 0) return null;
    
    const [userRows] = await poolReference.query('SELECT * FROM users WHERE id = ?', [custRows[0].user_id]);
    if (userRows.length === 0) return null;

    return {
      email: userRows[0].email,
      name: userRows[0].name
    };
  } catch (err) {
    console.error('Error fetching customer details for email:', err.message);
    return null;
  }
}

async function getMeterType(meterId) {
  if (!poolReference) return 'Utility';
  try {
    const [rows] = await poolReference.query('SELECT utilityType FROM meters WHERE meter_id = ?', [meterId]);
    return rows.length > 0 ? rows[0].utilityType : 'Utility';
  } catch (err) {
    return 'Utility';
  }
}

async function notifyNewBill(bill) {
  const details = await getCustomerEmailAndName(bill.customer_id);
  if (!details) return;

  const utilityType = await getMeterType(bill.meterId);
  const subject = `New Utility Bill Generated: ${utilityType.toUpperCase()} - ${bill.billingMonth} ${bill.billingYear}`;
  
  const html = `
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
      <h2 style="color: #00f2fe; text-align: center;">Utility Management System Invoice Notification</h2>
      <p>Dear <strong>${details.name}</strong>,</p>
      <p>A new utility bill has been generated for your account. Please find the summary below:</p>
      
      <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <tr style="background-color: #f8f9fa;">
          <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Invoice ID</th>
          <td style="padding: 10px; border: 1px solid #e0e0e0;">${bill.bill_id}</td>
        </tr>
        <tr>
          <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Utility Type</th>
          <td style="padding: 10px; border: 1px solid #e0e0e0;">${utilityType.toUpperCase()}</td>
        </tr>
        <tr style="background-color: #f8f9fa;">
          <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Billing Cycle</th>
          <td style="padding: 10px; border: 1px solid #e0e0e0;">${bill.billingMonth} ${bill.billingYear}</td>
        </tr>
        <tr>
          <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Consumption</th>
          <td style="padding: 10px; border: 1px solid #e0e0e0;">${bill.consumption} units</td>
        </tr>
        <tr style="background-color: #f8f9fa; font-weight: bold;">
          <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Total Payable</th>
          <td style="padding: 10px; border: 1px solid #e0e0e0; color: #ff5e62;">৳${bill.amount}</td>
        </tr>
        <tr>
          <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Due Date</th>
          <td style="padding: 10px; border: 1px solid #e0e0e0; font-weight: bold; color: #f5af19;">${bill.due_date}</td>
        </tr>
      </table>
      
      <p style="text-align: center; margin-top: 30px;">
        <a href="http://localhost:8080/#/public-bill-view?id=${bill.bill_id}" style="background-color: #00f2fe; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Details & Pay</a>
      </p>
      
      <hr style="border: 0; border-top: 1px solid #e0e0e0; margin-top: 30px;">
      <p style="font-size: 0.8rem; color: #888; text-align: center;">This is an automated notification. Please do not reply directly to this email.</p>
    </div>
  `;

  await sendMail(details.email, subject, html);
}

async function checkAndNotifyUpcomingBills() {
  if (!poolReference) return 0;
  let sentCount = 0;
  try {
    // Fetch all unpaid bills
    const [bills] = await poolReference.query("SELECT * FROM bills WHERE status = 'unpaid'");
    const today = new Date();
    
    for (const bill of bills) {
      const due = new Date(bill.due_date);
      const dueClean = new Date(due.getFullYear(), due.getMonth(), due.getDate());
      const todayClean = new Date(today.getFullYear(), today.getMonth(), today.getDate());
      
      const timeDiff = dueClean.getTime() - todayClean.getTime();
      const daysDiff = Math.round(timeDiff / (1000 * 3600 * 24));
      
      // Notify if bill is due in exactly 2 days or 1 day
      if (daysDiff === 1 || daysDiff === 2) {
        const details = await getCustomerEmailAndName(bill.customer_id);
        if (!details) continue;

        const utilityType = await getMeterType(bill.meterId);
        const subject = `URGENT Reminder: Utility Bill Due in ${daysDiff} Day(s) - ${bill.bill_id}`;
        
        const html = `
          <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ff5e62; border-radius: 8px;">
            <h2 style="color: #ff5e62; text-align: center;">Upcoming Bill Due Date Warning</h2>
            <p>Dear <strong>${details.name}</strong>,</p>
            <p style="color: #d9534f; font-weight: bold;">This is an urgent reminder that your utility bill is due in ${daysDiff} day(s) on ${bill.due_date}.</p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
              <tr style="background-color: #f8f9fa;">
                <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Invoice ID</th>
                <td style="padding: 10px; border: 1px solid #e0e0e0;">${bill.bill_id}</td>
              </tr>
              <tr>
                <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Utility Type</th>
                <td style="padding: 10px; border: 1px solid #e0e0e0;">${utilityType.toUpperCase()}</td>
              </tr>
              <tr style="background-color: #f8f9fa;">
                <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Billing Cycle</th>
                <td style="padding: 10px; border: 1px solid #e0e0e0;">${bill.billingMonth} ${bill.billingYear}</td>
              </tr>
              <tr style="background-color: #f8f9fa; font-weight: bold;">
                <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Total Payable</th>
                <td style="padding: 10px; border: 1px solid #e0e0e0; color: #ff5e62;">৳${bill.amount}</td>
              </tr>
              <tr>
                <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Due Date</th>
                <td style="padding: 10px; border: 1px solid #e0e0e0; font-weight: bold; color: #ff5e62;">${bill.due_date}</td>
              </tr>
            </table>
            
            <p style="text-align: center; margin-top: 30px;">
              <a href="http://localhost:8080/#/public-bill-view?id=${bill.bill_id}" style="background-color: #ff5e62; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Pay Invoice Now</a>
            </p>
            
            <hr style="border: 0; border-top: 1px solid #e0e0e0; margin-top: 30px;">
            <p style="font-size: 0.8rem; color: #888; text-align: center;">Please ignore this email if you have already completed the payment.</p>
          </div>
        `;

        await sendMail(details.email, subject, html);
        sentCount++;
      }
    }
  } catch (err) {
    console.error('Error running upcoming bills notification check:', err.message);
  }
  return sentCount;
}

module.exports = {
  setPool,
  notifyNewBill,
  checkAndNotifyUpcomingBills
};
