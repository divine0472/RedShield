from flask import Flask, render_template_string, request
import requests
import urllib.parse
import re
import json
import time
from datetime import datetime
import ssl
import socket
import base64

app = Flask(__name__)
app.secret_key = 'pentest-scanner-secret-key-2024'

# ==================== HTML TEMPLATES ====================
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlueShield - OWASP Top 10 Security Scanner</title>
    <style>
        :root {
            --primary-red: #dc2626;
            --dark-red: #991b1b;
            --light-red: #fee2e2;
            --bg-white: #ffffff;
            --off-white: #fafafa;
            --text-dark: #1f2937;
            --text-gray: #6b7280;
            --border: #e5e7eb;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #dc2626;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: var(--off-white);
            color: var(--text-dark);
            line-height: 1.6;
        }
        .header {
            background: var(--bg-white);
            border-bottom: 3px solid var(--primary-red);
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 10px rgba(220, 38, 38, 0.1);
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--primary-red);
            letter-spacing: -0.5px;
        }
        .logo svg { width: 36px; height: 36px; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-links a {
            color: var(--text-dark);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95rem;
            padding: 0.5rem 0;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }
        .nav-links a:hover, .nav-links a.active {
            color: var(--primary-red);
            border-bottom-color: var(--primary-red);
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .scan-section {
            background: var(--bg-white);
            border-radius: 16px;
            padding: 3rem;
            margin-bottom: 2rem;
            border: 1px solid var(--border);
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        }
        .scan-title { font-size: 2rem; font-weight: 800; color: var(--text-dark); margin-bottom: 0.5rem; }
        .scan-subtitle { color: var(--text-gray); margin-bottom: 2rem; font-size: 1.1rem; }
        .scan-form { display: flex; gap: 1rem; flex-wrap: wrap; }
        .input-group { flex: 1; min-width: 300px; }
        .input-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--text-dark);
            font-size: 0.9rem;
        }
        .input-group input, .input-group select, .input-group textarea {
            width: 100%;
            padding: 0.875rem 1rem;
            border: 2px solid var(--border);
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.2s;
            background: var(--bg-white);
            font-family: inherit;
        }
        .input-group input:focus, .input-group select:focus, .input-group textarea:focus {
            outline: none;
            border-color: var(--primary-red);
            box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
        }
        .btn {
            padding: 0.875rem 2rem;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        .btn-primary {
            background: var(--primary-red);
            color: white;
        }
        .btn-primary:hover {
            background: var(--dark-red);
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
        }
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        .card {
            background: var(--bg-white);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border);
            transition: all 0.2s;
        }
        .card:hover {
            border-color: var(--primary-red);
            box-shadow: 0 4px 20px rgba(220, 38, 38, 0.08);
            transform: translateY(-2px);
        }
        .card-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }
        .card-icon {
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            font-weight: 700;
        }
        .card-icon.critical { background: var(--light-red); color: var(--primary-red); }
        .card-icon.high { background: #fef3c7; color: #d97706; }
        .card-icon.medium { background: #dbeafe; color: #2563eb; }
        .card-icon.low { background: #d1fae5; color: #059669; }
        .card-title { font-weight: 700; font-size: 1rem; color: var(--text-dark); }
        .card-desc { color: var(--text-gray); font-size: 0.875rem; line-height: 1.5; }
        .results-section {
            background: var(--bg-white);
            border-radius: 16px;
            padding: 2rem;
            border: 1px solid var(--border);
            margin-bottom: 2rem;
        }
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .results-title { font-size: 1.5rem; font-weight: 800; }
        .badge {
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
        }
        .badge-critical { background: var(--light-red); color: var(--primary-red); }
        .badge-high { background: #fef3c7; color: #b45309; }
        .badge-medium { background: #dbeafe; color: #1d4ed8; }
        .badge-low { background: #d1fae5; color: #047857; }
        .badge-pass { background: #d1fae5; color: #047857; }
        .vuln-item {
            border: 1px solid var(--border);
            border-radius: 12px;
            margin-bottom: 1rem;
            overflow: hidden;
        }
        .vuln-header {
            padding: 1rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            background: var(--bg-white);
            transition: background 0.2s;
        }
        .vuln-header:hover { background: var(--off-white); }
        .vuln-header.critical { border-left: 4px solid var(--danger); }
        .vuln-header.high { border-left: 4px solid var(--warning); }
        .vuln-header.medium { border-left: 4px solid #3b82f6; }
        .vuln-header.low { border-left: 4px solid var(--success); }
        .vuln-header.pass { border-left: 4px solid var(--success); }
        .vuln-name { font-weight: 700; font-size: 1rem; }
        .vuln-meta { display: flex; gap: 1rem; align-items: center; }
        .vuln-body {
            padding: 1.5rem;
            background: var(--off-white);
            border-top: 1px solid var(--border);
            display: none;
        }
        .vuln-body.active { display: block; }
        .vuln-section { margin-bottom: 1.5rem; }
        .vuln-section h4 {
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-gray);
            margin-bottom: 0.5rem;
        }
        .code-block {
            background: #1f2937;
            color: #e5e7eb;
            padding: 1rem;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
        }
        .recommendation {
            background: var(--light-red);
            border: 1px solid #fecaca;
            border-radius: 8px;
            padding: 1rem;
            color: var(--dark-red);
        }
        .stats-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .stat-box {
            background: var(--bg-white);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid var(--border);
        }
        .stat-number { font-size: 2.5rem; font-weight: 800; line-height: 1; }
        .stat-number.critical { color: var(--danger); }
        .stat-number.high { color: var(--warning); }
        .stat-number.medium { color: #3b82f6; }
        .stat-number.low { color: var(--success); }
        .stat-label { font-size: 0.875rem; color: var(--text-gray); margin-top: 0.5rem; font-weight: 600; }
        .loading-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(255,255,255,0.95);
            display: none;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            z-index: 1000;
        }
        .loading-overlay.active { display: flex; }
        .spinner {
            width: 60px;
            height: 60px;
            border: 4px solid var(--border);
            border-top-color: var(--primary-red);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .loading-text {
            margin-top: 1.5rem;
            font-weight: 700;
            color: var(--text-dark);
            font-size: 1.1rem;
        }
        .footer {
            text-align: center;
            padding: 2rem;
            color: var(--text-gray);
            font-size: 0.875rem;
            border-top: 1px solid var(--border);
            margin-top: 2rem;
        }
        .footer strong { color: var(--primary-red); }
        @media (max-width: 768px) {
            .stats-row { grid-template-columns: repeat(2, 1fr); }
            .scan-form { flex-direction: column; }
            .nav-links { display: none; }
            .container { padding: 1rem; }
            .scan-section { padding: 1.5rem; }
        }
        .toggle-icon {
            transition: transform 0.2s;
            font-size: 1.2rem;
            color: var(--text-gray);
        }
        .toggle-icon.rotated { transform: rotate(180deg); }
        .tab-bar {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
            border-bottom: 2px solid var(--border);
            padding-bottom: 0;
        }
        .tab-btn {
            padding: 0.75rem 1.5rem;
            border: none;
            background: none;
            font-weight: 600;
            cursor: pointer;
            color: var(--text-gray);
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
        }
        .tab-btn.active {
            color: var(--primary-red);
            border-bottom-color: var(--primary-red);
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .disclaimer {
            background: var(--light-red);
            border: 1px solid #fecaca;
            border-radius: 10px;
            padding: 1rem 1.5rem;
            margin-bottom: 2rem;
            color: var(--dark-red);
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .disclaimer svg { flex-shrink: 0; width: 24px; height: 24px; }
        .api-tester {
            background: var(--bg-white);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border);
            margin-bottom: 1rem;
        }
        .repro-box {
            background: #fffbeb;
            border: 1px solid #fcd34d;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .repro-box h5 {
            color: #92400e;
            font-size: 0.875rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .step-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .step-list li {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
            align-items: flex-start;
        }
        .step-num {
            background: var(--primary-red);
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 700;
            flex-shrink: 0;
        }
        .step-text {
            font-size: 0.9rem;
            color: var(--text-dark);
            line-height: 1.5;
        }
        .payload-tag {
            display: inline-block;
            background: var(--light-red);
            color: var(--dark-red);
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.8rem;
            font-weight: 600;
            margin: 0.15rem;
        }
        .curl-box {
            background: #1e293b;
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.8rem;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
            border-left: 3px solid var(--primary-red);
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <path d="M9 12l2 2 4-4"/>
            </svg>
            RedShield
        </div>
        <nav class="nav-links">
            <a href="/" class="active">Scanner</a>
            <a href="/api-tester">API Tester</a>
            <a href="/owasp-guide">OWASP Guide</a>
        </nav>
    </div>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner"></div>
        <div class="loading-text" id="loadingText">Initializing security scan...</div>
    </div>
    <div class="container">
        {{ content | safe }}
    </div>
    <div class="footer">
        <strong>BlueShield</strong> &mdash; Authorized Security Testing Only. Use responsibly.
    </div>
    <script>
        function toggleVuln(id) {
            const body = document.getElementById('vuln-body-' + id);
            const icon = document.getElementById('vuln-icon-' + id);
            body.classList.toggle('active');
            icon.classList.toggle('rotated');
        }
        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById('tab-' + tabId).classList.add('active');
            document.getElementById('content-' + tabId).classList.add('active');
        }
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert('Copied to clipboard!');
            });
        }
    </script>
</body>
</html>
"""

# ==================== PAGE TEMPLATES ====================
SCANNER_PAGE = """
<div class="disclaimer">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
    <span><strong>Important:</strong> Only scan applications you own or have explicit written authorization to test. Unauthorized scanning may violate laws.</span>
</div>

<div class="scan-section">
    <h1 class="scan-title">OWASP Top 10 Security Scanner</h1>
    <p class="scan-subtitle">Enter a target URL to perform a comprehensive security assessment against the OWASP Top 10 vulnerabilities.</p>
    <form class="scan-form" id="scanForm" onsubmit="startScan(event)">
        <div class="input-group">
            <label>Target URL</label>
            <input type="url" name="target_url" placeholder="https://example.com" required>
        </div>
        <div class="input-group" style="flex: 0.5; min-width: 150px;">
            <label>Scan Depth</label>
            <select name="scan_depth">
                <option value="quick">Quick Scan</option>
                <option value="standard" selected>Standard</option>
                <option value="deep">Deep Scan</option>
            </select>
        </div>
        <button type="submit" class="btn btn-primary" style="align-self: flex-end;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
            </svg>
            Start Scan
        </button>
    </form>
</div>

<div id="resultsArea"></div>

<script>
async function startScan(e) {
    e.preventDefault();
    const form = e.target;
    const overlay = document.getElementById('loadingOverlay');
    const text = document.getElementById('loadingText');
    const results = document.getElementById('resultsArea');
    overlay.classList.add('active');
    results.innerHTML = '';
    const steps = [
        'Resolving target...', 'Checking SSL/TLS configuration...', 'Analyzing security headers...',
        'Testing for injection vulnerabilities...', 'Scanning for broken authentication...',
        'Checking sensitive data exposure...', 'Testing access controls...',
        'Scanning for XSS vulnerabilities...', 'Checking security misconfigurations...',
        'Analyzing API endpoints...', 'Generating report...'
    ];
    let step = 0;
    const interval = setInterval(() => {
        if (step < steps.length) { text.textContent = steps[step]; step++; }
    }, 800);
    try {
        const formData = new FormData(form);
        const response = await fetch('/scan', { method: 'POST', body: formData });
        const data = await response.text();
        results.innerHTML = data;
    } catch (err) {
        results.innerHTML = '<div class="scan-section"><p style="color:var(--danger);font-weight:600;">Scan failed: ' + err.message + '</p></div>';
    } finally {
        clearInterval(interval);
        overlay.classList.remove('active');
    }
}
</script>
"""

API_TESTER_PAGE = """
<div class="disclaimer">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
    <span><strong>Important:</strong> Only test APIs you own or have explicit authorization to test.</span>
</div>

<div class="scan-section">
    <h1 class="scan-title">API Security Tester</h1>
    <p class="scan-subtitle">Test REST API endpoints for security vulnerabilities with customizable payloads.</p>
    <form id="apiForm" onsubmit="testApi(event)">
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
            <div class="input-group">
                <label>API Endpoint</label>
                <input type="url" name="endpoint" placeholder="https://api.example.com/users" required>
            </div>
            <div class="input-group">
                <label>HTTP Method</label>
                <select name="method">
                    <option value="GET">GET</option>
                    <option value="POST">POST</option>
                    <option value="PUT">PUT</option>
                    <option value="DELETE">DELETE</option>
                    <option value="PATCH">PATCH</option>
                </select>
            </div>
            <div class="input-group">
                <label>Content-Type</label>
                <select name="content_type">
                    <option value="application/json">application/json</option>
                    <option value="application/x-www-form-urlencoded">x-www-form-urlencoded</option>
                    <option value="text/xml">text/xml</option>
                    <option value="multipart/form-data">multipart/form-data</option>
                </select>
            </div>
        </div>
        <div class="tab-bar">
            <button type="button" class="tab-btn active" onclick="switchTab('headers')">Headers</button>
            <button type="button" class="tab-btn" onclick="switchTab('body')">Body / Payload</button>
            <button type="button" class="tab-btn" onclick="switchTab('auth')">Authentication</button>
            <button type="button" class="tab-btn" onclick="switchTab('security')">Security Tests</button>
        </div>
        <div id="content-headers" class="tab-content active">
            <div class="input-group">
                <label>Custom Headers (JSON format)</label>
                <textarea name="headers" rows="6" class="code-block" style="background:#f9fafb;color:#374151;" placeholder='{"Authorization": "Bearer token", "X-API-Key": "key123"}'></textarea>
            </div>
        </div>
        <div id="content-body" class="tab-content">
            <div class="input-group">
                <label>Request Body</label>
                <textarea name="body" rows="8" class="code-block" style="background:#f9fafb;color:#374151;" placeholder='{"username": "test", "password": "test123"}'></textarea>
            </div>
        </div>
        <div id="content-auth" class="tab-content">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="input-group">
                    <label>Auth Type</label>
                    <select name="auth_type">
                        <option value="none">None</option>
                        <option value="bearer">Bearer Token</option>
                        <option value="basic">Basic Auth</option>
                        <option value="apikey">API Key</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>Auth Value</label>
                    <input type="text" name="auth_value" placeholder="token or credentials">
                </div>
            </div>
        </div>
        <div id="content-security" class="tab-content">
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;">
                    <input type="checkbox" name="test_sqli" checked> Test SQL Injection
                </label>
                <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;">
                    <input type="checkbox" name="test_nosqli" checked> Test NoSQL Injection
                </label>
                <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;">
                    <input type="checkbox" name="test_xss" checked> Test XSS Payloads
                </label>
                <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;">
                    <input type="checkbox" name="test_xxe" checked> Test XXE
                </label>
                <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;">
                    <input type="checkbox" name="test_cmdi" checked> Test Command Injection
                </label>
                <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;">
                    <input type="checkbox" name="test_traversal" checked> Test Path Traversal
                </label>
            </div>
        </div>
        <div style="margin-top: 1.5rem;">
            <button type="submit" class="btn btn-primary">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                </svg>
                Send & Test Security
            </button>
        </div>
    </form>
</div>

<div id="apiResults"></div>

<script>
async function testApi(e) {
    e.preventDefault();
    const overlay = document.getElementById('loadingOverlay');
    const text = document.getElementById('loadingText');
    const results = document.getElementById('apiResults');
    overlay.classList.add('active');
    text.textContent = 'Testing API endpoint...';
    try {
        const form = e.target;
        const formData = new FormData(form);
        const response = await fetch('/api-test', { method: 'POST', body: formData });
        const data = await response.text();
        results.innerHTML = data;
    } catch (err) {
        results.innerHTML = '<div class="scan-section"><p style="color:var(--danger);">Error: ' + err.message + '</p></div>';
    } finally {
        overlay.classList.remove('active');
    }
}
</script>
"""

OWASP_GUIDE_PAGE = """
<div class="scan-section">
    <h1 class="scan-title">OWASP Top 10 (2021) Reference</h1>
    <p class="scan-subtitle">Comprehensive guide to the most critical web application security risks.</p>
</div>
<div class="cards-grid">
    <div class="card">
        <div class="card-header">
            <div class="card-icon critical">A01</div>
            <div class="card-title">Broken Access Control</div>
        </div>
        <div class="card-desc">Restrictions on authenticated users are not properly enforced. Attackers can access unauthorized functionality or data.</div>
    </div>
    <div class="card">
        <div class="card-header">
            <div class="card-icon critical">A02</div>
            <div class="card-title">Cryptographic Failures</div>
        </div>
        <div class="card-desc">Sensitive data is not properly protected with encryption, leading to exposure of passwords, credit cards, health records, etc.</div>
    </div>
    <div class="card">
        <div class="card-header">
            <div class="card-icon critical">A03</div>
            <div class="card-title">Injection</div>
        </div>
        <div class="card-desc">Untrusted data is sent to an interpreter as part of a command or query. SQL, NoSQL, OS command, and LDAP injection attacks.</div>
    </div>
    <div class="card">
        <div class="card-header">
            <div class="card-icon high">A04</div>
            <div class="card-title">Insecure Design</div>
        </div>
        <div class="card-desc">Missing or ineffective security controls due to flawed design patterns and architecture decisions.</div>
    </div>
    <div class="card">
        <div class="card-header">
            <div class="card-icon high">A05</div>
            <div class="card-title">Security Misconfiguration</div>
        </div>
        <div class="card-desc">Improperly configured permissions, default accounts, unnecessary features, error messages with sensitive info.</div>
    </div>
    <div class="card">
        <div class="card-header">
            <div class="card-icon high">A06</div>
            <div class="card-title">Vulnerable Components</div>
        </div>
        <div class="card-desc">Using components with known vulnerabilities (libraries, frameworks, software modules) without proper patching.</div>
    </div>
    <div class="card">
        <div class="card-header">
            <div class="card-icon medium">A07</div>
            <div class="card-title">Auth Failures</div>
        </div>
        <div class="card-desc">Authentication weaknesses allowing credential stuffing, brute force, weak password policies, session hijacking.</div>
    </div>
    <div class="card">
        <div class="card-header">
            <div class="card-icon medium">A08</div>
            <div class="card-title">Data Integrity Failures</div>
        </div>
        <div class="card-desc">Software updates, critical data, and CI/CD pipelines without verification of integrity (deserialization, SSRF).</div>
    </div>
    <div class="card">
        <div class="card-header">
            <div class="card-icon medium">A09</div>
            <div class="card-title">Logging Failures</div>
        </div>
        <div class="card-desc">Insufficient logging and monitoring, plus missing incident response, allows attackers to maintain persistence.</div>
    </div>
    <div class="card">
        <div class="card-header">
            <div class="card-icon low">A10</div>
            <div class="card-title">SSRF</div>
        </div>
        <div class="card-desc">Server-Side Request Forgery allows attackers to induce the server to make requests to unintended locations.</div>
    </div>
</div>
"""

# ==================== ENHANCED SCANNER ENGINE WITH REPRO STEPS ====================

class SecurityScanner:
    def __init__(self, target_url, depth='standard'):
        self.target_url = target_url.rstrip('/')
        self.depth = depth
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BlueShield-Security-Scanner/1.0 (Authorized Testing)'
        })

    def run_all_checks(self):
        checks = [
            ("A01 - Broken Access Control", self.check_access_control),
            ("A02 - Cryptographic Failures", self.check_crypto_failures),
            ("A03 - Injection (SQL/NoSQL/Command)", self.check_injection),
            ("A04 - Insecure Design", self.check_insecure_design),
            ("A05 - Security Misconfiguration", self.check_misconfiguration),
            ("A06 - Vulnerable Components", self.check_vulnerable_components),
            ("A07 - Authentication Failures", self.check_authentication),
            ("A08 - Data Integrity Failures", self.check_data_integrity),
            ("A09 - Logging & Monitoring", self.check_logging),
            ("A10 - SSRF", self.check_ssrf),
        ]

        for name, check_func in checks:
            try:
                result = check_func()
                self.results.append({
                    'id': name.split(' - ')[0],
                    'name': name,
                    'severity': result.get('severity', 'info'),
                    'status': result.get('status', 'pending'),
                    'findings': result.get('findings', []),
                    'details': result.get('details', ''),
                    'recommendation': result.get('recommendation', ''),
                    'evidence': result.get('evidence', []),
                    'reproduction_steps': result.get('reproduction_steps', []),
                    'payloads': result.get('payloads', [])
                })
            except Exception as e:
                self.results.append({
                    'id': name.split(' - ')[0],
                    'name': name,
                    'severity': 'info',
                    'status': 'error',
                    'findings': [f'Scan error: {str(e)}'],
                    'details': 'The scanner encountered an error while testing this vulnerability.',
                    'recommendation': 'Verify the target is accessible and try again.',
                    'evidence': [],
                    'reproduction_steps': [],
                    'payloads': []
                })

        return self.results

    def check_access_control(self):
        findings = []
        severity = 'low'
        repro_steps = []
        payloads = []

        try:
            test_paths = [
                '/../', '/../../', '/../../../etc/passwd', '/.git/', '/.env',
                '/config.php', '/admin/', '/api/admin/', '/.htaccess', '/robots.txt',
            ]

            for path in test_paths:
                try:
                    full_url = self.target_url + path
                    resp = self.session.get(full_url, timeout=5, allow_redirects=False)
                    if resp.status_code in [200, 403]:
                        if 'root:' in resp.text or 'daemon:' in resp.text:
                            findings.append(f'Path traversal vulnerability detected: {path}')
                            severity = 'critical'
                            repro_steps.append(f'Navigate to {full_url} in browser or use curl')
                            repro_steps.append('Observe that server returns /etc/passwd contents')
                            payloads.append(full_url)
                        elif '.git' in path and resp.status_code == 200:
                            findings.append(f'Exposed .git directory: {path}')
                            severity = 'critical'
                            repro_steps.append(f'Visit {full_url} in browser')
                            repro_steps.append('Use tool like GitHacker to dump repository: git-dumper ' + full_url + ' ./output')
                            payloads.append(f'curl {full_url}')
                        elif '.env' in path and resp.status_code == 200:
                            findings.append(f'Exposed .env file: {path}')
                            severity = 'critical'
                            repro_steps.append(f'Visit {full_url} in browser or curl')
                            repro_steps.append('Look for DB_PASSWORD, API_KEY, APP_KEY values')
                            payloads.append(f'curl {full_url}')
                        elif 'admin' in path.lower() and resp.status_code == 200:
                            findings.append(f'Potentially exposed admin panel: {path}')
                            severity = max_severity(severity, 'high')
                            repro_steps.append(f'Visit {full_url} without authentication')
                            repro_steps.append('Verify if admin functionality is accessible')
                            payloads.append(full_url)
                except:
                    pass

            # CORS test
            try:
                headers = {'Origin': 'https://evil.com'}
                resp = self.session.get(self.target_url, headers=headers, timeout=5)
                acao = resp.headers.get('Access-Control-Allow-Origin', '')
                acac = resp.headers.get('Access-Control-Allow-Credentials', '')
                if acao == 'https://evil.com' or acao == '*':
                    findings.append(f'CORS misconfigured: Access-Control-Allow-Origin reflects arbitrary origins')
                    severity = max_severity(severity, 'high')
                    repro_steps.append('Create malicious HTML page hosted on attacker domain')
                    repro_steps.append('Send XMLHttpRequest with withCredentials=true to target')
                    repro_steps.append('Observe that browser allows reading authenticated response')
                    cors_payload = f'Origin: https://evil.com\nResponse: Access-Control-Allow-Origin: {acao}\nAccess-Control-Allow-Credentials: {acac}'
                    payloads.append(cors_payload)
            except:
                pass
        except Exception as e:
            findings.append(f'Access control check error: {str(e)}')

        return {
            'severity': severity,
            'status': 'vulnerable' if findings else 'pass',
            'findings': findings if findings else ['No obvious access control issues detected.'],
            'details': 'Broken access control allows attackers to bypass authorization and perform privileged operations.',
            'recommendation': 'Implement proper access controls, deny by default, validate server-side, and avoid exposing sensitive paths.',
            'evidence': findings[:3],
            'reproduction_steps': repro_steps,
            'payloads': payloads
        }

    def check_crypto_failures(self):
        findings = []
        severity = 'low'
        repro_steps = []
        payloads = []

        try:
            parsed = urllib.parse.urlparse(self.target_url)
            hostname = parsed.netloc.split(':')[0]
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)

            if parsed.scheme == 'http':
                findings.append('Site served over HTTP (no TLS encryption)')
                severity = 'critical'
                repro_steps.append('Open browser DevTools > Network tab')
                repro_steps.append('Observe all requests sent over unencrypted HTTP')
                repro_steps.append('Use Wireshark/tcpdump to capture traffic in plaintext')
                payloads.append('Protocol: HTTP (port 80)')
            else:
                try:
                    context = ssl.create_default_context()
                    with socket.create_connection((hostname, port), timeout=5) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            cipher = ssock.cipher()
                            version = ssock.version()
                            if version in ['TLSv1', 'TLSv1.1', 'SSLv3', 'SSLv2']:
                                findings.append(f'Weak TLS version detected: {version}')
                                severity = max_severity(severity, 'high')
                                repro_steps.append(f'Run: openssl s_client -connect {hostname}:{port} -{version.lower().replace("v", "")}')
                                repro_steps.append('Observe successful handshake with deprecated protocol')
                                payloads.append(f'TLS Version: {version}')
                            if 'RC4' in str(cipher) or 'DES' in str(cipher) or 'MD5' in str(cipher):
                                findings.append(f'Weak cipher detected: {cipher[0]}')
                                severity = max_severity(severity, 'high')
                                repro_steps.append(f'Run: nmap --script ssl-enum-ciphers -p {port} {hostname}')
                                repro_steps.append('Review output for weak cipher suites')
                                payloads.append(f'Cipher: {cipher[0]}')
                except Exception as e:
                    findings.append(f'SSL/TLS check failed: {str(e)}')

            try:
                resp = self.session.get(self.target_url, timeout=5)
                patterns = [
                    (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?[^"\'\s]+', 'Hardcoded password detected'),
                    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?[^"\'\s]+', 'API key exposed in response'),
                    (r'(?i)(aws_access_key_id|aws_secret_access_key)\s*[=:]\s*["\']?[^"\'\s]+', 'AWS credentials exposed'),
                    (r'(?i)(private[_-]?key)\s*[=:]\s*["\']?[^"\'\s]+', 'Private key exposed'),
                    (r'[0-9]{16}', 'Potential credit card number pattern'),
                    (r'[0-9]{3}-[0-9]{2}-[0-9]{4}', 'Potential SSN pattern'),
                ]
                for pattern, msg in patterns:
                    match = re.search(pattern, resp.text)
                    if match:
                        findings.append(msg)
                        severity = max_severity(severity, 'critical')
                        repro_steps.append('View page source or intercept response with proxy')
                        repro_steps.append(f'Search for pattern: {pattern}')
                        repro_steps.append('Document exposed sensitive data')
                        payloads.append(f'Exposed: {match.group(0)[:50]}...')
            except:
                pass
        except Exception as e:
            findings.append(f'Cryptographic check error: {str(e)}')

        return {
            'severity': severity,
            'status': 'vulnerable' if findings else 'pass',
            'findings': findings if findings else ['No obvious cryptographic failures detected.'],
            'details': 'Cryptographic failures expose sensitive data due to weak encryption, missing TLS, or hardcoded secrets.',
            'recommendation': 'Enforce HTTPS with TLS 1.2+, use strong ciphers, encrypt sensitive data at rest and in transit.',
            'evidence': findings[:3],
            'reproduction_steps': repro_steps,
            'payloads': payloads
        }

    def check_injection(self):
        findings = []
        severity = 'low'
        repro_steps = []
        payloads = []

        try:
            sqli_payloads = [
                ("' OR '1'='1", "Boolean-based SQLi"),
                ("' OR 1=1--", "Comment-based SQLi"),
                ("1' AND 1=1--", "Conditional SQLi (true)"),
                ("1' AND 1=2--", "Conditional SQLi (false)"),
                ("' UNION SELECT NULL--", "Union-based SQLi"),
                ("'; DROP TABLE users; --", "Stacked query SQLi"),
                ("1 AND 1=1", "Numeric SQLi"),
                ("1 AND 1=2", "Numeric SQLi false"),
            ]
            test_urls = [
                self.target_url + '/?id=1', self.target_url + '/?page=1',
                self.target_url + '/?search=test', self.target_url + '/?user=1',
                self.target_url + '/api/?id=1',
            ]

            for test_url in test_urls:
                try:
                    base_resp = self.session.get(test_url, timeout=5)
                except:
                    continue
                for payload, desc in sqli_payloads[:4]:
                    try:
                        parsed = urllib.parse.urlparse(test_url)
                        params = urllib.parse.parse_qs(parsed.query)
                        if params:
                            key = list(params.keys())[0]
                            new_url = test_url.replace(f"{key}={params[key][0]}", f"{key}={urllib.parse.quote(payload)}")
                            resp = self.session.get(new_url, timeout=5)
                            sql_errors = [
                                'sql syntax', 'mysql_fetch', 'pg_query', 'ora-', 'sqlite3',
                                'sql server', 'odbc', 'jdbc', 'you have an error in your sql syntax',
                                'warning: mysql', 'unclosed quotation mark', 'quoted string not properly terminated',
                            ]
                            for error in sql_errors:
                                if error.lower() in resp.text.lower() and error.lower() not in base_resp.text.lower():
                                    findings.append(f'SQL Injection vulnerability (error-based) in parameter: {key}')
                                    severity = 'critical'
                                    repro_steps.append(f'1. Open {test_url} in browser (baseline)')
                                    repro_steps.append(f'2. Modify {key} parameter to: {payload}')
                                    repro_steps.append(f'3. Send request to: {new_url}')
                                    repro_steps.append('4. Observe SQL error message in response')
                                    payloads.append(f'Parameter: {key}={payload}')
                                    break
                            if self.depth != 'quick' and resp.elapsed.total_seconds() > 5:
                                findings.append(f'Potential time-based SQL Injection in parameter: {key}')
                                severity = max_severity(severity, 'high')
                                repro_steps.append(f'1. Send request with payload: {key}={payload}')
                                repro_steps.append('2. Measure response time (should be > 5 seconds)')
                                repro_steps.append('3. Compare with normal request timing')
                                payloads.append(f'Time-based: {key}={payload}')
                    except:
                        pass

            # Command Injection
            cmd_payloads = [
                (";cat /etc/passwd", "Semicolon command injection"),
                ("|whoami", "Pipe command injection"),
                ("`id`", "Backtick command injection"),
                ("$(id)", "Substitution command injection"),
                (";echo test123", "Echo test"),
            ]
            for test_url in test_urls[:2]:
                for payload, desc in cmd_payloads[:2]:
                    try:
                        parsed = urllib.parse.urlparse(test_url)
                        params = urllib.parse.parse_qs(parsed.query)
                        if params:
                            key = list(params.keys())[0]
                            new_url = test_url.replace(f"{key}={params[key][0]}", f"{key}={urllib.parse.quote(payload)}")
                            resp = self.session.get(new_url, timeout=5)
                            if 'root:' in resp.text or 'daemon:' in resp.text or 'uid=' in resp.text:
                                findings.append(f'Command Injection vulnerability in parameter: {key}')
                                severity = 'critical'
                                repro_steps.append(f'1. Identify parameter: {key}')
                                repro_steps.append(f'2. Send payload: {payload}')
                                repro_steps.append(f'3. Full URL: {new_url}')
                                repro_steps.append('4. Observe command output in response (uid, root, etc.)')
                                payloads.append(f'CMD: {key}={payload}')
                    except:
                        pass

            # LDAP Injection
            ldap_payloads = [
                ("*)(uid=*))(&(uid=*", "LDAP filter bypass"),
                ("*)(|(uid=*", "LDAP OR injection"),
            ]
            for test_url in test_urls[:2]:
                for payload, desc in ldap_payloads:
                    try:
                        parsed = urllib.parse.urlparse(test_url)
                        params = urllib.parse.parse_qs(parsed.query)
                        if params:
                            key = list(params.keys())[0]
                            new_url = test_url.replace(f"{key}={params[key][0]}", f"{key}={urllib.parse.quote(payload)}")
                            resp = self.session.get(new_url, timeout=5)
                            if 'ldap' in resp.text.lower() or 'directory' in resp.text.lower():
                                findings.append(f'Potential LDAP Injection in parameter: {key}')
                                severity = max_severity(severity, 'high')
                                repro_steps.append(f'1. Target parameter: {key}')
                                repro_steps.append(f'2. Inject LDAP filter: {payload}')
                                repro_steps.append('3. Observe LDAP query results or errors')
                                payloads.append(f'LDAP: {key}={payload}')
                    except:
                        pass
        except Exception as e:
            findings.append(f'Injection check error: {str(e)}')

        return {
            'severity': severity,
            'status': 'vulnerable' if findings else 'pass',
            'findings': findings if findings else ['No obvious injection vulnerabilities detected.'],
            'details': 'Injection flaws allow attackers to send hostile data to interpreters, executing unintended commands.',
            'recommendation': 'Use parameterized queries, input validation, ORMs, and escape special characters.',
            'evidence': findings[:3],
            'reproduction_steps': repro_steps,
            'payloads': payloads
        }

    def check_insecure_design(self):
        findings = []
        severity = 'low'
        repro_steps = []
        payloads = []

        try:
            sensitive_endpoints = [
                '/register', '/signup', '/password-reset', '/forgot-password',
                '/reset-password', '/change-password',
            ]
            for endpoint in sensitive_endpoints:
                try:
                    resp = self.session.get(self.target_url + endpoint, timeout=5, allow_redirects=False)
                    if resp.status_code == 200:
                        findings.append(f'Exposed sensitive endpoint: {endpoint}')
                        severity = max_severity(severity, 'medium')
                        repro_steps.append(f'1. Visit {self.target_url}{endpoint}')
                        repro_steps.append('2. Attempt to use functionality without proper auth')
                        repro_steps.append('3. Check for rate limiting or brute force protection')
                        payloads.append(f'GET {self.target_url}{endpoint}')
                except:
                    pass

            idor_patterns = ['/user/1', '/account/1', '/profile/1', '/order/1', '/invoice/1']
            for pattern in idor_patterns:
                try:
                    resp = self.session.get(self.target_url + pattern, timeout=5, allow_redirects=False)
                    if resp.status_code == 200:
                        findings.append(f'Potential IDOR endpoint: {pattern}')
                        severity = max_severity(severity, 'medium')
                        repro_steps.append('1. Authenticate as User A')
                        repro_steps.append(f'2. Access {self.target_url}{pattern}')
                        repro_steps.append('3. Increment ID (1, 2, 3...) to access other users data')
                        repro_steps.append('4. Verify if access control prevents cross-user access')
                        payloads.append(f'GET {self.target_url}/user/{{ID}}')
                except:
                    pass
        except Exception as e:
            findings.append(f'Insecure design check error: {str(e)}')

        return {
            'severity': severity,
            'status': 'vulnerable' if findings else 'pass',
            'findings': findings if findings else ['No obvious insecure design patterns detected.'],
            'details': 'Insecure design refers to missing or ineffective security controls due to flawed design patterns.',
            'recommendation': 'Implement threat modeling, secure design patterns, rate limiting, and business logic validation.',
            'evidence': findings[:3],
            'reproduction_steps': repro_steps,
            'payloads': payloads
        }

    def check_misconfiguration(self):
        findings = []
        severity = 'low'
        repro_steps = []
        payloads = []

        try:
            resp = self.session.get(self.target_url, timeout=5)
            headers = resp.headers

            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
                'X-XSS-Protection': '1; mode=block',
                'Content-Security-Policy': None,
                'Strict-Transport-Security': None,
                'Referrer-Policy': None,
                'Permissions-Policy': None,
            }

            for header, expected in security_headers.items():
                if header not in headers:
                    findings.append(f'Missing security header: {header}')
                    severity = max_severity(severity, 'medium')
                    repro_steps.append(f'1. Run: curl -I {self.target_url}')
                    repro_steps.append(f'2. Look for {header} in response headers')
                    repro_steps.append(f'3. Confirm header is absent')
                    payloads.append(f'Missing: {header}')
                elif expected and headers.get(header) not in (expected if isinstance(expected, list) else [expected]):
                    if header == 'X-Content-Type-Options' and headers.get(header) != 'nosniff':
                        findings.append(f'Weak {header} value: {headers.get(header)}')

            server = headers.get('Server', '')
            if server:
                findings.append(f'Server version disclosed: {server}')
                severity = max_severity(severity, 'low')
                repro_steps.append(f'1. Run: curl -I {self.target_url}')
                repro_steps.append(f'2. Observe Server header: {server}')
                repro_steps.append('3. Search for known vulnerabilities in this version')
                payloads.append(f'Server: {server}')

            x_powered = headers.get('X-Powered-By', '')
            if x_powered:
                findings.append(f'X-Powered-By header exposes technology: {x_powered}')
                repro_steps.append(f'1. Run: curl -I {self.target_url}')
                repro_steps.append(f'2. Observe X-Powered-By: {x_powered}')
                payloads.append(f'X-Powered-By: {x_powered}')

            try:
                error_resp = self.session.get(self.target_url + '/nonexistent-page-12345', timeout=5)
                if any(x in error_resp.text.lower() for x in ['stack trace', 'traceback', 'exception', 'debug', 'server error']):
                    findings.append('Verbose error messages may expose stack traces')
                    severity = max_severity(severity, 'medium')
                    repro_steps.append(f'1. Visit {self.target_url}/nonexistent-page-12345')
                    repro_steps.append('2. Observe full error details in response')
                    repro_steps.append('3. Look for file paths, code snippets, or database info')
                    payloads.append(f'GET {self.target_url}/nonexistent-page-12345')
            except:
                pass

            try:
                options_resp = self.session.options(self.target_url, timeout=5)
                allow = options_resp.headers.get('Allow', '')
                if allow:
                    methods = [m.strip() for m in allow.split(',')]
                    dangerous = ['PUT', 'DELETE', 'TRACE', 'CONNECT', 'PATCH']
                    found = [m for m in dangerous if m in methods]
                    if found:
                        findings.append(f'Dangerous HTTP methods enabled: {", ".join(found)}')
                        severity = max_severity(severity, 'medium')
                        repro_steps.append(f'1. Run: curl -X OPTIONS -I {self.target_url}')
                        repro_steps.append(f'2. Observe Allow header: {allow}')
                        repro_steps.append(f'3. Test each dangerous method: curl -X PUT {self.target_url}')
                        payloads.append(f'Allow: {allow}')
            except:
                pass
        except Exception as e:
            findings.append(f'Misconfiguration check error: {str(e)}')

        return {
            'severity': severity,
            'status': 'vulnerable' if findings else 'pass',
            'findings': findings if findings else ['No major security misconfigurations detected.'],
            'details': 'Security misconfiguration is the most commonly seen vulnerability due to insecure defaults and incomplete configurations.',
            'recommendation': 'Implement secure defaults, remove unnecessary features, and regularly review configurations.',
            'evidence': findings[:3],
            'reproduction_steps': repro_steps,
            'payloads': payloads
        }

    def check_vulnerable_components(self):
        findings = []
        severity = 'low'
        repro_steps = []
        payloads = []

        try:
            resp = self.session.get(self.target_url, timeout=5)
            headers = resp.headers

            tech_signatures = {
                'Apache': [r'Apache/([0-9.]+)', r'Apache'],
                'nginx': [r'nginx/([0-9.]+)', r'nginx'],
                'PHP': [r'PHP/([0-9.]+)', r'\.php'],
                'WordPress': [r'wp-content', r'wordpress'],
                'Drupal': [r'drupal', r'sites/default'],
                'jQuery': [r'jquery[/-]([0-9.]+)', r'jquery'],
                'Bootstrap': [r'bootstrap[/-]([0-9.]+)', r'bootstrap'],
                'React': [r'react[/-]([0-9.]+)', r'react'],
                'Angular': [r'angular[/-]([0-9.]+)', r'angular'],
                'Django': [r'django', r'csrfmiddlewaretoken'],
                'Flask': [r'flask', r'werkzeug'],
                'Express': [r'express', r'x-powered-by'],
                'ASP.NET': [r'asp\.net', r'\.aspx'],
                'IIS': [r'Microsoft-IIS/([0-9.]+)', r'IIS'],
                'Tomcat': [r'Apache-Coyote', r'tomcat'],
            }

            detected = []
            for tech, patterns in tech_signatures.items():
                for pattern in patterns:
                    if re.search(pattern, resp.text, re.I) or re.search(pattern, str(headers), re.I):
                        detected.append(tech)
                        break

            if detected:
                findings.append(f'Detected technologies: {", ".join(set(detected))}')
                findings.append('Ensure all components are updated to latest versions')
                severity = 'medium'
                repro_steps.append('1. Identify all detected technologies and versions')
                repro_steps.append('2. Search CVE database for known vulnerabilities')
                repro_steps.append('3. Use tools: searchsploit, nuclei, or retire.js')
                for tech in set(detected):
                    payloads.append(f'Technology: {tech}')

            vuln_paths = [
                '/wp-login.php', '/phpmyadmin', '/adminer.php', '/_all_dbs',
                '/actuator', '/swagger-ui.html', '/api/swagger-ui.html',
                '/console', '/manager/html',
            ]

            for path in vuln_paths:
                try:
                    resp = self.session.get(self.target_url + path, timeout=5, allow_redirects=False)
                    if resp.status_code == 200:
                        findings.append(f'Potentially vulnerable component exposed: {path}')
                        severity = max_severity(severity, 'high')
                        repro_steps.append(f'1. Visit {self.target_url}{path}')
                        repro_steps.append('2. Check for default credentials')
                        repro_steps.append('3. Review exposed functionality for abuse')
                        payloads.append(f'Exposed: {self.target_url}{path}')
                except:
                    pass
        except Exception as e:
            findings.append(f'Component check error: {str(e)}')

        return {
            'severity': severity,
            'status': 'vulnerable' if findings else 'pass',
            'findings': findings if findings else ['No obviously vulnerable components detected.'],
            'details': 'Applications using components with known vulnerabilities can undermine defenses and enable attacks.',
            'recommendation': 'Maintain an inventory of components, remove unused dependencies, and monitor security advisories.',
            'evidence': findings[:3],
            'reproduction_steps': repro_steps,
            'payloads': payloads
        }

    def check_authentication(self):
        findings = []
        severity = 'low'
        repro_steps = []
        payloads = []

        try:
            login_paths = [
                '/login', '/signin', '/auth', '/authenticate',
                '/wp-login.php', '/admin/login',
            ]

            for path in login_paths:
                try:
                    resp = self.session.get(self.target_url + path, timeout=5, allow_redirects=False)
                    if resp.status_code == 200:
                        findings.append(f'Login endpoint found: {path}')
                        if not any(x in resp.text.lower() for x in ['minimum', 'at least', 'must contain', 'password requirements']):
                            findings.append(f'No visible password policy on {path}')
                            severity = max_severity(severity, 'low')
                        if not any(x in resp.text.lower() for x in ['captcha', 'recaptcha', 'g-recaptcha']):
                            findings.append(f'No CAPTCHA/brute force protection on {path}')
                            severity = max_severity(severity, 'medium')
                            repro_steps.append(f'1. Visit {self.target_url}{path}')
                            repro_steps.append('2. Attempt common passwords: password123, admin123, 123456')
                            repro_steps.append('3. Use tool: hydra or burp intruder for brute force')
                            repro_steps.append('4. Observe if account gets locked or rate limited')
                            payloads.append(f'POST {self.target_url}{path} with username=admin&password=password123')
                        break
                except:
                    pass

            resp = self.session.get(self.target_url, timeout=5)
            parsed = urllib.parse.urlparse(self.target_url)
            cookies = resp.cookies
            for cookie in cookies:
                if not cookie.secure and parsed.scheme == 'https':
                    findings.append(f'Cookie "{cookie.name}" missing Secure flag')
                    severity = max_severity(severity, 'medium')
                    repro_steps.append(f'1. Run: curl -I {self.target_url}')
                    repro_steps.append(f'2. Look for Set-Cookie: {cookie.name}')
                    repro_steps.append('3. Verify Secure flag is absent')
                    payloads.append(f'Set-Cookie: {cookie.name}={cookie.value}; (no Secure flag)')
                if not cookie.has_nonstandard_attr('HttpOnly'):
                    findings.append(f'Cookie "{cookie.name}" missing HttpOnly flag')
                    severity = max_severity(severity, 'medium')
                    repro_steps.append(f'1. Run: curl -I {self.target_url}')
                    repro_steps.append(f'2. Check Set-Cookie for {cookie.name}')
                    repro_steps.append('3. Verify HttpOnly flag is absent')
                    repro_steps.append('4. Test XSS: document.cookie should reveal this cookie')
                    payloads.append(f'Set-Cookie: {cookie.name}={cookie.value}; (no HttpOnly)')
                if not cookie.has_nonstandard_attr('SameSite'):
                    findings.append(f'Cookie "{cookie.name}" missing SameSite attribute')
                    severity = max_severity(severity, 'low')
                    payloads.append(f'Set-Cookie: {cookie.name}={cookie.value}; (no SameSite)')

            if 'password' in self.target_url.lower() or 'pwd' in self.target_url.lower():
                findings.append('Potential password in URL parameter')
                severity = max_severity(severity, 'high')
                repro_steps.append(f'1. Observe URL: {self.target_url}')
                repro_steps.append('2. Check browser history and server access logs')
                repro_steps.append('3. Passwords in URLs are logged by proxies, browsers, and servers')
                payloads.append(f'URL contains password: {self.target_url}')
        except Exception as e:
            findings.append(f'Authentication check error: {str(e)}')

        return {
            'severity': severity,
            'status': 'vulnerable' if findings else 'pass',
            'findings': findings if findings else ['No obvious authentication failures detected.'],
            'details': 'Authentication weaknesses allow credential stuffing, brute force, and session hijacking.',
            'recommendation': 'Implement MFA, strong password policies, brute force protection, and secure session management.',
            'evidence': findings[:3],
            'reproduction_steps': repro_steps,
            'payloads': payloads
        }

    def check_data_integrity(self):
        findings = []
        severity = 'low'
        repro_steps = []
        payloads = []

        try:
            deser_indicators = [
                'java serialized', 'pickle', 'yaml.load', 'unserialize',
                'objectinputstream', 'readobject',
            ]
            resp = self.session.get(self.target_url, timeout=5)
            for indicator in deser_indicators:
                if indicator in resp.text.lower():
                    findings.append(f'Potential deserialization usage: {indicator}')
                    severity = max_severity(severity, 'high')
                    repro_steps.append(f'1. Search source code for: {indicator}')
                    repro_steps.append('2. Identify deserialization entry points')
                    repro_steps.append('3. Craft malicious serialized payload')
                    repro_steps.append('4. Use ysoserial (Java) or pickle (Python) to generate payload')
                    payloads.append(f'Deserialization: {indicator}')

            xml_endpoints = ['/api/xml', '/soap', '/wsdl', '/xmlrpc', '/api/soap']
            for endpoint in xml_endpoints:
                try:
                    resp = self.session.get(self.target_url + endpoint, timeout=5, allow_redirects=False)
                    if resp.status_code == 200:
                        findings.append(f'XML endpoint detected (XXE risk): {endpoint}')
                        severity = max_severity(severity, 'high')
                        repro_steps.append(f'1. Send crafted XML to {self.target_url}{endpoint}')
                        repro_steps.append('2. Include external entity reference to local files')
                        repro_steps.append('3. Observe if file contents are returned in response')
                        xxe_payload = '<?xml version="1.0"?>\n<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>\n<foo>&xxe;</foo>'
                        payloads.append(f'XXE to {endpoint}:\n{xxe_payload}')
                except:
                    pass

            upload_paths = ['/upload', '/fileupload', '/api/upload', '/import']
            for path in upload_paths:
                try:
                    resp = self.session.get(self.target_url + path, timeout=5, allow_redirects=False)
                    if resp.status_code == 200:
                        findings.append(f'File upload endpoint detected: {path}')
                        severity = max_severity(severity, 'medium')
                        repro_steps.append(f'1. Visit {self.target_url}{path}')
                        repro_steps.append('2. Upload file with dangerous extension: .php, .jsp, .aspx')
                        repro_steps.append('3. Try bypassing extension filters: shell.php.jpg, shell.phtml')
                        repro_steps.append('4. Verify if uploaded file is executable')
                        payloads.append(f'Upload to: {self.target_url}{path}')
                except:
                    pass
        except Exception as e:
            findings.append(f'Data integrity check error: {str(e)}')

        return {
            'severity': severity,
            'status': 'vulnerable' if findings else 'pass',
            'findings': findings if findings else ['No obvious data integrity issues detected.'],
            'details': 'Data integrity failures occur when software updates, critical data, and CI/CD pipelines lack integrity verification.',
            'recommendation': 'Use digital signatures, integrity checks, and avoid deserializing untrusted data.',
            'evidence': findings[:3],
            'reproduction_steps': repro_steps,
            'payloads': payloads
        }

    def check_logging(self):
        findings = []
        severity = 'low'
        repro_steps = []
        payloads = []

        try:
            test_paths = ['/nonexistent-trigger-error', '/test\\x00', '/test%00']
            for path in test_paths:
                try:
                    resp = self.session.get(self.target_url + path, timeout=5)
                    if resp.status_code == 404 and 'not found' in resp.text.lower():
                        findings.append('Application returns generic errors - verify logging is in place')
                        severity = max_severity(severity, 'low')
                        repro_steps.append(f'1. Visit {self.target_url}{path}')
                        repro_steps.append('2. Observe generic 404 response')
                        repro_steps.append('3. Check server logs for request recording')
                        repro_steps.append('4. Verify security events are logged with sufficient detail')
                        payloads.append(f'GET {self.target_url}{path}')
                        break
                except:
                    pass

            log_paths = ['/logs', '/log', '/error.log', '/access.log', '/debug.log', '/application.log', '/var/log']
            for path in log_paths:
                try:
                    resp = self.session.get(self.target_url + path, timeout=5, allow_redirects=False)
                    if resp.status_code == 200 and len(resp.text) > 100:
                        findings.append(f'Potentially exposed log file: {path}')
                        severity = max_severity(severity, 'high')
                        repro_steps.append(f'1. Visit {self.target_url}{path}')
                        repro_steps.append('2. Review log contents for sensitive data')
                        repro_steps.append('3. Check for session tokens, passwords, or PII')
                        payloads.append(f'GET {self.target_url}{path}')
                except:
                    pass
        except Exception as e:
            findings.append(f'Logging check error: {str(e)}')

        return {
            'severity': severity,
            'status': 'vulnerable' if findings else 'pass',
            'findings': findings if findings else ['No obvious logging failures detected.'],
            'details': 'Insufficient logging and monitoring allows attackers to maintain persistence and avoid detection.',
            'recommendation': 'Implement comprehensive logging, real-time monitoring, and incident response plans.',
            'evidence': findings[:3],
            'reproduction_steps': repro_steps,
            'payloads': payloads
        }

    def check_ssrf(self):
        findings = []
        severity = 'low'
        repro_steps = []
        payloads = []

        try:
            url_params = [
                '?url=', '?path=', '?dest=', '?redirect=', '?uri=', '?src=', '?endpoint=', '?webhook=',
            ]

            for param in url_params:
                try:
                    test_url = self.target_url + param + 'http://127.0.0.1'
                    resp = self.session.get(test_url, timeout=5, allow_redirects=False)
                    if resp.status_code in [200, 302]:
                        findings.append(f'Potential SSRF parameter: {param}')
                        severity = max_severity(severity, 'high')
                        repro_steps.append(f'1. Identify parameter that accepts URLs: {param}')
                        repro_steps.append('2. Replace value with internal IP: http://127.0.0.1')
                        repro_steps.append('3. Try other internal targets: http://169.254.169.254/ (AWS metadata)')
                        repro_steps.append('4. Use Burp Collaborator or dnslog.cn to confirm outbound requests')
                        payloads.append(f'{param}http://127.0.0.1')
                        payloads.append(f'{param}http://169.254.169.254/latest/meta-data/')
                except:
                    pass

            callback_paths = ['/webhook', '/callback', '/fetch', '/proxy', '/resolve', '/import', '/preview']
            for path in callback_paths:
                try:
                    resp = self.session.get(self.target_url + path, timeout=5, allow_redirects=False)
                    if resp.status_code == 200:
                        findings.append(f'Potential SSRF endpoint: {path}')
                        severity = max_severity(severity, 'medium')
                        repro_steps.append(f'1. Visit {self.target_url}{path}')
                        repro_steps.append('2. Submit URL field with internal address')
                        repro_steps.append('3. Monitor for server-side requests to internal resources')
                        payloads.append(f'POST {self.target_url}{path} with url=http://127.0.0.1')
                except:
                    pass
        except Exception as e:
            findings.append(f'SSRF check error: {str(e)}')

        return {
            'severity': severity,
            'status': 'vulnerable' if findings else 'pass',
            'findings': findings if findings else ['No obvious SSRF vulnerabilities detected.'],
            'details': 'SSRF allows attackers to induce the server-side application to make requests to unintended locations.',
            'recommendation': 'Validate and sanitize all URLs, use allowlists, and disable unnecessary URL schemas.',
            'evidence': findings[:3],
            'reproduction_steps': repro_steps,
            'payloads': payloads
        }


def max_severity(current, new):
    levels = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
    return new if levels.get(new, 0) > levels.get(current, 0) else current

# ==================== API SECURITY TESTER ====================

class APITester:
    def __init__(self, endpoint, method='GET', headers=None, body=None, auth_type='none', auth_value=''):
        self.endpoint = endpoint
        self.method = method.upper()
        self.headers = headers or {}
        self.body = body
        self.auth_type = auth_type
        self.auth_value = auth_value
        self.results = []

    def set_auth(self):
        if self.auth_type == 'bearer':
            self.headers['Authorization'] = f'Bearer {self.auth_value}'
        elif self.auth_type == 'basic':
            self.headers['Authorization'] = f'Basic {base64.b64encode(self.auth_value.encode()).decode()}'
        elif self.auth_type == 'apikey':
            self.headers['X-API-Key'] = self.auth_value

    def run_security_tests(self, tests_config):
        self.set_auth()

        try:
            base_resp = self._make_request()
        except Exception as e:
            return {'error': f'Base request failed: {str(e)}'}

        results = {
            'base_request': {
                'status': base_resp.status_code,
                'headers': dict(base_resp.headers),
                'body_preview': base_resp.text[:500],
            },
            'security_tests': []
        }

        if tests_config.get('test_sqli', False):
            sqli_payloads = [
                ("' OR '1'='1", "Boolean-based SQLi"),
                ("1' AND 1=1--", "Conditional SQLi"),
                ("; DROP TABLE users; --", "Stacked query"),
                ("1 AND 1=1", "Numeric SQLi"),
            ]
            for payload, desc in sqli_payloads[:2]:
                test_result = self._test_payload(payload, 'SQL Injection', desc)
                if test_result:
                    results['security_tests'].append(test_result)

        if tests_config.get('test_nosqli', False):
            nosql_payloads = [
                ('{"$gt": ""}', "Greater than bypass"),
                ('{"$ne": null}', "Not equal bypass"),
                ('{"$regex": ".*"}', "Regex bypass"),
            ]
            for payload, desc in nosql_payloads[:2]:
                test_result = self._test_payload(payload, 'NoSQL Injection', desc)
                if test_result:
                    results['security_tests'].append(test_result)

        if tests_config.get('test_xss', False):
            xss_payloads = [
                ('<script>alert(1)</script>', "Basic script tag"),
                ('javascript:alert(1)', "JavaScript protocol"),
                ('<img src=x onerror=alert(1)>', "Image onerror"),
            ]
            for payload, desc in xss_payloads[:2]:
                test_result = self._test_payload(payload, 'XSS', desc)
                if test_result:
                    results['security_tests'].append(test_result)

        if tests_config.get('test_xxe', False):
            xxe_payload = '<?xml version="1.0"?>\n<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>\n<foo>&xxe;</foo>'
            test_result = self._test_payload(xxe_payload, 'XXE', 'External entity file read', content_type='application/xml')
            if test_result:
                results['security_tests'].append(test_result)

        if tests_config.get('test_cmdi', False):
            cmd_payloads = [
                (';cat /etc/passwd', "Semicolon injection"),
                ('|whoami', "Pipe injection"),
                ('`id`', "Backtick injection"),
            ]
            for payload, desc in cmd_payloads[:2]:
                test_result = self._test_payload(payload, 'Command Injection', desc)
                if test_result:
                    results['security_tests'].append(test_result)

        if tests_config.get('test_traversal', False):
            traversal_payloads = [
                ('../../../etc/passwd', "Unix traversal"),
                ('..\\..\\..\\windows\\win.ini', "Windows traversal"),
                ('....//....//etc/passwd', "Double dot bypass"),
            ]
            for payload, desc in traversal_payloads[:2]:
                test_result = self._test_payload(payload, 'Path Traversal', desc)
                if test_result:
                    results['security_tests'].append(test_result)

        return results

    def _make_request(self, payload=None, content_type=None):
        headers = dict(self.headers)
        if content_type:
            headers['Content-Type'] = content_type

        url = self.endpoint
        data = self.body

        if payload:
            if data:
                try:
                    json_data = json.loads(data)
                    for key in json_data:
                        if isinstance(json_data[key], str):
                            json_data[key] = payload
                            break
                    data = json.dumps(json_data)
                except:
                    data = data + payload
            else:
                url = f"{url}?test={urllib.parse.quote(payload)}"

        if self.method == 'GET':
            return requests.get(url, headers=headers, timeout=10, allow_redirects=False)
        elif self.method == 'POST':
            return requests.post(url, headers=headers, data=data, timeout=10, allow_redirects=False)
        elif self.method == 'PUT':
            return requests.put(url, headers=headers, data=data, timeout=10, allow_redirects=False)
        elif self.method == 'DELETE':
            return requests.delete(url, headers=headers, timeout=10, allow_redirects=False)
        elif self.method == 'PATCH':
            return requests.patch(url, headers=headers, data=data, timeout=10, allow_redirects=False)
        else:
            return requests.request(self.method, url, headers=headers, data=data, timeout=10, allow_redirects=False)

    def _test_payload(self, payload, test_name, test_desc, content_type=None):
        try:
            resp = self._make_request(payload, content_type)

            indicators = {
                'SQL Injection': ['sql syntax', 'mysql_fetch', 'pg_query', 'ora-', 'sqlite3', 'unclosed quotation'],
                'NoSQL Injection': ['$where', 'MongoError', 'invalid operator'],
                'XSS': ['<script>', 'alert(1)', 'onerror'],
                'XXE': ['root:', 'daemon:', 'etc/passwd', 'bin/bash'],
                'Command Injection': ['root:', 'uid=', 'daemon:', 'windows'],
                'Path Traversal': ['root:', 'daemon:', '[extensions]', 'for 16-bit app support'],
            }

            found_indicators = []
            for indicator in indicators.get(test_name, []):
                if indicator.lower() in resp.text.lower():
                    found_indicators.append(indicator)

            if found_indicators:
                return {
                    'test_name': test_name,
                    'test_desc': test_desc,
                    'payload': payload,
                    'status_code': resp.status_code,
                    'vulnerable': True,
                    'indicators': found_indicators,
                    'response_preview': resp.text[:300],
                    'repro_steps': [
                        f'1. Send {self.method} request to {self.endpoint}',
                        f'2. Include payload in request body/parameter: {payload}',
                        '3. Observe response for vulnerability indicators',
                        f'4. Status code: {resp.status_code}'
                    ],
                    'curl_cmd': self._build_curl(payload, content_type)
                }

            error_patterns = ['error', 'exception', 'traceback', 'stack trace', 'syntax']
            if any(p in resp.text.lower() for p in error_patterns) and resp.status_code >= 400:
                return {
                    'test_name': test_name,
                    'test_desc': test_desc,
                    'payload': payload,
                    'status_code': resp.status_code,
                    'vulnerable': 'possible',
                    'indicators': ['Error response triggered'],
                    'response_preview': resp.text[:300],
                    'repro_steps': [
                        f'1. Send {self.method} request to {self.endpoint}',
                        f'2. Include payload: {payload}',
                        '3. Application returned error - may indicate vulnerability',
                        f'4. Status code: {resp.status_code}'
                    ],
                    'curl_cmd': self._build_curl(payload, content_type)
                }

            return {
                'test_name': test_name,
                'test_desc': test_desc,
                'payload': payload,
                'status_code': resp.status_code,
                'vulnerable': False,
                'indicators': [],
                'response_preview': resp.text[:200],
                'repro_steps': [],
                'curl_cmd': ''
            }

        except Exception as e:
            return {
                'test_name': test_name,
                'test_desc': test_desc,
                'payload': payload,
                'error': str(e),
                'vulnerable': False,
                'repro_steps': [],
                'curl_cmd': ''
            }

    def _build_curl(self, payload, content_type=None):
        ct = content_type or 'application/json'
        curl = f"curl -X {self.method} '{self.endpoint}'"

        for key, val in self.headers.items():
            curl += f" -H '{key}: {val}'"

        if content_type:
            curl += f" -H 'Content-Type: {content_type}'"

        if self.body:
            try:
                json_data = json.loads(self.body)
                for key in json_data:
                    if isinstance(json_data[key], str):
                        json_data[key] = payload
                        break
                curl += f" -d '{json.dumps(json_data)}'"
            except:
                curl += f" -d '{self.body}{payload}'"
        else:
            curl += f" -d '{payload}'"

        return curl

# ==================== FLASK ROUTES ====================

def build_repro_section(repro_steps, payloads):
    html = ''
    if repro_steps or payloads:
        html += '<div class="vuln-section">'
        html += '<h4>How to Reproduce</h4>'
        html += '<div class="repro-box">'
        html += '<h5><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> Step-by-Step Reproduction</h5>'
        html += '<ol class="step-list">'
        for i, step in enumerate(repro_steps, 1):
            html += f'<li><span class="step-num">{i}</span><span class="step-text">{step}</span></li>'
        html += '</ol>'
        html += '</div>'

        if payloads:
            html += '<div style="margin-top:1rem;">'
            html += '<h5 style="color:var(--dark-red);font-size:0.875rem;margin-bottom:0.75rem;display:flex;align-items:center;gap:0.5rem;">'
            html += '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>'
            html += 'Payloads & Commands</h5>'
            for payload in payloads:
                html += f'<div class="curl-box" style="margin-bottom:0.5rem;">{payload}</div>'
            html += '</div>'

        html += '</div>'
    return html


@app.route('/')
def index():
    return render_template_string(BASE_TEMPLATE, content=SCANNER_PAGE)

@app.route('/api-tester')
def api_tester():
    return render_template_string(BASE_TEMPLATE, content=API_TESTER_PAGE)

@app.route('/owasp-guide')
def owasp_guide():
    return render_template_string(BASE_TEMPLATE, content=OWASP_GUIDE_PAGE)

@app.route('/scan', methods=['POST'])
def scan():
    target_url = request.form.get('target_url', '')
    scan_depth = request.form.get('scan_depth', 'standard')

    if not target_url.startswith(('http://', 'https://')):
        return '<div class="scan-section"><p style="color:var(--danger);font-weight:600;">Invalid URL. Must start with http:// or https://</p></div>'

    scanner = SecurityScanner(target_url, scan_depth)
    results = scanner.run_all_checks()

    stats = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'pass': 0}
    for r in results:
        if r['status'] == 'pass':
            stats['pass'] += 1
        else:
            stats[r['severity']] += 1

    html = '<div class="stats-row">'
    html += f'<div class="stat-box"><div class="stat-number critical">{stats["critical"]}</div><div class="stat-label">Critical</div></div>'
    html += f'<div class="stat-box"><div class="stat-number high">{stats["high"]}</div><div class="stat-label">High</div></div>'
    html += f'<div class="stat-box"><div class="stat-number medium">{stats["medium"]}</div><div class="stat-label">Medium</div></div>'
    html += f'<div class="stat-box"><div class="stat-number low">{stats["low"] + stats["pass"]}</div><div class="stat-label">Low / Pass</div></div>'
    html += '</div>'

    risk_badge = 'critical' if stats['critical'] > 0 else 'high' if stats['high'] > 0 else 'medium' if stats['medium'] > 0 else 'pass'
    risk_text = 'CRITICAL RISK' if stats['critical'] > 0 else 'HIGH RISK' if stats['high'] > 0 else 'MEDIUM RISK' if stats['medium'] > 0 else 'LOW RISK'

    html += '<div class="results-section">'
    html += '<div class="results-header">'
    html += f'<h2 class="results-title">Scan Results for {target_url}</h2>'
    html += f'<span class="badge badge-{risk_badge}">{risk_text}</span>'
    html += '</div>'

    for i, result in enumerate(results):
        severity_class = result['severity'] if result['status'] != 'pass' else 'pass'
        badge_class = result['severity'] if result['status'] != 'pass' else 'pass'
        status_text = 'VULNERABLE' if result['status'] == 'vulnerable' else 'PASS' if result['status'] == 'pass' else 'REVIEW'

        findings_html = '<ul style="margin:0;padding-left:1.2rem;">'
        for finding in result['findings']:
            findings_html += f'<li style="margin-bottom:0.3rem;">{finding}</li>'
        findings_html += '</ul>'

        evidence_html = ''
        if result['evidence']:
            evidence_html = '<div class="vuln-section"><h4>Evidence</h4>'
            for ev in result['evidence']:
                evidence_html += f'<div class="code-block">{ev}</div>'
            evidence_html += '</div>'

        repro_html = build_repro_section(result.get('reproduction_steps', []), result.get('payloads', []))

        html += f'<div class="vuln-item">'
        html += f'<div class="vuln-header {severity_class}" onclick="toggleVuln({i})">'
        html += f'<div><span class="badge badge-{badge_class}">{result["id"]}</span>'
        html += f'<span class="vuln-name" style="margin-left:0.5rem;">{result["name"]}</span></div>'
        html += f'<div class="vuln-meta"><span class="badge badge-{badge_class}">{status_text}</span>'
        html += f'<span class="toggle-icon" id="vuln-icon-{i}">&#9660;</span></div></div>'
        html += f'<div class="vuln-body" id="vuln-body-{i}">'
        html += f'<div class="vuln-section"><h4>Findings</h4>{findings_html}</div>'
        html += f'<div class="vuln-section"><h4>Description</h4><p>{result["details"]}</p></div>'
        html += evidence_html
        html += repro_html
        html += f'<div class="vuln-section"><h4>Recommendation</h4><div class="recommendation">{result["recommendation"]}</div></div>'
        html += '</div></div>'

    html += '</div>'
    return html

@app.route('/api-test', methods=['POST'])
def api_test():
    endpoint = request.form.get('endpoint', '')
    method = request.form.get('method', 'GET')
    headers_str = request.form.get('headers', '{}')
    body = request.form.get('body', '')
    auth_type = request.form.get('auth_type', 'none')
    auth_value = request.form.get('auth_value', '')

    try:
        headers = json.loads(headers_str) if headers_str else {}
    except:
        headers = {}

    tests_config = {
        'test_sqli': request.form.get('test_sqli') == 'on',
        'test_nosqli': request.form.get('test_nosqli') == 'on',
        'test_xss': request.form.get('test_xss') == 'on',
        'test_xxe': request.form.get('test_xxe') == 'on',
        'test_cmdi': request.form.get('test_cmdi') == 'on',
        'test_traversal': request.form.get('test_traversal') == 'on',
    }

    tester = APITester(endpoint, method, headers, body, auth_type, auth_value)
    results = tester.run_security_tests(tests_config)

    if 'error' in results:
        return f'<div class="scan-section"><p style="color:var(--danger);font-weight:600;">{results["error"]}</p></div>'

    base = results['base_request']

    html = '<div class="results-section">'
    html += '<div class="results-header">'
    html += '<h2 class="results-title">API Test Results</h2>'
    has_vuln = any(t.get('vulnerable') for t in results['security_tests'])
    badge = 'critical' if has_vuln else 'pass'
    text = 'VULNERABILITIES FOUND' if has_vuln else 'NO VULNERABILITIES'
    html += f'<span class="badge badge-{badge}">{text}</span>'
    html += '</div>'

    html += '<div class="api-tester">'
    html += '<h4 style="margin-bottom:1rem;">Base Request Response</h4>'
    html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem;">'
    status_badge = 'pass' if base['status'] < 400 else 'high'
    html += f'<div><strong>Status:</strong> <span class="badge badge-{status_badge}">{base["status"]}</span></div>'
    html += f'<div><strong>Content-Type:</strong> {base["headers"].get("Content-Type", "N/A")}</div>'
    html += '</div>'
    html += '<h4 style="font-size:0.875rem;color:var(--text-gray);margin-bottom:0.5rem;">Response Preview</h4>'
    html += f'<div class="code-block">{base["body_preview"]}</div>'
    html += '</div>'

    for test in results['security_tests']:
        if test.get('vulnerable'):
            vuln_status = 'CRITICAL' if test['vulnerable'] == True else 'POSSIBLE'
            badge = 'badge-critical' if test['vulnerable'] == True else 'badge-high'
            test_id = test['test_name'].replace(' ', '_')

            indicators_html = ''.join(f'<li>{ind}</li>' for ind in test.get('indicators', []))

            repro_html = ''
            if test.get('repro_steps'):
                repro_html = '<div class="vuln-section"><h4>How to Reproduce</h4><div class="repro-box"><h5>Step-by-Step</h5><ol class="step-list">'
                for i, step in enumerate(test['repro_steps'], 1):
                    repro_html += f'<li><span class="step-num">{i}</span><span class="step-text">{step}</span></li>'
                repro_html += '</ol></div>'
                if test.get('curl_cmd'):
                    repro_html += f'<div style="margin-top:1rem;"><h5>curl Command</h5><div class="curl-box">{test["curl_cmd"]}</div></div>'
                repro_html += '</div>'

            html += f'<div class="vuln-item">'
            html += f'<div class="vuln-header critical" onclick="toggleVuln(\'{test_id}\')">'
            html += f'<div><span class="badge {badge}">{vuln_status}</span>'
            html += f'<span class="vuln-name" style="margin-left:0.5rem;">{test["test_name"]} ({test.get("test_desc", "")})</span></div>'
            html += f'<span class="toggle-icon" id="vuln-icon-{test_id}">&#9660;</span></div>'
            html += f'<div class="vuln-body" id="vuln-body-{test_id}">'
            html += f'<div class="vuln-section"><h4>Payload Used</h4><div class="code-block">{test["payload"]}</div></div>'
            html += f'<div class="vuln-section"><h4>Indicators Found</h4><ul style="margin:0;padding-left:1.2rem;">{indicators_html}</ul></div>'
            html += f'<div class="vuln-section"><h4>Response Preview</h4><div class="code-block">{test.get("response_preview", "N/A")}</div></div>'
            html += repro_html
            html += '</div></div>'

    if not has_vuln:
        html += '<div class="scan-section" style="text-align:center;padding:3rem;">'
        html += '<div style="font-size:3rem;margin-bottom:1rem;">&#10003;</div>'
        html += '<h3 style="color:var(--success);margin-bottom:0.5rem;">No Vulnerabilities Detected</h3>'
        html += '<p style="color:var(--text-gray);">The tested payloads did not trigger any known vulnerability indicators.</p>'
        html += '</div>'

    html += '</div>'
    return html


if __name__ == '__main__':
    print("=" * 60)
    print("  BlueShield - OWASP Top 10 Security Scanner")
    print("=" * 60)
    print("  Starting server on http://0.0.0.0:5000")
    print("  Press Ctrl+C to stop")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
