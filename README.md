🔵 BlueShield — OWASP Top 10 Web Application & API Security Scanner
   
A comprehensive, web-based penetration testing tool for discovering and reproducing OWASP Top 10 vulnerabilities in web applications and APIs.
Features • Installation • Usage • Vulnerabilities • API Testing • Screenshots • Disclaimer
________________________________________
✨ Features
Feature	Description
🔍 OWASP Top 10 Scanner	Automated testing against all 10 OWASP categories with severity classification
🎯 API Security Tester	Custom REST API endpoint testing with multiple injection vectors
📋 Step-by-Step Reproduction	Every finding includes numbered reproduction steps and exact payloads
⚡ Ready-to-Use Payloads	Copy-paste curl commands, URLs, and exploit payloads for each vulnerability
🔐 SSL/TLS Analysis	Weak cipher detection, deprecated protocol identification, certificate validation
🛡️ Security Headers Audit	Checks for CSP, HSTS, X-Frame-Options, and 7 other critical headers
🔧 Technology Detection	Identifies frameworks, servers, and libraries with known CVEs
📊 Risk Dashboard	Visual severity statistics with Critical / High / Medium / Low breakdown
🎨 Clean UI	White & red professional interface optimized for security assessments
________________________________________
🚀 Quick Start
Prerequisites
•	Python 3.8 or higher
•	pip package manager
Installation
# Clone the repository
git clone https://github.com/divine0472/blueshield.git
cd blueshield

# Install dependencies
pip install -r requirements.txt

# Or install manually
pip install flask requests
Running the Scanner
python blueshield_scanner.py
Then open your browser and navigate to:
http://localhost:5000
________________________________________
📖 Usage
Web Application Scanning
1.	Enter your target URL (must start with http:// or https://)
2.	Select scan depth: Quick, Standard, or Deep
3.	Click Start Scan
4.	Review findings with reproduction steps and payloads
API Security Testing
1.	Navigate to the API Tester tab
2.	Enter your API endpoint and select HTTP method
3.	Configure headers, body, and authentication
4.	Select which security tests to run (SQLi, XSS, XXE, etc.)
5.	Click Send & Test Security
6.	Each vulnerability includes auto-generated curl commands
________________________________________
🛡️ Vulnerability Coverage
OWASP Top 10 (2021)
ID	Category	Tests Performed	Payloads Provided
A01	Broken Access Control	Path traversal, CORS misconfig, exposed admin panels, .git/.env leaks	✅ Yes
A02	Cryptographic Failures	Weak TLS/SSL versions, deprecated ciphers, hardcoded secrets, missing HTTPS	✅ Yes
A03	Injection	SQL Injection (error-based, time-based, union), Command Injection, LDAP Injection	✅ Yes
A04	Insecure Design	IDOR endpoints, exposed password reset, missing rate limiting	✅ Yes
A05	Security Misconfiguration	Missing security headers, verbose errors, dangerous HTTP methods, version disclosure	✅ Yes
A06	Vulnerable Components	Technology fingerprinting, exposed admin interfaces (phpMyAdmin, Swagger, etc.)	✅ Yes
A07	Authentication Failures	Weak password policies, missing CAPTCHA, insecure cookie flags, brute force vectors	✅ Yes
A08	Data Integrity Failures	Deserialization detection, XXE endpoints, unrestricted file uploads	✅ Yes
A09	Logging & Monitoring	Exposed log files, generic error handling, missing audit trails	✅ Yes
A10	SSRF	URL parameter injection, callback endpoints, AWS metadata access	✅ Yes
API Injection Tests
•	SQL Injection — Boolean-based, error-based, time-based, UNION-based
•	NoSQL Injection — MongoDB operator bypass ($gt, $ne, $regex)
•	XSS — Reflected payload testing with script tags and event handlers
•	XXE — XML External Entity with file read attempts
•	Command Injection — Shell metacharacter injection (;, |, `, $())
•	Path Traversal — Directory traversal for Unix and Windows systems
________________________________________
📋 Example Reproduction Output
When BlueShield finds a vulnerability, it provides everything you need to reproduce it:
Sample: SQL Injection Finding
┌─────────────────────────────────────────────────────────────┐
│  A03 - Injection (SQL/NoSQL/Command)        [CRITICAL]      │
└─────────────────────────────────────────────────────────────┘

Findings:
  • SQL Injection vulnerability (error-based) in parameter: id

How to Reproduce:
  1. Open https://target.com/?id=1 in browser (baseline)
  2. Modify id parameter to: ' OR '1'='1
  3. Send request to: https://target.com/?id=%27+OR+%271%27%3D%271
  4. Observe SQL error message in response

Payloads & Commands:
  curl "https://target.com/?id=' OR '1'='1"
  curl "https://target.com/?id=1' AND 1=1--"
  curl "https://target.com/?id=' UNION SELECT NULL--"

Recommendation:
  Use parameterized queries, input validation, ORMs, and escape 
  special characters.
Sample: API Test with curl Command
Test: SQL Injection (Boolean-based)
Payload: ' OR '1'='1
Status: CRITICAL

How to Reproduce:
  1. Send POST request to https://api.target.com/users
  2. Include payload in request body: {"name": "' OR '1'='1"}
  3. Observe response for vulnerability indicators
  4. Status code: 500

curl Command:
  curl -X POST 'https://api.target.com/users' \
    -H 'Authorization: Bearer eyJ0...' \
    -H 'Content-Type: application/json' \
    -d '{"name":"'\'' OR '\''1'\''='\''1"}'
________________________________________
🏗️ Project Structure
blueshield/
├── blueshield_scanner.py    # Main Flask application (all-in-one)
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── LICENSE                # MIT License
________________________________________
⚙️ Configuration
Scan Depth Levels
Level	Description	Use Case
Quick	Basic checks only, no time-based tests	Fast initial assessment
Standard	Full test suite with moderate depth	Regular security audits
Deep	Extended time-based tests and exhaustive checks	Thorough penetration test
Environment Variables
# Optional: Change default port
export REDSHIELD_PORT=8080

# Optional: Set custom User-Agent
export REDSHIELD_UA="Custom-Security-Scanner/1.0"
________________________________________
🔒 Security & Legal
⚠️ IMPORTANT DISCLAIMER
BlueShield is intended for authorized security testing only.
•	✅ DO scan applications you own
•	✅ DO scan applications you have explicit written authorization to test
•	❌ DO NOT scan third-party websites without permission
•	❌ DO NOT use this tool for malicious purposes
Unauthorized access to computer systems is illegal under: - US: Computer Fraud and Abuse Act (CFAA) - EU: Directive on Attacks against Information Systems - UK: Computer Misuse Act 1990 - Other jurisdictions: Applicable cybercrime laws
The authors assume no liability for misuse or damage caused by this tool.
________________________________________
🤝 Contributing
Contributions are welcome! Please follow these guidelines:
1.	Fork the repository
2.	Create a feature branch (git checkout -b feature/amazing-feature)
3.	Commit your changes (git commit -m 'Add amazing feature')
4.	Push to the branch (git push origin feature/amazing-feature)
5.	Open a Pull Request
Areas for Contribution
•	☐ Additional OWASP test cases
•	☐ New API authentication methods (OAuth2, JWT validation)
•	☐ PDF/CSV report export
•	☐ Docker containerization
•	☐ CI/CD pipeline integration
•	☐ WebSocket security testing
•	☐ GraphQL injection tests
________________________________________
📝 Requirements
Flask>=2.0.0
requests>=2.25.0
See requirements.txt for full dependency list.
________________________________________
📜 License
This project is licensed under the MIT License — see the LICENSE file for details.
________________________________________
🙏 Acknowledgments
•	OWASP Foundation for the OWASP Top 10 standard
•	PortSwigger Web Security Academy for vulnerability research
•	The open-source security community for payload databases and testing methodologies
________________________________________
Built with ❤️ for defensive security professionals BlueShield — Find it. Reproduce it. Fix it.
