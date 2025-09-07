# 🛠️ Development Guide - Bakery Mini App Server

## 🏗️ Project Architecture

### Code Structure
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
│   ├── config.py         # Configuration
│   ├── keyboards.py      # Telegram keyboards
│   ├── security_manager.py # Security manager
│   ├── security.py       # Security functions
│   ├── security_middleware.py # Security middleware
│   └── security_headers.py # Security headers
├── data/                  # Data files
│   ├── products_scraped.json
│   └── order_counter.json
├── tests/                 # Test files
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── web_app/          # Web app tests
├── scripts/              # Utilities
│   ├── normalize_cache.py
│   └── bump_cache.sh
└── docs/                 # Documentation
```

## 🔧 Main Components

### 1. Bot Main (bot/main.py)
Main bot file containing:
- Bot and dispatcher initialization
- Command and message handlers
- Cart and order logic
- Email notifications

### 2. API Server (bot/api_server.py)
HTTP API server for WebApp:
- Product and category endpoints
- HMAC authentication
- Rate limiting
- Security headers

### 3. Configuration (bot/config.py)
Configuration management:
- SecureConfig class
- Environment variable validation
- Security settings

### 4. Security Manager (bot/security_manager.py)
Centralized security management:
- HMAC signatures
- Rate limiting
- Webhook validation
- Security monitoring

## 🧪 Testing

### Test Structure
```
tests/
├── unit/                 # Unit tests
│   ├── test_api_server.py
│   ├── test_config.py
│   ├── test_keyboards.py
│   ├── test_main.py
│   ├── test_orders.py
│   ├── test_cart.py
│   ├── test_security_features.py
│   └── ...
├── integration/          # Integration tests
│   └── test_api_integration.py
└── web_app/             # Web app tests
    ├── test_checkout_validation.py
    └── test_script.js
```

### Running Tests
```bash
# All tests
python -m pytest tests/

# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# With coverage
python -m pytest --cov=bot tests/

# Specific test
python -m pytest tests/unit/test_api_server.py -v
```

### Test Categories
- **Unit Tests:** Individual function testing
- **Integration Tests:** API endpoint testing
- **Security Tests:** Security function validation
- **Web App Tests:** Frontend functionality testing

## 🔄 Development

### Development Environment Setup
```bash
# Clone repository
git clone https://github.com/your-username/BakeryMiniAppServer.git
cd BakeryMiniAppServer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Local Development
```bash
# Setup environment variables
cp env.example .env
# Edit .env file

# Run in development mode
python bot/main.py
```

### Code Structure

#### Main Principles
- **Modularity:** Each component in separate file
- **Security:** All functions checked for security
- **Testability:** Code covered with tests
- **Documentation:** All functions documented

#### Code Style
```python
# Example function structure
async def process_order(order_data: dict, user_id: int) -> dict:
    """
    Process user order.
    
    Args:
        order_data: Order data
        user_id: User ID
        
    Returns:
        dict: Order processing result
        
    Raises:
        ValidationError: For invalid order data
    """
    # Input data validation
    if not validate_order_data(order_data):
        raise ValidationError("Invalid order data")
    
    # Order processing
    result = await _process_order_internal(order_data, user_id)
    
    return result
```

## 📊 Monitoring and Logging

### Logging
```python
import logging

logger = logging.getLogger(__name__)

# Different logging levels
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

### Performance Monitoring
```python
import time

async def monitored_function():
    start_time = time.time()
    
    # Function execution
    result = await some_operation()
    
    duration = time.time() - start_time
    logger.info(f"Operation completed in {duration:.3f}s")
    
    return result
```

## 🔧 Development Utilities

### Scripts
```bash
# Cache update
python scripts/normalize_cache.py

# Version update
bash scripts/bump_cache.sh

# Run parser
python run_parser.py

# Task scheduler
python scheduler.py
```

### Development Tools
```bash
# Code checking
flake8 bot/
black bot/
isort bot/

# Security checking
bandit -r bot/
pip-audit

# Testing
pytest tests/ -v --cov=bot
```

## 🚀 Development Process

### Workflow
1. **Create branch** for new feature
2. **Development** with test writing
3. **Testing** all components
4. **Code review** and security check
5. **Merge** to main branch
6. **Deploy** to staging/production

### Git Workflow
```bash
# Create branch
git checkout -b feature/new-feature

# Development
git add .
git commit -m "Add new feature"

# Push
git push origin feature/new-feature

# Create Pull Request
# After review - merge
git checkout main
git pull origin main
```

## 📋 Checklists

### Before Commit
- [ ] Code tested
- [ ] Tests pass
- [ ] Security checked
- [ ] Documentation updated
- [ ] Logging added

### Before Deployment
- [ ] All tests pass
- [ ] Security audit completed
- [ ] Performance tests passed
- [ ] Documentation current
- [ ] Backup created

## 🔍 Debugging

### Local Debugging
```python
import pdb

# Breakpoint
pdb.set_trace()

# Or use IDE debugger
```

### Production Debugging
```bash
# View logs
heroku logs --tail

# Connect to app
heroku run bash

# Check environment variables
heroku config
```

---

**Last Updated:** 2025-09-07  
**Maintained by:** Development Team