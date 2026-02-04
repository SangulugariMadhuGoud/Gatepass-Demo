# Email Configuration Fix

## Problem
Registration emails were not being sent to students, wardens, or security staff when they registered. The emails were only being printed to console logs instead of actually being sent.

## Root Cause
The Django email backend was configured to use `console.EmailBackend` by default, which only prints emails to the console/logs instead of sending them via SMTP.

## Solution Applied

### 1. Updated `settings.py`
- Added comprehensive SMTP email configuration
- Email backend automatically switches to SMTP if email credentials are provided
- Falls back to console backend if no SMTP credentials are configured

### 2. Updated `render.yaml`
- Added email environment variables to the deployment configuration
- Set up for Gmail SMTP by default (can be changed to other providers)

### 3. Documentation Updated
- Added email setup instructions to `RENDER_DEPLOYMENT_CONFIG.md`
- Included step-by-step guides for Gmail and other email providers

## How to Enable Email Sending

### For Local Development
Add these to your `.env` file or environment:
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### For Render Deployment
Add these environment variables in Render Dashboard:

**Gmail Setup (Recommended for Testing):**
1. Enable 2-Factor Authentication on your Gmail account
2. Create an App Password: https://myaccount.google.com/apppasswords
3. Add these environment variables in Render:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Important:** Use App Password, not your regular Gmail password!

### Alternative Email Providers

**SendGrid (Free tier available):**
```
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

**Outlook/Hotmail:**
```
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

## What Happens Now

When a user registers (student, warden, or security):
1. The `_send_registration_email()` function is called automatically
2. If SMTP is configured, an email is sent with:
   - Username
   - Password
   - Account details
3. If SMTP is not configured, email details are logged to console (for debugging)

## Testing

After setting up email configuration:
1. Register a test user (student/warden/security)
2. Check the email inbox for the registration email
3. Check Render logs if email doesn't arrive (for error messages)

## Files Modified
- `Gatepass/hostel_gatepass/settings.py` - Added SMTP configuration
- `render.yaml` - Added email environment variables
- `RENDER_DEPLOYMENT_CONFIG.md` - Added email setup documentation

## Next Steps
1. Set up email credentials in Render Dashboard
2. Deploy the updated configuration
3. Test registration to verify emails are being sent
4. Monitor logs for any email-related errors

