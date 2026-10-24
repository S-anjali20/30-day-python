# ✈️ Day 22 — SkyTrack: Real-Time Flight Tracker

A desktop-based flight tracking application built with Python that displays live aircraft data from the OpenSky Network on an interactive map.

**SkyTrack** allows users to track aircraft worldwide or explore specific regions through a modern desktop dashboard built with CustomTkinter and interactive Folium maps.

This project is **Day 22** of my **30 Days, 30 Python Projects Challenge**, where I build practical applications to strengthen my Python development, API integration, GUI programming, and problem-solving skills.

---

## ✨ Features

- 🌍 **Worldwide Flight Tracking:** Request available aircraft state vector data globally.
- 🗺️ **Interactive Flight Map:** View aircraft positions, click interactive markers, and explore flight details inside your web browser.
- 🌐 **Regional Filters:** Quickly filter coverage between Europe, North America, India & nearby regions, East Asia, or the complete Global dataset.
- 🔎 **Aircraft Search:** Search in real time by callsign, ICAO24 identifier, or country of origin.
- 📊 **Live Dashboard:** View aggregate aircraft counts, active search matches, and airborne aircraft metrics at a glance.
- ✈️ **Aircraft Details:** Inspect altitude, velocity/speed, heading, vertical rate, exact coordinates, and squawk codes.
- 🔄 **Automatic Refresh:** Configure automated polling intervals (30s, 60s, 120s, or 300s).
- 🎯 **Aircraft Selection:** Select any aircraft from the list to view detailed telemetry and center the map on its exact location.
- 🌙 **Dark Desktop Interface:** A clean, responsive dashboard built with CustomTkinter.

---

## 🛠️ Tech Stack

| Technology / Library | Purpose |
| :--- | :--- |
| **Python** | Core application logic |
| **`customtkinter`** | Modern desktop graphical user interface (GUI) |
| **`folium`** | Interactive HTML map rendering |
| **`requests`** | HTTP communication with REST APIs |
| **OpenSky Network REST API** | Real-time aircraft state vector data provider |
| **`threading`** | Asynchronous API requests to keep the UI completely smooth |
| **`webbrowser`** | Rendering generated HTML maps in native browsers |

---

##Demo
<img width="1512" height="758" alt="Screenshot 2026-10-24 at 10 33 20 AM" src="https://github.com/user-attachments/assets/ce86b8e0-34bd-4dd9-b012-813d2d78ab8d" />
<img width="1209" height="820" alt="Screenshot 2026-10-24 at 10 34 06 AM" src="https://github.com/user-attachments/assets/f2d0a252-aee7-4b18-8a41-50d99300fc92" />
