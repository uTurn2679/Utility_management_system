const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');

const LOG_FILE = path.join(__dirname, 'data', 'sent_emails.log');

// Setup logging directory
if (!fs.existsSync(path.dirname(LOG_FILE))) {
  fs.mkdirSync(path.dirname(LOG_FILE), { recursive: true });
}

function logEmail(to, subject, html, etherealUrl = null) {
  const logMessage = `\n==================================================\n` +
                     `[SENT AT]       : ${new Date().toISOString()}\n` +
                     `[TO]            : ${to}\n` +
                     `[SUBJECT]       : ${subject}\n` +
                     (etherealUrl ? `[VIEW ONLINE IN BOX] : ${etherealUrl}\n` : '') +
                     `[CONTENT]       :\n${html}\n` +
                     `==================================================\n`;
  fs.appendFileSync(LOG_FILE, logMessage, 'utf8');
  console.log(`[Email Logged] Subject: "${subject}" to ${to}`);
  if (etherealUrl) {
    console.log(`👉 View sent email online at: ${etherealUrl}`);
  }

  // Also log to a JSON file for easy UI listing
  const JSON_LOG = path.join(__dirname, 'data', 'sent_emails.json');
  try {
    let emails = [];
    if (fs.existsSync(JSON_LOG)) {
      emails = JSON.parse(fs.readFileSync(JSON_LOG, 'utf8'));
    }
    emails.push({
      id: 'eml-' + Math.floor(100000 + Math.random() * 900000),
      sentAt: new Date().toISOString(),
      to: to,
      subject: subject,
      etherealUrl: etherealUrl,
      html: html
    });
    // Keep only the last 100 emails to prevent bloat
    if (emails.length > 100) {
      emails.shift();
    }
    fs.writeFileSync(JSON_LOG, JSON.stringify(emails, null, 2), 'utf8');
  } catch (err) {
    console.error('Error logging email to JSON:', err.message);
  }
}

async function sendMail(to, subject, html) {
  const host = process.env.SMTP_HOST;
  const user = process.env.SMTP_USER;
  const pass = process.env.SMTP_PASS;

  // If no SMTP configured, automatically create a free test mail box dynamically
  if (!host || !user || !pass || user.includes('your-email')) {
    try {
      console.log('🔄 Creating a free Ethereal test SMTP account...');
      const testAccount = await nodemailer.createTestAccount();
      
      const transporter = nodemailer.createTransport({
        host: 'smtp.ethereal.email',
        port: 587,
        secure: false,
        auth: {
          user: testAccount.user,
          pass: testAccount.pass
        }
      });

      const info = await transporter.sendMail({
        from: '"Utility Management System Support" <support@utilis.com>',
        to: to,
        subject: subject,
        html: html
      });

      const etherealUrl = nodemailer.getTestMessageUrl(info);
      logEmail(to, subject, html, etherealUrl);
      return { success: true, etherealUrl };
    } catch (err) {
      console.error('Error generating Ethereal test mail:', err.message);
      // Fallback to offline file log
      logEmail(to, subject, html);
      return { success: true, loggedOffline: true };
    }
  }

  // If custom SMTP is configured, send real email
  try {
    const transporter = nodemailer.createTransport({
      host: host,
      port: parseInt(process.env.SMTP_PORT) || 587,
      secure: false,
      auth: {
        user: user,
        pass: pass
      }
    });

    const info = await transporter.sendMail({
      from: `"Utility Management System Support" <${user}>`,
      to: to,
      subject: subject,
      html: html
    });

    console.log(`[Email Sent] MessageId: ${info.messageId} to ${to}`);
    logEmail(to, subject, html);
    return { success: true, messageId: info.messageId };
  } catch (error) {
    console.error('Error sending email via SMTP:', error.message);
    logEmail(to, subject, html);
    return { success: false, error: error.message };
  }
}

module.exports = { sendMail };
