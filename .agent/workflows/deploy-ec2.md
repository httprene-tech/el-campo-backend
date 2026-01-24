---
description: Deploy local changes to EC2 production server via Git
---
# EC2 Deployment Workflow

This workflow syncs your local development environment with the production EC2 server.

## Prerequisites
- SSH key file located at: `deploy/elcampo.pem`
- Git remote configured (origin → GitHub/GitLab)
- EC2 instance running with Gunicorn + Nginx

---

## Steps

### 1. Verify Local Changes
```powershell
# Check status
git status

# Review diff if needed
git diff
```

### 2. Commit Changes Locally
```powershell
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "feat(module): description of changes"
```

### 3. Push to Remote Repository
// turbo
```powershell
git push origin main
```

### 4. SSH into EC2
```powershell
# Connect to EC2 (from project root or deploy folder)
ssh -i deploy/elcampo.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### 5. Pull Changes on EC2
```bash
# Navigate to project directory
cd /home/ubuntu/el-campo-backend

# Activate virtual environment
source venv/bin/activate

# Pull latest changes
git pull origin main
```

### 6. Apply Database Migrations (if any)
```bash
python manage.py migrate
```

### 7. Collect Static Files (if changed)
```bash
python manage.py collectstatic --noinput
```

### 8. Restart Application Server
// turbo
```bash
sudo systemctl restart elcampo.service
```

### 9. Verify Deployment
```bash
# Check service status
sudo systemctl status elcampo.service

# Check Nginx
sudo systemctl status nginx

# Check logs for errors
sudo journalctl -u elcampo.service -n 50
```

---

## Cleanup EC2 (Recommended Periodically)

### Remove Python Cache
```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
```

### Remove Old Migrations (CAREFUL - only if not needed)
```bash
# List migration files
find . -path "*/migrations/*.py" -not -name "__init__.py"

# Only delete if you're sure they're applied
```

### Check Disk Usage
```bash
df -h
du -sh /home/ubuntu/el-campo-backend
```

---

## Troubleshooting

### If service fails to start:
```bash
# Check detailed logs
sudo journalctl -u elcampo.service -f

# Check Gunicorn directly
cd /home/ubuntu/el-campo-backend
source venv/bin/activate
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

### If Nginx returns 502:
```bash
# Check if Gunicorn socket exists
ls -la /run/gunicorn.sock

# Restart Nginx
sudo systemctl restart nginx
```
