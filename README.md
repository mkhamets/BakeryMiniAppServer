# 🥖 Bakery Mini App Server

Telegram WebApp for Drazhin Bakery with full bakery ordering functionality.

## 🎯 Overview

This project is a fully functional Telegram WebApp for a bakery, including:
- Product catalog with categories
- Shopping cart
- Order processing
- Email notifications
- Security system

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

### Additional Environment Variables
```bash
ADMIN_EMAIL_PASSWORD=your_smtp_password
SMTP_SERVER=smtp.gmail.com
HMAC_SECRET=your_hmac_secret_key
```

## 🚀 Deployment

### Heroku (Recommended)

1. **Create Heroku app:**
```bash
heroku create your-app-name
```

2. **Set environment variables:**
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

## 🛠️ Project Structure

```
BakeryMiniAppServer/
├── bot/                    # Main application code
│   ├── web_app/           # Web application files
│   │   ├── index.html     # Main HTML file
│   │   ├── script.js      # JavaScript application
│   │   ├── style.css      # CSS styles
│   │   └── images/        # Static images
│   ├── api_server.py      # API server
│   ├── main.py           # Main bot file
│   ├── parser.py         # Product parser
│   └── config.py         # Configuration
├── data/                  # Data files
│   ├── products_scraped.json
│   └── order_counter.json
├── tests/                 # Test files
├── scripts/              # Utilities
└── docs/                 # Documentation
```

## 🔑 Key Features

### 1. Customer Data Management
- **Form Auto-fill:** Remembers customer information
- **1 Year Storage:** Data saved for returning customers
- **Privacy:** Local storage only, no server-side storage

### 2. Product Management
- **Automatic Parsing:** Updates product data every hour
- **Category Filtering:** Organized product display
- **Image Optimization:** Lazy loading and compression

### 3. Order Processing
- **Cart Management:** Add/remove items with quantity control
- **Form Validation:** Comprehensive input validation
- **Order Tracking:** Unique order numbers and status

## 📊 API Endpoints

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
- **Security Tests:** Security function validation
- **Performance Tests:** Load and stress testing

## 🔄 Version History

### Current Version: 1.3.108
- ✅ HMAC signature authentication
- ✅ Rate limiting implementation
- ✅ Telegram WebApp validation
- ✅ Security improvements

### Previous Versions
- **1.3.97:** Initial security implementation
- **1.3.95:** Customer data storage
- **1.3.90:** Basic functionality
- **1.3.85:** Core functionality

---

**Last Updated:** 2025-09-07  
**Maintained by:** Development Team  
**Security Contact:** security@drazhin.by