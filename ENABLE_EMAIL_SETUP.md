# 📧 Enable Email Notifications

## How to Make Emails Actually Send to Users

Currently, emails are **disabled for testing** and links are printed to the console. To send **real emails** to users, follow these steps:

---

## Step 1: Update Your `.env` File

Create or update your `.env` file in the project root with email settings:

```env
# Enable email notifications
ENABLE_EMAIL_NOTIFICATIONS=True

# Gmail SMTP Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=YodaAI
```

---

## Step 2: Get Gmail App Password

### Option A: Using Gmail App Password (Recommended)

1. **Go to Google Account Settings**
   - Visit: https://myaccount.google.com/security

2. **Enable 2-Step Verification**
   - Click "2-Step Verification"
   - Follow the setup process

3. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" as the app
   - Select "Other (Custom name)" as the device
   - Name it: "YodaAI Email Service"
   - Click "Generate"

4. **Copy the 16-Character Password**
   - It will look like: `abcd efgh ijkl mnop`
   - Remove spaces: `abcdefghijklmnop`

5. **Paste in `.env`**
   ```env
   SMTP_PASSWORD=abcdefghijklmnop
   ```

### Option B: Using Less Secure Apps (Not Recommended)

⚠️ **This method is deprecated by Google**

1. Go to: https://myaccount.google.com/lesssecureapps
2. Turn on "Allow less secure apps"
3. Use your regular Gmail password

---

## Step 3: Alternative Email Services

### Using SendGrid (Free)

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=YodaAI
```

**Sign up**: https://sendgrid.com

### Using Mailgun

```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=your_mailgun_username
SMTP_PASSWORD=your_mailgun_password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=YodaAI
```

**Sign up**: https://mailgun.com

### Using AWS SES

```env
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your_aws_access_key
SMTP_PASSWORD=your_aws_secret_key
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=YodaAI
```

---

## Step 4: Test Your Email Settings

### Option 1: Update `.env` File

1. Create `.env` file in project root (if it doesn't exist)
2. Copy from `env.example`
3. Update email settings:

```env
# Enable email notifications
ENABLE_EMAIL_NOTIFICATIONS=True

# Gmail settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop  # Your app password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=YodaAI
```

### Option 2: Restart Your Server

```bash
# Stop the current server (Ctrl+C)
# Start again
python start_server.py
```

### Option 3: Test Registration

1. Register a new user
2. Check the email inbox (including spam)
3. Click the verification link

---

## Troubleshooting

### Issue: "Authentication failed"

**Solution:**
- Make sure you're using an **App Password**, not your regular Gmail password
- Check that 2-Step Verification is enabled
- Verify the password has no spaces

### Issue: "Connection refused"

**Solution:**
- Check firewall settings
- Try SMTP_PORT=465 with SSL
- Try a different network

### Issue: "Email goes to spam"

**Solution:**
- Use a custom domain email
- Set up SPF/DKIM records
- Use a professional email service (SendGrid, Mailgun)

### Issue: Still seeing console output

**Solution:**
- Make sure `ENABLE_EMAIL_NOTIFICATIONS=True` in `.env`
- Restart the server after changing `.env`
- Check for typos in environment variable names

---

## Security Best Practices

### ✅ Do:
- Use environment variables (`.env`)
- Never commit `.env` to git
- Use App Passwords, not real passwords
- Rotate passwords regularly

### ❌ Don't:
- Hardcode credentials in code
- Share `.env` files
- Use your main email password
- Send emails from personal Gmail accounts in production

---

## Quick Reference

**Current Setup (Testing):**
```env
ENABLE_EMAIL_NOTIFICATIONS=False  # Emails printed to console
```

**Production Setup:**
```env
ENABLE_EMAIL_NOTIFICATIONS=True   # Real emails sent
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

---

## Summary

To send real emails:

1. ✅ Create `.env` file
2. ✅ Get Gmail App Password
3. ✅ Update `ENABLE_EMAIL_NOTIFICATIONS=True`
4. ✅ Add SMTP credentials
5. ✅ Restart server
6. ✅ Test registration

After this, users will receive **actual emails** instead of checking the console! 📧
