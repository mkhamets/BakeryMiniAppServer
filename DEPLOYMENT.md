# 🚀 Deployment Guide - Bakery Mini App Server

## 🎯 Deployment Methods

### Heroku Deployment (Recommended)

#### 1. Creating Heroku App
```bash
heroku create your-app-name
```

#### 2. Environment Variables Setup
```bash
heroku config:set BOT_TOKEN="your_token"
heroku config:set ADMIN_CHAT_ID="your_id"
heroku config:set ADMIN_EMAIL="your_email"
heroku config:set BASE_WEBAPP_URL="https://your-app.herokuapp.com/bot-app/"
heroku config:set HMAC_SECRET="your_hmac_secret"
```

#### 3. Authentication Setup

**Option 1: Login through browser (recommended)**
```bash
heroku login
# Press any key to open browser and login
```

**Option 2: Use API key**
1. Get API key from [dashboard.heroku.com/account](https://dashboard.heroku.com/account)
2. Scroll down to "API Key" section
3. Copy your API key
4. Set environment variable:
```bash
export HEROKU_API_KEY="your_api_key_here"
```

**Option 3: Add to shell profile (permanent)**
```bash
# Add to ~/.zshrc or ~/.bashrc
echo 'export HEROKU_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

#### 4. Deployment
```bash
git push heroku main
```

### Alternative Deployment Methods

#### GitHub Actions

**1. Create workflow file** (`.github/workflows/deploy.yml`):
```yaml
name: Deploy to Heroku
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.14
      with:
        heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
        heroku_app_name: ${{ secrets.HEROKU_APP_NAME }}
        heroku_email: ${{ secrets.HEROKU_EMAIL }}
```

**2. Configure GitHub Secrets:**
1. Go to repository settings → Secrets and variables → Actions
2. Add the following secrets:
   - `HEROKU_API_KEY` - your Heroku API key
   - `HEROKU_APP_NAME` - your app name (e.g., `bakery-mini-app-server`)
   - `HEROKU_EMAIL` - your Heroku email

**3. Get Heroku API Key:**
1. Visit [dashboard.heroku.com/account](https://dashboard.heroku.com/account)
2. Scroll down to "API Key" section
3. Click "Reveal" and copy the key

#### Web Interface
1. Connect GitHub repository to Heroku
2. Enable automatic deployments
3. Configure environment variables in dashboard

## 🔧 Configuration Files

### app.json
```json
{
  "name": "bakery-mini-app-server",
  "description": "Telegram WebApp for Bakery",
  "repository": "https://github.com/your-username/BakeryMiniAppServer",
  "logo": "https://your-app.herokuapp.com/logo.png",
  "keywords": ["telegram", "bot", "webapp", "bakery"],
  "env": {
    "BOT_TOKEN": {
      "description": "Telegram Bot Token",
      "required": true
    },
    "ADMIN_CHAT_ID": {
      "description": "Admin Telegram Chat ID",
      "required": true
    },
    "ADMIN_EMAIL": {
      "description": "Admin Email Address",
      "required": true
    }
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "basic"
    }
  },
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}
```

### Procfile
```
web: python bot/main.py
worker: python scheduler.py
```

### requirements.txt
```
aiogram==3.4.1
aiosqlite==0.19.0
aiohttp==3.9.1
aiohttp-cors==0.7.0
beautifulsoup4==4.12.2
lxml==4.9.3
```

## 📋 Environment Variables

### Required Variables
```bash
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_CHAT_ID=123456789
ADMIN_EMAIL=admin@example.com
BASE_WEBAPP_URL=https://your-app.herokuapp.com/bot-app/
```

### Additional Variables
```bash
ADMIN_EMAIL_PASSWORD=your_smtp_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
HMAC_SECRET=your_hmac_secret_key
ENABLE_RATE_LIMITING=true
RATE_LIMIT_MAX_REQUESTS=100
LOG_LEVEL=INFO
```

## 🔄 Deployment Process

### 1. Preparation
```bash
# Clone repository
git clone https://github.com/your-username/BakeryMiniAppServer.git
cd BakeryMiniAppServer

# Install dependencies
pip install -r requirements.txt
```

### 2. Local Testing
```bash
# Setup environment variables
cp env.example .env
# Edit .env file

# Run locally
python bot/main.py
```

### 3. Heroku Deployment
```bash
# Create app
heroku create your-app-name

# Configure variables
heroku config:set BOT_TOKEN="your_token"
heroku config:set ADMIN_CHAT_ID="your_id"
heroku config:set ADMIN_EMAIL="your_email"

# Deploy
git push heroku main
```

### 4. Deployment Verification
```bash
# Check status
heroku ps

# View logs
heroku logs --tail

# Check configuration
heroku config
```

## 🛠️ Deployment Scripts

### build.sh
```bash
#!/bin/bash
# Build and cache update script

echo "Building application..."
python -c "
import time
timestamp = int(time.time())
print(f'Cache busting timestamp: {timestamp}')
"

echo "Build completed successfully!"
```

### deploy.sh
```bash
#!/bin/bash
# Deployment automation script

echo "Starting deployment..."

# Check git status
if [ -n "$(git status --porcelain)" ]; then
    echo "Error: Working directory not clean"
    exit 1
fi

# Deploy to Heroku
git push heroku main

echo "Deployment completed!"
```

## 📊 Deployment Monitoring

### Health Check
```bash
# Check status
curl https://your-app.herokuapp.com/health

# Check API
curl https://your-app.herokuapp.com/bot-app/api/categories
```

### Logs and Monitoring
```bash
# View real-time logs
heroku logs --tail

# View logs from last hour
heroku logs --since=1h

# Monitor metrics
heroku ps:scale web=1
```

## 🚨 Deployment Troubleshooting

### Common Issues

#### 1. Build Errors
```bash
# Check build logs
heroku logs --tail

# Check dependencies
pip check
```

#### 2. Configuration Errors
```bash
# Check environment variables
heroku config

# Check bot token
curl "https://api.telegram.org/bot<TOKEN>/getMe"
```

#### 3. Performance Issues
```bash
# Scale up
heroku ps:scale web=2

# Check resource usage
heroku ps
```

### Debug Commands
```bash
# Connect to app
heroku run bash

# Check file system
heroku run ls -la

# Test database connection
heroku run python -c "import sqlite3; print('DB OK')"
```

## 🔄 Updates and Rollbacks

### Application Updates
```bash
# Deploy new version
git push heroku main

# Check status
heroku ps
```

### Rollback to Previous Version
```bash
# View releases
heroku releases

# Rollback to previous release
heroku rollback

# Rollback to specific release
heroku rollback v123
```

---

**Last Updated:** 2025-09-07  
**Maintained by:** Development Team