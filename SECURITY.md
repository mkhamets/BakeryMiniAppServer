# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.3.x   | :white_check_mark: |
| < 1.3   | :x:                |

## Reporting a Vulnerability

We take the security of our Telegram bot and WebApp seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to **security@drazhin.by**.

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the requested information listed below (as much as you can provide) to help us better understand the nature and scope of the possible issue:

- Type of issue (buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the vulnerability
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.

## Security Features

Our application includes the following security measures:

### Bot Security
- Environment-based configuration (no hardcoded secrets)
- Rate limiting for bot interactions
- Input validation and sanitization
- Webhook security monitoring and automatic cleanup
- Security event logging and monitoring

### WebApp Security
- Content Security Policy (CSP) headers
- X-Frame-Options, X-Content-Type-Options, and other security headers
- CORS restrictions to known origins
- Input validation for all user data
- Secure session management

### API Security
- Rate limiting for API endpoints
- Input validation for all API requests
- Security headers on all responses
- CORS restrictions
- Content hash-based ETags

### Development Security
- Automated security scanning (CodeQL, Bandit, pip-audit)
- Pre-commit hooks for security checks
- Secrets detection and prevention
- Regular dependency vulnerability scanning

## Security Best Practices

### For Users
- Never share your bot token or API keys
- Use strong, unique passwords
- Keep your Telegram app updated
- Be cautious of suspicious messages or links

### For Developers
- Always use environment variables for sensitive data
- Validate all user input
- Keep dependencies updated
- Follow secure coding practices
- Run security scans regularly

## Security Updates

We regularly update our security measures and dependencies. Security updates are typically released as patch versions (e.g., 1.3.1, 1.3.2).

## Acknowledgments

We would like to thank all security researchers who responsibly disclose vulnerabilities to us. Your contributions help make our application more secure for everyone.

## Contact

- **Security Email**: security@drazhin.by
- **Security Policy**: https://github.com/your-username/BakeryMiniAppServer/blob/main/SECURITY.md
- **Security.txt**: https://bakery-mini-app-server-440955f475ad.herokuapp.com/.well-known/security.txt

---

*This security policy is based on the [GitHub Security Policy template](https://github.com/github/securitylab/blob/main/SECURITY.md).*
