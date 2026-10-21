# 🛡️ Day 20 — CyberShield: Cybersecurity Learning Simulator

A Python-based desktop application designed to explore fundamental cybersecurity concepts through interactive tools. 

**CyberShield** combines password strength analysis, suspicious URL inspection, file integrity monitoring, and simulated security event logging into a modern dark-themed graphical dashboard.

This project is **Day 20** of my **30 Days, 30 Python Projects Challenge**, where I build practical applications to strengthen my software engineering and problem-solving skills.

---

## ✨ Features

### 🔐 1. Password Strength Analyzer
- **Entropy & Complexity Analysis:** Evaluates password length, character variety (uppercase, lowercase, numbers, symbols), and structural patterns.
- **Pattern Detection:** Flags common weak patterns, sequential strings, and repetitive sequences.
- **Visual Strength Indicator:** Real-time feedback with a dynamic progress bar and color-coded rating.
- **Security Recommendations:** Specific, actionable tips to increase password complexity.
- **Zero-Knowledge Architecture:** Performs all evaluations locally without sending sensitive credentials across any network.

### 🔎 2. Suspicious URL Checker
- **Static Analysis:** Inspects URL structure safely without opening or visiting the web link.
- **Heuristic Pattern Detection:** Identifies risky structural signals, including:
  - Raw IP addresses used as hostnames
  - Excessively long hostnames or path strings
  - Multiple nested subdomain levels
  - User credentials or `@` symbols in URLs
  - Punycode hostnames (`xn--`) and obfuscated strings
  - Unencrypted HTTP connections
- **Risk Score Breakdown:** Generates a heuristic risk score alongside detailed rule findings.

> **Note:** This is a rule-based educational checker, not a live phishing detection service. A low risk score does not guarantee that a URL is safe.

### 📁 3. File Integrity Monitor
- **Hash Generation:** Computes SHA-256 cryptographic hashes for chosen local files.
- **Baseline Management:** Save known-good file hash baselines locally.
- **Integrity Verification:** Compare active file contents against saved baselines to instantly detect unauthorized modifications or file corruption.

---

## 🛠️ Technologies Used

| Technology / Library | Purpose |
| :--- | :--- |
| **Python** | Core programming language |
| **`customtkinter`** | Modern, dark-themed graphical user interface (GUI) framework |
| **`hashlib`** | Cryptographic hash functions (SHA-256) for file integrity validation |
| **`urllib.parse`** | Safe URL decomposition and structural parsing |
| **`re`** | Regular expressions for pattern detection and rule matching |
| **`json`** | Storing baseline hash records and configuration data locally |

---

## Demo
<img width="1176" height="786" alt="Screenshot 2026-10-21 at 8 12 02 PM" src="https://github.com/user-attachments/assets/e01846c0-ce4e-4c81-baf3-3d061d178246" />
