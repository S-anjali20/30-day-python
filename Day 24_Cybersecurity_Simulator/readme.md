# 🛡️ Day 24 — CyberOps: Cybersecurity Simulator

A desktop cybersecurity training simulator built with Python and CustomTkinter as part of my **30 Days, 30 Python Projects Challenge**.

**CyberOps** provides a Security Operations Center (SOC)-inspired desktop interface where users can explore fictional security logs, identify suspicious login patterns, investigate simulated incidents, and maintain a persistent record of resolved cases.

---

## ✨ Features

- 📊 **Security Overview:** View event counts, open incidents, priority alerts, and resolved cases at a glance.
- 🔎 **Event Log Explorer:** Search and filter security events by severity (`INFO`, `WARN`, `ERROR`), source, or message contents.
- 🧠 **Basic Threat Detection:** Identify repeated failed-login attempts using Python regular expressions (`re`).
- 🔬 **Incident Investigation Lab:** Review detailed incident descriptions, severity levels, evidence, and suggested response steps.
- ✅ **Response Checklists:** Follow structured remediation checklists while investigating simulated incidents.
- 💾 **Case History Tracking:** Save and review resolved incident logs in a local SQLite database.
- 📄 **CSV Export:** Export simulated event logs for offline analysis or documentation.
- 🌙 **Modern SOC Dashboard GUI:** Navigate a dark-themed desktop interface inspired by security monitoring consoles.

---

## 🛠️ Tech Stack

| Technology / Library | Purpose |
| :--- | :--- |
| **Python** | Core application logic and log processing |
| **`customtkinter`** | Modern dark-themed graphical user interface (GUI) framework |
| **`sqlite3`** | Local relational database for tracking case resolutions |
| **`re` (Regular Expressions)** | Pattern matching to detect repeated failed-login attempts |
| **`csv`** | Exporting structured event log records |
| **`tkinter`** | Native file save dialogs and message alerts |

---

##Demo
<img width="1145" height="791" alt="Screenshot 2026-10-26 at 10 55 54 PM" src="https://github.com/user-attachments/assets/9aee9af6-3962-466a-8621-66a4ab594a4d" />

