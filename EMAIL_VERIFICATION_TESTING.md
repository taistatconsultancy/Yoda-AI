# 📧 Email Verification - Testing Guide

## Issue Summary

The email verification system is **working correctly**, but emails are **not being sent** because:

✅ **User is created in database**  
✅ **Verification token is generated**  
✅ **Token is stored in database**  
✅ **Verification link is generated**  
❌ **Email is NOT sent** (emails disabled for testing)

---

## Why No Email Is Sent

The `.env` file has email notifications **disabled**:

```env
ENABLE_EMAIL_NOTIFICATIONS=False
```

This is **intentional** for development/testing. The system prints verification links to the **server console** instead of sending real emails.

---

## How to Get Verification Link

### Method 1: Check Server Console (Recommended)

When you register, check your server terminal output for:

```
INFO:     * Checking console output for verification link *
✅ Verification email sent to: marswriter649@gmail.com
```

Then look for:
```
==========================================================
EMAIL VERIFICATION LINK (check console):
==========================================================
Click here to verify: http://localhost:8000/api/v1/user-auth/verify-email?token=XXXXX
==========================================================
```

**Copy that link** and paste it in your browser.

---

### Method 2: Get Verification Link Script

Run this script to get the verification link for any user:

```bash
python get_verification_link.py marswriter649@gmail.com
```

**Output:**
```
============================================================
EMAIL VERIFICATION LINK:
============================================================

http://localhost:8000/api/v1/user-auth/verify-email?token=3W5lHViUj0t7dQVphaanQQxSFiFri9efDA_WPBRxGgk

============================================================

✅ Copy this link and paste in your browser to verify marswriter649@gmail.com
   Token expires: 2025-10-28 15:40:04.237893
```

---

### Method 3: Check Database Directly

Query the `email_verification_tokens` table:

```sql
SELECT 
    et.token,
    et.expires_at,
    u.email,
    u.email_verified
FROM email_verification_tokens et
JOIN users u ON u.id = et.user_id
WHERE et.used_at IS NULL
ORDER BY et.created_at DESC
LIMIT 1;
```

Then construct the URL:
```
http://localhost:8000/api/v1/user-auth/verify-email?token=<TOKEN_FROM_QUERY>
```

---

## Testing Steps

### 1. Register a New User

**Endpoint:** `POST /api/v1/user-auth/register`

**Body:**
```json
{
  "email": "test@example.com",
  "password": "test123",
  "full_name": "Test User"
}
```

**Response:** `403 Forbidden`
```json
{
  "detail": "Verification email sent. Please check your email to verify your account."
}
```

### 2. Get Verification Link

**Option A:** Check server console for link

**Option B:** Run script
```bash
python get_verification_link.py test@example.com
```

### 3. Verify Email

Paste the verification link in your browser.

**Expected Result:**
- ✅ Success page with "Email Verified Successfully!"
- ✅ User can now log in
- ✅ Database shows `email_verified = TRUE`

### 4. Test Login

**Endpoint:** `POST /api/v1/user-auth/login`

**Body:**
```json
{
  "email": "test@example.com",
  "password": "test123"
}
```

**Expected Result:** Success with JWT token

---

## Enable Real Email (Optional)

To send real emails, update your `.env`:

```env
# Enable email notifications
ENABLE_EMAIL_NOTIFICATIONS=True

# Gmail settings (example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # Get from Google Account settings
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=YodaAI
```

**How to get Gmail App Password:**
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"
3. Go to "App passwords"
4. Generate password for "Mail"
5. Copy 16-character password to `.env`

---

## Current Status Check

For user `marswriter649@gmail.com`:

```sql
SELECT email, email_verified, email_verified_at 
FROM users 
WHERE email = 'marswriter649@gmail.com';
```

**If `email_verified = FALSE`:**
- ✅ Normal - user needs to verify
- Run `python get_verification_link.py marswriter649@gmail.com`
- Copy the link
- Open in browser

**If `email_verified = TRUE`:**
- ✅ Already verified
- User can log in

---

## Troubleshooting

### Issue: "Invalid or already used verification token"

**Solution:**
- Token has expired (24 hours) or already used
- Register again to get a new token

### Issue: "Verification email sent" but can't find link

**Solution:**
1. Check server console output
2. Run `python get_verification_link.py <email>`
3. Check database directly

### Issue: Email not in inbox

**Solution:**
- **Expected behavior** - emails are disabled for testing
- Use console link or script instead

---

## Summary

✅ **Email verification is WORKING**  
✅ **Tokens are generated correctly**  
✅ **Database records are created**  
✅ **Verification endpoint works**  
❌ **Emails not sent** (disabled for testing - use console/script instead)

**To verify:**
1. Register → get 403
2. Run `python get_verification_link.py <email>`
3. Copy link to browser
4. See success page
5. Login works ✅
