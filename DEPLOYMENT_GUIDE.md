# Deployment Guide - Hostel Gatepass Management System

This guide will help you push your code to GitHub and deploy it on Render.com (free tier) with PostgreSQL database.

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Push to GitHub](#push-to-github)
3. [Deploy on Render.com](#deploy-on-rendercom)
4. [Alternative Free Hosting Options](#alternative-free-hosting-options)
5. [Post-Deployment Setup](#post-deployment-setup)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- GitHub account (free)
- Render.com account (free)
- Git installed on your computer
- Python 3.11+ installed (for local testing)

---

## Push to GitHub

### Step 1: Initialize Git Repository

1. Open terminal/command prompt in your project root directory:
   ```bash
   cd "C:\Users\Madhu Goud\Desktop\Gatepass nov2"
   ```

2. Initialize Git repository (if not already done):
   ```bash
   git init
   ```

3. Check current status:
   ```bash
   git status
   ```

### Step 2: Add Files to Git

```bash
git add .
```

### Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: Hostel Gatepass Management System"
```

### Step 4: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Repository name: `hostel-gatepass-system` (or any name you prefer)
5. Description: "Django-based hostel gatepass management system"
6. Choose **Public** or **Private**
7. **DO NOT** initialize with README, .gitignore, or license (we already have these)
8. Click **"Create repository"**

### Step 5: Push to GitHub

1. Copy the repository URL from GitHub (e.g., `https://github.com/yourusername/hostel-gatepass-system.git`)

2. Add remote origin:
   ```bash
   git remote add origin https://github.com/yourusername/hostel-gatepass-system.git
   ```

3. Rename branch to main (if needed):
   ```bash
   git branch -M main
   ```

4. Push to GitHub:
   ```bash
   git push -u origin main
   ```

5. Enter your GitHub username and password (or use Personal Access Token)

**Note:** If you get authentication errors, you may need to use a Personal Access Token instead of password:
- Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
- Generate new token with `repo` scope
- Use the token as your password when pushing

---

## Deploy on Render.com

### Step 1: Sign Up for Render.com

1. Go to [Render.com](https://render.com)
2. Click **"Get Started for Free"**
3. Sign up with GitHub (recommended) for easy integration

### Step 2: Create PostgreSQL Database

1. In Render dashboard, click **"New +"**
2. Select **"PostgreSQL"**
3. Configure:
   - **Name**: `gatepass-db`
   - **Database**: `gatepass`
   - **User**: `gatepass_user`
   - **Region**: Choose closest to you (e.g., Singapore, US East)
   - **PostgreSQL Version**: 15 (or latest)
   - **Plan**: **Free** (512 MB RAM, 1 GB storage)
4. Click **"Create Database"**
5. **Wait for database to be created** (takes 1-2 minutes)
6. Copy the **Internal Database URL** (we'll use this later)

### Step 3: Deploy Web Service

#### Option A: Using render.yaml (Recommended - Automatic Setup)

1. In Render dashboard, click **"New +"**
2. Select **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` file
5. Click **"Apply"** to deploy

Render will automatically:
- Create the web service
- Link the PostgreSQL database
- Set environment variables
- Deploy your application

#### Option B: Manual Setup

1. In Render dashboard, click **"New +"**
2. Select **"Web Service"**
3. Connect your GitHub repository
4. Select your repository: `hostel-gatepass-system`
5. Configure settings:
   - **Name**: `gatepass-django`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `Gatepass` (important!)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py create_superuser_if_not_exists --noinput
     ```
   - **Start Command**: 
     ```bash
     gunicorn hostel_gatepass.wsgi:application --bind 0.0.0.0:$PORT
     ```

6. **Environment Variables**:
   - `DEBUG`: `False`
   - `SECRET_KEY`: Generate a secure key (you can use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
   - `DATABASE_URL`: Use the Internal Database URL from Step 2
   - `ALLOWED_HOSTS`: `.onrender.com`
   - `PYTHON_VERSION`: `3.11.7`
   - `DJANGO_SUPERUSER_USERNAME`: `admin` (or your preferred username)
   - `DJANGO_SUPERUSER_EMAIL`: `admin@hostel.com` (or your email)
   - `DJANGO_SUPERUSER_PASSWORD`: `your-secure-password` (use a strong password!)

7. **Advanced Settings**:
   - **Auto-Deploy**: `Yes` (deploys on every push to main)
   - **Plan**: **Free** (512 MB RAM)

8. Click **"Create Web Service"**

### Step 4: Create Superuser

**✅ AUTOMATIC METHOD (Recommended) - No Shell Required!**

The superuser will be **automatically created** during deployment using environment variables!

If you're using `render.yaml` (Option A), the superuser is created automatically with these defaults:
- **Username**: `admin`
- **Email**: `admin@hostel.com`
- **Password**: Auto-generated (check Render dashboard → Environment → `DJANGO_SUPERUSER_PASSWORD`)

**To customize superuser credentials:**
1. Go to Render dashboard → Your service → Environment
2. Update these environment variables:
   - `DJANGO_SUPERUSER_USERNAME` - Change from `admin` to your preferred username
   - `DJANGO_SUPERUSER_EMAIL` - Change email if needed
   - `DJANGO_SUPERUSER_PASSWORD` - Set a custom password (or keep auto-generated)
3. Redeploy your service

**Manual Method (Alternative):**

If you prefer to create superuser manually or the automatic method didn't work:

1. **Option 1: Using Render Shell**
   - Go to your service dashboard
   - Click **"Shell"** tab
   - Run:
     ```bash
     cd Gatepass
     python manage.py createsuperuser
     ```
   - Follow prompts to create admin user

2. **Option 2: Using Management Command via Shell**
   - Go to Render Shell
   - Run:
     ```bash
     cd Gatepass
     python manage.py create_superuser_if_not_exists --username admin --email admin@hostel.com --password yourpassword
     ```

3. **Option 3: Using Environment Variables (Manual Setup)**
   - In Render dashboard → Environment variables, add:
     - `DJANGO_SUPERUSER_USERNAME`: `admin`
     - `DJANGO_SUPERUSER_EMAIL`: `admin@hostel.com`
     - `DJANGO_SUPERUSER_PASSWORD`: `your-secure-password`
   - Update build command to include:
     ```bash
     python manage.py create_superuser_if_not_exists --noinput
     ```
   - Redeploy service

### Step 5: Access Your Application

1. Your application will be available at: `https://gatepass-django.onrender.com`
2. Admin panel: `https://gatepass-django.onrender.com/admin/`
3. Login with superuser credentials

---

## Alternative Free Hosting Options

### 1. Railway.app (Recommended Alternative)
- **Free Tier**: $5 credit/month (enough for small apps)
- **PostgreSQL**: Included
- **Auto-deploy**: Yes
- **Website**: [railway.app](https://railway.app)

**Deployment Steps:**
1. Sign up with GitHub
2. Create new project
3. Add PostgreSQL service
4. Add web service from GitHub
5. Set environment variables
6. Deploy!

### 2. Fly.io
- **Free Tier**: 3 shared VMs, 3GB storage
- **PostgreSQL**: Available
- **Website**: [fly.io](https://fly.io)

### 3. PythonAnywhere
- **Free Tier**: Limited but good for testing
- **Database**: MySQL (free), PostgreSQL (paid)
- **Website**: [pythonanywhere.com](https://www.pythonanywhere.com)

### 4. Supabase + Vercel
- **Supabase**: Free PostgreSQL database
- **Vercel**: Free hosting (but needs adjustments for Django)
- **Website**: [supabase.com](https://supabase.com)

---

## Post-Deployment Setup

### 1. Create Initial Superuser

After deployment, create a superuser account:

```bash
# In Render Shell or via SSH
cd Gatepass
python manage.py createsuperuser
```

Default credentials (change these):
- Username: `admin`
- Email: `admin@hostel.com`
- Password: `admin123` (change immediately!)

### 2. Configure Email (Optional)

For parent verification SMS/Email:
- Add email backend in `settings.py`
- Configure SMTP settings
- Or use services like SendGrid (free tier available)

### 3. Set Up Domain (Optional)

1. Go to Render dashboard
2. Click on your service
3. Go to **Settings** → **Custom Domains**
4. Add your domain
5. Update DNS records as instructed

### 4. Monitor Your Application

- **Logs**: View in Render dashboard → Logs tab
- **Metrics**: Monitor CPU, Memory usage
- **Alerts**: Set up email alerts for downtime

---

## Troubleshooting

### Issue: Build Fails

**Solution:**
- Check build logs in Render dashboard
- Ensure `requirements.txt` is in `Gatepass/` directory
- Verify Python version in `runtime.txt`

### Issue: Database Connection Error

**Solution:**
- Verify `DATABASE_URL` environment variable is set
- Check database is created and running
- Ensure `psycopg2-binary` is in `requirements.txt`

### Issue: Static Files Not Loading

**Solution:**
- Ensure `whitenoise` is in `requirements.txt`
- Check `collectstatic` runs during build
- Verify `STATIC_ROOT` and `STATIC_URL` in settings.py

### Issue: Application Crashes on Startup

**Solution:**
- Check logs for error messages
- Verify all environment variables are set
- Ensure migrations are running
- Check `ALLOWED_HOSTS` includes your Render URL

### Issue: 500 Internal Server Error

**Solution:**
- Set `DEBUG=True` temporarily to see errors
- Check database migrations: `python manage.py migrate`
- Verify superuser exists
- Check logs in Render dashboard

### Issue: Free Tier Limitations

**Render.com Free Tier:**
- Spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- 750 hours/month (enough for always-on if single service)
- Database: 1 GB storage, 512 MB RAM

**Solutions:**
- Use services like [UptimeRobot](https://uptimerobot.com) (free) to ping your app every 5 minutes
- Upgrade to paid plan for always-on service
- Consider Railway.app for better free tier

---

## Environment Variables Reference

```bash
# Required
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/database
ALLOWED_HOSTS=.onrender.com

# Optional
PYTHON_VERSION=3.11.7
```

---

## Security Checklist

- [ ] Change default admin password
- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS (automatic on Render)
- [ ] Restrict `ALLOWED_HOSTS`
- [ ] Review CORS settings for production
- [ ] Set up regular database backups
- [ ] Monitor application logs

---

## Support & Resources

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Django Deployment**: [docs.djangoproject.com/en/stable/howto/deployment/](https://docs.djangoproject.com/en/stable/howto/deployment/)
- **PostgreSQL Docs**: [postgresql.org/docs](https://www.postgresql.org/docs/)

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Deploy on Render.com
3. ✅ Create superuser
4. ✅ Test all features
5. ✅ Set up monitoring
6. ✅ Configure backups
7. ✅ Add custom domain (optional)
8. ✅ Set up email notifications

---

**Happy Deploying! 🚀**

For questions or issues, check the troubleshooting section or refer to Render's documentation.

