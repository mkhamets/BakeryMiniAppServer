# Overview

This is a Telegram Mini App for a bakery business, providing customers with a web-based ordering system. The application consists of a Python-based Telegram bot backend with an integrated web server serving a responsive web interface. Customers can browse bakery products organized by categories, manage shopping carts, place orders, and track deliveries. The system includes automated web scraping to keep product data current, comprehensive security features, and support for both pickup and delivery orders.

**Project Status**: Successfully imported and configured for Replit environment. The web application is running in demo mode on port 5000 and is fully functional for testing and development. To enable full Telegram bot functionality, environment variables for bot credentials need to be configured.

# User Preferences

Preferred communication style: Simple, everyday language.

# Recent Changes

**September 21, 2025**: 
- Successfully imported GitHub project to Replit environment
- Installed Python 3.11 and all required dependencies (aiogram, aiohttp, beautifulsoup4, etc.)
- Modified configuration to support demo mode without requiring Telegram bot credentials
- Set up main workflow to run on port 5000 with proper CORS configuration for Replit proxy
- Configured deployment settings for production use with autoscale target
- Application is now fully functional in demo mode with web interface accessible

# System Architecture

## Backend Architecture
- **Framework**: Built on aiogram 3.4.1 for Telegram bot functionality with aiohttp 3.9.1 for the web server
- **API Server**: Single aiohttp application serving both bot webhooks and web app endpoints with CORS support
- **Data Storage**: JSON-based file system for products, orders, and configuration data stored in the `data/` directory
- **Security Layer**: Comprehensive security manager with HMAC request signing, rate limiting, input validation, and webhook protection

## Frontend Architecture
- **Web Application**: Vanilla JavaScript SPA with Bootstrap styling integrated with Telegram WebApp API
- **Caching Strategy**: Multi-layered approach using browser localStorage, cache versioning, and service worker integration
- **Mobile-First Design**: Responsive interface optimized for mobile devices within Telegram's WebApp container
- **State Management**: Client-side cart management with localStorage persistence and server synchronization

## Product Data Management
- **Automated Scraping**: BeautifulSoup-based parser extracting products from drazhin.by website
- **Scheduling**: Configurable automatic updates via Heroku Scheduler or systemd service
- **Data Structure**: Category-based organization with support for availability tracking and product metadata
- **Cache Invalidation**: Version-controlled cache busting system across HTML, CSS, JS, and image assets

## Order Processing Pipeline
- **Order Generation**: Sequential order numbering with monthly reset functionality
- **Validation Layer**: Multi-stage validation for customer data, product availability, and business logic
- **Notification System**: SMTP-based email notifications for administrators and customers
- **Data Persistence**: JSON file storage with atomic writes and backup mechanisms

## Security Architecture
- **Request Authentication**: HMAC-SHA256 signing for API requests using Telegram WebApp initData
- **Rate Limiting**: Per-user and per-IP throttling with configurable limits and block durations  
- **Input Validation**: Comprehensive sanitization and validation for all user inputs
- **Content Security Policy**: Strict CSP headers allowing only necessary resources and Telegram origins
- **Webhook Security**: Telegram webhook signature verification and malicious webhook detection

## Deployment Strategy
- **Multi-Platform Support**: Configurations for Heroku, traditional VPS hosting, and containerized deployment
- **Environment Management**: Secure configuration via environment variables with validation
- **Process Management**: Support for both single-process and multi-worker deployment models
- **Health Monitoring**: Built-in endpoint monitoring and automatic recovery mechanisms

# External Dependencies

## Core Services
- **Telegram Bot API**: Primary interface for bot interactions and WebApp integration
- **Web Scraping Target**: drazhin.by bakery website for product data extraction
- **SMTP Services**: Gmail SMTP (configurable) for email notifications

## Development and Deployment
- **Heroku Platform**: Primary hosting platform with Scheduler addon for automated tasks
- **Alternative Hosting**: Support for traditional VPS hosting (Hoster.by, custom servers)
- **Version Control**: Git-based deployment workflows

## Frontend Libraries
- **Bootstrap CSS Framework**: Responsive UI components and grid system
- **Google Fonts**: Typography enhancement (Yeseva One font family)
- **Telegram WebApp API**: Native integration with Telegram's web application framework

## Monitoring and Security
- **Security Scanning**: Bandit for Python security analysis and pip-audit for dependency vulnerabilities
- **Rate Limiting Storage**: In-memory storage (production should use Redis)
- **SSL/TLS**: Automatic HTTPS via platform providers or reverse proxy configuration