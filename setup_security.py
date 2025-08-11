#!/usr/bin/env python3
"""
Security Setup Script for Bakery Bot
This script helps configure and validate all security features.
"""

import os
import sys
import json
import subprocess
import requests
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section."""
    print(f"\n--- {title} ---")

def check_python_version():
    """Check if Python version is compatible."""
    print_section("Python Version Check")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ required.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    print_section("Dependencies Check")
    
    required_packages = [
        'aiogram', 'aiohttp', 'aiohttp-cors', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_environment_file():
    """Check if .env file exists and has required variables."""
    print_section("Environment Configuration")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("📝 Copy env.example to .env and fill in your values")
        return False
    
    print("✅ .env file found")
    
    # Load and check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'BOT_TOKEN',
        'ADMIN_CHAT_ID', 
        'ADMIN_EMAIL',
        'ADMIN_EMAIL_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            print(f"❌ {var} - Not set")
            missing_vars.append(var)
        else:
            # Mask sensitive values
            if 'TOKEN' in var or 'PASSWORD' in var:
                masked_value = value[:8] + '*' * (len(value) - 8) if len(value) > 8 else '***'
                print(f"✅ {var} - {masked_value}")
            else:
                print(f"✅ {var} - {value}")
    
    if missing_vars:
        print(f"\n⚠️  Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def validate_bot_token():
    """Validate bot token with Telegram API."""
    print_section("Bot Token Validation")
    
    bot_token = os.environ.get('BOT_TOKEN')
    if not bot_token:
        print("❌ BOT_TOKEN not set")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data['result']
                print(f"✅ Bot token valid")
                print(f"   Bot name: {bot_info.get('first_name', 'Unknown')}")
                print(f"   Username: @{bot_info.get('username', 'Unknown')}")
                print(f"   Bot ID: {bot_info.get('id', 'Unknown')}")
                return True
            else:
                print(f"❌ Bot token invalid: {data.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def check_webhook_security():
    """Check current webhook security status."""
    print_section("Webhook Security Check")
    
    bot_token = os.environ.get('BOT_TOKEN')
    if not bot_token:
        print("❌ BOT_TOKEN not set")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                webhook_info = data['result']
                url = webhook_info.get('url', '')
                
                if not url:
                    print("✅ No webhook set - Using long polling (secure)")
                    return True
                else:
                    print(f"⚠️  Webhook is set to: {url}")
                    
                    # Check for suspicious patterns
                    suspicious_patterns = [
                        'botelegram.work.gd', 'casino', 'spam', 'malicious'
                    ]
                    
                    for pattern in suspicious_patterns:
                        if pattern.lower() in url.lower():
                            print(f"🚨 SUSPICIOUS WEBHOOK DETECTED!")
                            print(f"   Pattern: {pattern}")
                            print(f"   URL: {url}")
                            print("   ⚠️  This webhook should be deleted immediately!")
                            return False
                    
                    print("⚠️  Webhook detected - Monitor for suspicious activity")
                    return True
            else:
                print(f"❌ Failed to get webhook info: {data.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def check_smtp_configuration():
    """Check SMTP configuration."""
    print_section("SMTP Configuration Check")
    
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = os.environ.get('SMTP_PORT', '587')
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_EMAIL_PASSWORD')
    
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"Admin Email: {admin_email}")
    
    if not admin_password:
        print("❌ ADMIN_EMAIL_PASSWORD not set")
        return False
    
    if admin_email and '@gmail.com' in admin_email:
        print("ℹ️  Gmail detected - Make sure you're using an App Password")
        print("   Enable 2FA and generate App Password at: https://myaccount.google.com/apppasswords")
    
    print("✅ SMTP configuration appears valid")
    return True

def generate_security_report():
    """Generate a comprehensive security report."""
    print_section("Security Report")
    
    report = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "environment_vars": {
            "BOT_TOKEN": "SET" if os.environ.get('BOT_TOKEN') else "NOT SET",
            "ADMIN_CHAT_ID": "SET" if os.environ.get('ADMIN_CHAT_ID') else "NOT SET",
            "ADMIN_EMAIL": "SET" if os.environ.get('ADMIN_EMAIL') else "NOT SET",
            "ADMIN_EMAIL_PASSWORD": "SET" if os.environ.get('ADMIN_EMAIL_PASSWORD') else "NOT SET",
        },
        "security_features": {
            "rate_limiting": os.environ.get('ENABLE_RATE_LIMITING', 'true').lower() == 'true',
            "security_monitoring": os.environ.get('ENABLE_SECURITY_MONITORING', 'true').lower() == 'true',
            "webhooks_allowed": os.environ.get('ALLOW_WEBHOOKS', 'false').lower() == 'true',
            "log_security_events": os.environ.get('LOG_SECURITY_EVENTS', 'true').lower() == 'true'
        }
    }
    
    # Save report to file
    report_file = Path('security_report.json')
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📊 Security report saved to: {report_file}")
    print(f"🔒 Rate Limiting: {'Enabled' if report['security_features']['rate_limiting'] else 'Disabled'}")
    print(f"🔒 Security Monitoring: {'Enabled' if report['security_features']['security_monitoring'] else 'Disabled'}")
    print(f"🔒 Webhooks: {'Allowed' if report['security_features']['webhooks_allowed'] else 'Blocked'}")
    print(f"🔒 Security Logging: {'Enabled' if report['security_features']['log_security_events'] else 'Disabled'}")

def main():
    """Main security setup function."""
    print_header("BAKERY BOT SECURITY SETUP")
    
    checks = [
        check_python_version,
        check_dependencies,
        check_environment_file,
        validate_bot_token,
        check_webhook_security,
        check_smtp_configuration
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    if all_passed:
        print_header("✅ ALL SECURITY CHECKS PASSED")
        print("Your bot is configured securely!")
    else:
        print_header("⚠️  SECURITY ISSUES DETECTED")
        print("Please fix the issues above before running your bot.")
    
    generate_security_report()
    
    print_header("NEXT STEPS")
    if all_passed:
        print("1. ✅ Your bot is ready to run securely")
        print("2. 🔒 Security features are enabled")
        print("3. 📊 Monitor security logs regularly")
        print("4. 🔄 Run this script periodically to check security")
    else:
        print("1. ❌ Fix the security issues above")
        print("2. 🔧 Update your .env file with missing values")
        print("3. 🔒 Ensure webhook security")
        print("4. 🔄 Run this script again after fixes")
    
    print("\nFor more information, see the security documentation.")

if __name__ == "__main__":
    main()
