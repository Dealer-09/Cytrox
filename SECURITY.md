# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in RepoShield-AI, please email security@reposhield.io instead of using the public issue tracker.

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Your suggested fix (if any)

## Security Best Practices

### For Deployment
1. Use HTTPS in production
2. Keep dependencies updated
3. Rotate secrets regularly
4. Enable webhook signature verification
5. Use strong JWT secrets
6. Encrypt sensitive data at rest
7. Implement rate limiting
8. Monitor for unusual activity
9. Use managed databases with backups
10. Implement proper access controls

### For Users
1. Use strong GitHub OAuth tokens
2. Enable 2FA on GitHub accounts
3. Review subscription and payment methods
4. Be cautious with private repository scanning
5. Don't commit secrets before scanning

## Supported Versions

| Version | Supported          |
|---------|-------------------|
| 2.x     | Active support  |
| 1.x     | Deprecated      |

## Security Features

Zero Code Execution (Static Analysis Only)
OAuth 2.0 Authentication
JWT with Expiration
HMAC-SHA256 Webhook Signatures
Encrypted Token Storage
Rate Limiting
CSRF Protection
SQL Injection Prevention (SQLAlchemy ORM)
XSS Protection
CORS Enforcement

## Dependencies

We maintain security by:
- Scanning dependencies with Snyk
- Updating critical vulnerabilities promptly
- Using well-maintained packages
- Avoiding unmaintained alternatives

## Updates

Security updates are released as patch versions (2.0.1, 2.0.2, etc.) and should be deployed immediately.

---

Last updated: 2026-03-24
