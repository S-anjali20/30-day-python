# 🚀 Day 21 — CryptoPulse: Real-Time Crypto Tracker & Price Alerts

A desktop cryptocurrency tracking application built with Python and CustomTkinter as part of my **30 Days, 30 Python Projects Challenge**.

**CryptoPulse** fetches real-time cryptocurrency prices from the CoinGecko API, lets users create custom threshold-based price alerts, sends desktop notifications when targets are met, and logs historical price checks locally in an SQLite database.

---

## ✨ Features

- 📈 **Live Cryptocurrency Prices:** Fetch current USD prices and 24-hour percentage price changes in real time.
- 📌 **Custom Watchlist:** Dynamically add and remove cryptocurrencies from your main dashboard.
- 🔔 **Price Alerts:** Set threshold triggers when a cryptocurrency rises above or falls below a targeted price.
- 💬 **Desktop Notifications:** Receive native OS notifications via `plyer` when alert targets are hit.
- ⏱️ **Automatic Refresh:** Configure customized automated price polling intervals.
- 💾 **Price History Logging:** Persistently store historical price checks in a local SQLite database.
- 📊 **Interactive Charts:** Visualize stored price trends over time using embedded Matplotlib charts.
- ⚙️ **Alert Management:** Pause, resume, and delete configured alerts effortlessly.
- 🌙 **Modern Dark Dashboard:** Dark-themed responsive desktop interface built with CustomTkinter.
- 🔒 **Local Storage:** All alerts and price records remain strictly on your local machine.

---

## 🛠️ Tech Stack

| Technology / Library | Purpose |
| :--- | :--- |
| **Python** | Core application logic |
| **`customtkinter`** | Modern desktop graphical user interface (GUI) |
| **`requests`** | HTTP communication with REST APIs |
| **CoinGecko API** | Real-time cryptocurrency market data provider |
| **`plyer`** | Cross-platform desktop notifications |
| **`sqlite3`** | Local database for storing alerts and price history logs |
| **`matplotlib`** | Rendering price trend charts |
| **`threading`** | Asynchronous API polling to keep the UI completely smooth |

---

## Demo
<img width="1177" height="809" alt="Screenshot 2026-10-22 at 7 07 58 PM" src="https://github.com/user-attachments/assets/f7f99514-3e89-49cf-a90d-e142d4a54edc" />
