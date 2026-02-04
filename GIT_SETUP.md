# Git Setup Instructions

Quick guide to push your code to GitHub.

## Step-by-Step Instructions

### 1. Check if Git is Installed

Open PowerShell or Command Prompt and run:
```bash
git --version
```

If not installed, download from: https://git-scm.com/download/win

### 2. Navigate to Project Directory

```bash
cd "C:\Users\Madhu Goud\Desktop\Gatepass nov2"
```

### 3. Initialize Git (if not already done)

```bash
git init
```

### 4. Configure Git (if first time)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 5. Check Status

```bash
git status
```

You should see your files listed. Make sure `db.sqlite3`, `venv/`, and other excluded files are not listed.

### 6. Add All Files

```bash
git add .
```

### 7. Create First Commit

```bash
git commit -m "Initial commit: Hostel Gatepass Management System"
```

### 8. Create GitHub Repository

1. Go to https://github.com
2. Click **"+"** → **"New repository"**
3. Name: `hostel-gatepass-system`
4. Description: "Django hostel gatepass management system"
5. Choose **Public** or **Private**
6. **DO NOT** check "Initialize with README"
7. Click **"Create repository"**

### 9. Add Remote and Push

Replace `YOUR_USERNAME` with your GitHub username:

```bash
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/hostel-gatepass-system.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

### 10. Authentication

If prompted for credentials:
- **Username**: Your GitHub username
- **Password**: Use a **Personal Access Token** (not your GitHub password)

#### How to Create Personal Access Token:

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click **"Generate new token (classic)"**
3. Name: `Git Push Token`
4. Select scope: `repo` (check the box)
5. Click **"Generate token"**
6. **Copy the token immediately** (you won't see it again)
7. Use this token as your password when pushing

### 11. Verify Push

Go to your GitHub repository and verify all files are uploaded.

---

## Common Commands

```bash
# Check status
git status

# Add files
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push

# Pull latest changes
git pull

# View commit history
git log
```

---

## Troubleshooting

### Error: "fatal: remote origin already exists"

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/hostel-gatepass-system.git
```

### Error: "Authentication failed"

- Use Personal Access Token instead of password
- Or set up SSH keys for authentication

### Error: "Permission denied"

- Check repository URL is correct
- Verify you have push access to the repository
- Check your GitHub credentials

---

## Next Steps

After pushing to GitHub:
1. Follow [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) to deploy on Render.com
2. Set up continuous deployment
3. Configure environment variables

---

**Need Help?** Check GitHub documentation: https://docs.github.com

