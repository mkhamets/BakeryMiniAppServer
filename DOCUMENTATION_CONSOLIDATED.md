# 📚 Bakery Mini App Server - Consolidated Documentation

## 🎯 Overview

This document consolidates all the scattered documentation files into a single, comprehensive guide for the Bakery Mini App Server project.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git
- Heroku CLI
- Telegram Bot Token

### Installation
```bash
git clone <repository-url>
cd BakeryMiniAppServer
pip install -r requirements.txt
```

### Environment Setup
Copy `env.example` to `.env` and configure:
```bash
cp env.example .env
# Edit .env with your values
```

## 🔧 Configuration

### Required Environment Variables
```bash
BOT_TOKEN=your_telegram_bot_token
ADMIN_CHAT_ID=your_telegram_user_id
ADMIN_EMAIL=your_email@example.com
BASE_WEBAPP_URL=https://your-app.herokuapp.com/bot-app/
```

### Optional Environment Variables
```bash
ADMIN_EMAIL_PASSWORD=your_smtp_password
SMTP_SERVER=smtp.gmail.com
HMAC_SECRET=your_hmac_secret_key
```

## 🚀 Deployment

### Heroku Deployment (Recommended)

1. **Create Heroku App:**
```bash
heroku create your-app-name
```

2. **Set Environment Variables:**
```bash
heroku config:set BOT_TOKEN="your_token"
heroku config:set ADMIN_CHAT_ID="your_id"
heroku config:set ADMIN_EMAIL="your_email"
heroku config:set BASE_WEBAPP_URL="https://your-app.herokuapp.com/bot-app/"
```

3. **Deploy:**
```bash
git push heroku main
```

### Alternative Deployment Methods

#### GitHub Actions
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
```

#### Web Interface
1. Connect GitHub repository to Heroku
2. Enable automatic deploys
3. Configure environment variables in dashboard

## 🔒 Security Features

### Implemented Security Measures

#### 1. HMAC Signature Authentication
- **Client-side:** Generates HMAC signatures using Telegram WebApp initData
- **Server-side:** Validates signatures to prevent proxy attacks
- **Protection:** Blocks Charles/Fiddler and other proxy tools

#### 2. Rate Limiting
- **IP-based:** 100 requests per hour per IP
- **Token-based:** Separate limits for authentication tokens
- **Protection:** Prevents abuse and DoS attacks

#### 3. Telegram WebApp Validation
- **initData validation:** Uses Telegram's unique session data
- **Timestamp validation:** Prevents replay attacks (5-minute window)
- **Platform detection:** Validates Telegram WebApp environment

#### 4. Security Headers
- **HTTPS enforcement:** Redirects HTTP to HTTPS
- **Cache control:** Prevents sensitive data caching
- **CORS protection:** Restricts cross-origin requests

### Security Configuration
```python
# Rate limiting
RATE_LIMIT_REQUESTS_PER_HOUR = 100
RATE_LIMIT_BLOCK_DURATION = 3600

# HMAC settings
HMAC_SECRET = os.environ.get('HMAC_SECRET', 'default-secret')
HMAC_ALGORITHM = 'sha256'

# Timestamp validation
TIMESTAMP_TOLERANCE = 300  # 5 minutes
```

## 📊 Performance Optimizations

### Implemented Optimizations

#### 1. API Response Caching
- **In-memory caching:** Fast access to frequently requested data
- **TTL-based expiration:** Automatic cache invalidation
- **Cache headers:** Proper HTTP caching directives

#### 2. Image Lazy Loading
- **Intersection Observer:** Loads images when visible
- **Bandwidth reduction:** 20-30% less data transfer
- **Performance improvement:** Faster initial page load

#### 3. CSS Optimization
- **Critical CSS inlining:** Above-the-fold content loads first
- **CSS minification:** Reduced file sizes
- **Custom properties:** Consistent theming

#### 4. JavaScript Optimization
- **Module splitting:** Separated concerns for better maintainability
- **Lazy loading:** Load modules on demand
- **Service worker:** Offline caching capabilities

### Performance Metrics
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| API Response Time | 200-500ms | 50-100ms | 75-80% |
| WebApp Load Time | 3-5s | 1-2s | 60-70% |
| Image Loading | Eager | Lazy | 20-30% bandwidth |
| Cache Hit Rate | 0% | 85-90% | New feature |

## 🛠️ Development

### Project Structure
```
BakeryMiniAppServer/
├── bot/                    # Main application code
│   ├── web_app/           # Web application files
│   │   ├── index.html     # Main HTML file
│   │   ├── script.js      # JavaScript application
│   │   ├── style.css      # CSS styles
│   │   └── images/        # Static images
│   ├── api_server.py      # API server
│   ├── main.py           # Bot main file
│   ├── parser.py         # Product parser
│   └── config.py         # Configuration
├── data/                  # Data files
│   ├── products_scraped.json
│   └── order_counter.json
├── tests/                 # Test files
├── scripts/              # Utility scripts
└── docs/                 # Documentation
```

### Key Features

#### 1. Customer Data Persistence
- **Automatic form population:** Remembers customer information
- **1-year storage:** Data persists for repeat customers
- **Privacy-focused:** Local storage only, no server-side storage

#### 2. Product Management
- **Automatic parsing:** Updates product data hourly
- **Category filtering:** Organized product display
- **Image optimization:** Lazy loading and compression

#### 3. Order Processing
- **Cart management:** Add/remove items with quantity control
- **Form validation:** Comprehensive input validation
- **Order tracking:** Unique order numbers and status

### API Endpoints
```
GET /bot-app/api/products          # Get all products
GET /bot-app/api/products?category=bread  # Get products by category
GET /bot-app/api/categories        # Get product categories
GET /bot-app/api/auth/token        # Get authentication token
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/

# Run with coverage
python -m pytest --cov=bot tests/
```

### Test Categories
- **Unit Tests:** Individual function testing
- **Integration Tests:** API endpoint testing
- **Security Tests:** Security feature validation
- **Performance Tests:** Load and stress testing

## 📈 Monitoring

### Security Monitoring
- **Rate limit tracking:** Monitor for abuse patterns
- **Failed authentication:** Track invalid access attempts
- **Security events:** Log all security-related activities

### Performance Monitoring
- **Response times:** Track API performance
- **Error rates:** Monitor application health
- **Cache hit rates:** Optimize caching strategies

### Logging
```python
# Security events
logger.warning(f"Rate limit exceeded for IP {client_ip}")
logger.warning(f"Invalid signature from {client_ip}")

# Performance metrics
logger.info(f"Request: {request.path} - {duration:.3f}s - {response.status}")
```

## 🔧 Maintenance

### Regular Tasks

#### 1. Security Updates
- **Dependency updates:** Keep packages current
- **Security scans:** Run bandit and pip-audit
- **Token rotation:** Regenerate bot tokens quarterly

#### 2. Performance Monitoring
- **Cache optimization:** Monitor hit rates
- **Database cleanup:** Remove old data
- **Log rotation:** Manage log file sizes

#### 3. Data Management
- **Product updates:** Ensure fresh product data
- **Order cleanup:** Archive old orders
- **Backup verification:** Test restore procedures

### Automated Tasks
```bash
# Security audit
bandit -r . -f json -o bandit-report.json
pip-audit --format=json --output=pip-audit-report.json

# Performance testing
python -m pytest tests/performance/ -v

# Data backup
python scripts/backup_data.py
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Bot Not Responding
- Check bot token validity
- Verify webhook configuration
- Review application logs

#### 2. API Errors
- Check environment variables
- Verify HMAC secret configuration
- Review rate limiting settings

#### 3. Performance Issues
- Monitor cache hit rates
- Check database query performance
- Review image loading optimization

### Debug Commands
```bash
# Check bot status
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Test API endpoints
curl -H "X-Signature: <signature>" https://your-app.herokuapp.com/bot-app/api/products

# View application logs
heroku logs --tail
```

## 📚 Additional Resources

### Documentation Files
- `README.md` - Basic setup and deployment
- `HEROKU_SETUP.md` - Detailed Heroku configuration
- `SECURITY.md` - Security policy and reporting
- `FINAL_SETUP.md` - Complete setup guide

### Configuration Files
- `app.json` - Heroku application configuration
- `Procfile` - Heroku process definitions
- `requirements.txt` - Python dependencies
- `env.example` - Environment variable template

### Scripts
- `build.sh` - Build and cache busting
- `deploy.sh` - Deployment automation
- `run_parser.py` - Product parser execution
- `scheduler.py` - Task scheduling

## 🔄 Version History

### Current Version: 1.3.108
- ✅ HMAC signature authentication
- ✅ Rate limiting implementation
- ✅ Telegram WebApp validation
- ✅ Performance optimizations
- ✅ Security enhancements

### Previous Versions
- **1.3.97:** Initial security implementation
- **1.3.95:** Customer data persistence
- **1.3.90:** Performance optimizations
- **1.3.85:** Basic functionality

---

**Last Updated:** 2025-09-03  
**Maintainer:** Development Team  
**Security Contact:** security@drazhin.by
