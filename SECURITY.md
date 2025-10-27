# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| develop | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of the TTA (Therapeutic Text Adventure) project seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to:
- **Email:** theinternetisbig@gmail.com
- **Subject:** [SECURITY] TTA Vulnerability Report

### What to Include

Please include the following information in your report:

1. **Type of vulnerability** (e.g., SQL injection, XSS, authentication bypass)
2. **Full paths of source file(s)** related to the vulnerability
3. **Location of the affected source code** (tag/branch/commit or direct URL)
4. **Step-by-step instructions** to reproduce the issue
5. **Proof-of-concept or exploit code** (if possible)
6. **Impact of the vulnerability** (what an attacker could achieve)
7. **Suggested fix** (if you have one)

### What to Expect

- **Acknowledgment:** We will acknowledge receipt of your vulnerability report within 48 hours
- **Updates:** We will send you regular updates about our progress
- **Timeline:** We aim to resolve critical vulnerabilities within 7 days
- **Credit:** We will credit you in our security advisory (unless you prefer to remain anonymous)

### Security Update Process

1. **Triage:** We will confirm the vulnerability and determine its severity
2. **Fix:** We will develop and test a fix
3. **Release:** We will release a security patch
4. **Disclosure:** We will publish a security advisory with details

## Security Features

The TTA repository has the following security features enabled:

### Automated Security

- ✅ **Secret Scanning:** Automatically detects accidentally committed secrets
- ✅ **Secret Scanning Push Protection:** Prevents secrets from being pushed
- ✅ **Dependabot Security Updates:** Automatically creates PRs for vulnerable dependencies
- ✅ **Branch Protection:** Main branch requires PR reviews and passing tests
- ✅ **Pre-commit Hooks:** Bandit security scanning runs before commits

### Manual Security Practices

- **Code Review:** All changes require review before merging to main
- **Security Scanning:** Semgrep, CodeQL, Trivy, TruffleHog, and GitLeaks in CI/CD
- **Dependency Audits:** Regular dependency vulnerability scanning
- **Access Control:** Minimal permissions principle for all integrations

## Security Best Practices for Contributors

### For Developers

1. **Never commit secrets** (API keys, passwords, tokens)
   - Use environment variables
   - Use `.env` files (which are gitignored)
   - Use GitHub Secrets for CI/CD

2. **Keep dependencies updated**
   - Review and merge Dependabot PRs promptly
   - Check for security advisories regularly

3. **Follow secure coding practices**
   - Validate all user inputs
   - Use parameterized queries (prevent SQL injection)
   - Sanitize outputs (prevent XSS)
   - Use secure authentication methods

4. **Run security checks locally**
   ```bash
   # Run pre-commit hooks
   pre-commit run --all-files

   # Run security scan
   uv run bandit -r src/

   # Check for secrets
   git secrets --scan
   ```

### For Users

1. **Keep your API keys secure**
   - Never share your OpenRouter API key
   - Rotate keys if compromised
   - Use environment-specific keys

2. **Report suspicious activity**
   - Contact us immediately if you notice unusual behavior
   - Check for security advisories regularly

3. **Use secure connections**
   - Always use HTTPS
   - Verify SSL certificates
   - Use secure WebSocket connections (WSS)

## Known Security Considerations

### Therapeutic Data

- **Patient Privacy:** All therapeutic data must be handled according to HIPAA guidelines
- **Data Encryption:** Sensitive data should be encrypted at rest and in transit
- **Access Logging:** All access to therapeutic data is logged
- **Data Retention:** Follow data retention policies for therapeutic applications

### AI Model Integration

- **API Key Security:** OpenRouter API keys must be kept secure
- **Rate Limiting:** Implement rate limiting to prevent abuse
- **Input Validation:** All AI inputs must be validated and sanitized
- **Output Filtering:** AI outputs should be filtered for inappropriate content

### Database Security

- **Neo4j Security:** Use strong passwords and enable authentication
- **Redis Security:** Use password authentication and disable dangerous commands
- **Connection Security:** Use encrypted connections (TLS/SSL)
- **Backup Security:** Encrypt database backups

## Security Advisories

Security advisories will be published at:
- **GitHub Security Advisories:** https://github.com/theinterneti/TTA/security/advisories
- **Repository Releases:** https://github.com/theinterneti/TTA/releases

Subscribe to repository notifications to receive security updates.

## Compliance

The TTA project aims to comply with:

- **HIPAA:** Health Insurance Portability and Accountability Act (for therapeutic data)
- **GDPR:** General Data Protection Regulation (for EU users)
- **OWASP Top 10:** Common web application security risks
- **CWE Top 25:** Most dangerous software weaknesses

## Security Contacts

- **Primary Contact:** theinternetisbig@gmail.com
- **GitHub Security:** https://github.com/theinterneti/TTA/security

## Acknowledgments

We would like to thank the following individuals for responsibly disclosing security vulnerabilities:

- *No vulnerabilities reported yet*

---

**Last Updated:** October 4, 2025
**Version:** 1.0
