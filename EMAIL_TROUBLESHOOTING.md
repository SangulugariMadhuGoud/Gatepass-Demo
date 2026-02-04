# Email Troubleshooting Guide

## Quick Diagnosis

If emails are not being sent, check the following in order:

### 1. Check Render Logs
Go to your Render dashboard → Service → Logs and search for:
- `"Registration email"` - to see if email sending is attempted
- `"SMTP credentials not configured"` - if credentials are missing
- `"console mode"` - if using console backend
- `"email sent successfully"` - if email was sent
- Any SMTP error messages

### 2. Verify Environment Variables in Render

Go to **Render Dashboard → Your Service → Environment** and verify these variables are set:

**Required for Email Sending:**
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Already Set (don't change these):**
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

### 3. Common Issues & Solutions

#### Issue 1: "SMTP credentials not configured"
**Symptoms:** Log shows "SMTP credentials not configured"
**Solution:** Add `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in Render Environment Variables

#### Issue 2: "console mode - not sent"
**Symptoms:** Log shows "console mode"
**Solution:** Check that `EMAIL_BACKEND` is set to `django.core.mail.backends.smtp.EmailBackend` in Render

#### Issue 3: Gmail Authentication Failed
**Symptoms:** SMTP authentication errors in logs
**Solutions:**
- Use **App Password**, not your regular Gmail password
- Ensure 2-Factor Authentication is enabled on Gmail
- Create new App Password: https://myaccount.google.com/apppasswords
- Make sure there are no spaces in the app password

#### Issue 4: Emails in Spam Folder
**Symptoms:** Emails sent but not received
**Solution:** 
- Check spam/junk folder
- Verify `DEFAULT_FROM_EMAIL` matches `EMAIL_HOST_USER`
- Add sender email to contacts

#### Issue 5: Connection Timeout
**Symptoms:** "Connection timeout" or "Connection refused" errors
**Solutions:**
- Verify `EMAIL_HOST` is correct for your provider
- Check firewall/network restrictions
- Try different SMTP port (465 for SSL instead of 587 for TLS)

## Step-by-Step Setup for Gmail

### Step 1: Enable 2FA on Gmail
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"

### Step 2: Create App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" as app
3. Select "Other" as device, enter "Gatepass System"
4. Click "Generate"
5. Copy the 16-character password (format: `abcd efgh ijkl mnop`)

### Step 3: Add to Render
1. Go to Render Dashboard → Your Service → Environment
2. Add/Edit these variables:
   ```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=abcdefghijklmnop  (no spaces!)
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```
3. Click "Save Changes"
4. Service will automatically redeploy

### Step 4: Test
1. Register a new user
2. Check Render logs for "Registration email sent successfully"
3. Check email inbox (and spam folder)

## Testing Email Configuration

### Method 1: Check Logs After Registration
After registering a user, check Render logs for:
- ✅ `"Registration email sent successfully"` - Email was sent
- ⚠️ `"SMTP credentials not configured"` - Need to add credentials
- ⚠️ `"console mode"` - Using console backend (emails not sent)

### Method 2: Test from Django Shell (if you have shell access)
```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test email.',
    settings.DEFAULT_FROM_EMAIL,
    ['your-test-email@gmail.com'],
    fail_silently=False,  # This will show errors
)
```

## Email Provider Settings

### Gmail
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Outlook/Hotmail
```
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-password
```

### SendGrid (Recommended for Production)
```
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Yahoo Mail
```
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@yahoo.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Still Not Working?

1. **Check Render Logs** - Most issues show up in logs
2. **Verify All Variables** - Double-check spelling and values
3. **Try Different Provider** - Test with SendGrid or Outlook
4. **Check Spam Folder** - Emails might be filtered
5. **Verify Email Address** - Make sure recipient email is correct
6. **Test with Simple Email Client** - Verify SMTP credentials work

## Debugging Tips

### Enable Verbose Logging
Add to Render Environment Variables:
```
DJANGO_LOG_LEVEL=DEBUG
```

### Check Current Configuration
Look in Render logs for these lines after deployment:
- Email backend being used
- SMTP server configuration
- Any authentication errors

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `SMTPAuthenticationError` | Wrong password/username | Use App Password, verify username |
| `SMTPConnectError` | Can't connect to server | Check EMAIL_HOST and EMAIL_PORT |
| `Timeout` | Connection timeout | Check network, increase EMAIL_TIMEOUT |
| `SSL/TLS Error` | Wrong encryption settings | Check EMAIL_USE_TLS vs EMAIL_USE_SSL |

