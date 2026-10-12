# 🧮 Day 2 — Smart Calculator

A feature-rich command-line calculator built with Python.

This project started as a basic calculator and was enhanced with scientific operations, live currency conversion, API integration, and a beautiful terminal interface using **Rich**.

---

## ✨ Features

### 🧮 Basic Calculator
- ➕ Addition
- ➖ Subtraction
- ✖️ Multiplication
- ➗ Division
- `%` Modulus
- `**` Power
- 🛡️ Division-by-zero handling

### 🔬 Scientific Operations
- `√` Square Root
- Percentage calculation
- Negative number validation for square root operations

### 💱 Live Currency Converter
- Fetches supported currencies directly from the **Frankfurter API**
- Select currency easily using a numbered menu
- Interactive selection for **FROM** and **TO** currencies
- Input conversion amount dynamically
- Fetches real-time exchange rates and displays:
  - Original amount
  - Current exchange rate
  - Converted total
  - Rate timestamp/date
- Handles API connection errors and invalid selections gracefully

### 🎨 Rich Terminal Interface
Uses the `rich` library to deliver a polished CLI experience:
- 📋 Interactive formatted tables
- 📦 Styled visual panels

---

## 🛠️ Technologies & Libraries

| Technology / Library | Purpose |
| :--- | :--- |
| **Python** | Main programming language |
| **`math`** | Square root and scientific math operations |
| **`requests`** | Performing HTTP API requests |
| **`rich`** | Advanced terminal UI formatting |
| **Frankfurter API** | Real-time currency exchange rates |

---

## 📚 Concepts Learned

Through this project, I practiced:
- Function creation, parameters, and return values
- Exception handling using `try`/`except`
- Working with REST APIs, parsing JSON responses, and HTTP requests
- Robust user input validation
- Integrating external Python libraries
- Terminal user interface design

---
## Demo
<img width="970" height="529" alt="Screenshot 2026-10-02 at 9 28 08 PM" src="https://github.com/user-attachments/assets/0d9d0415-dfa4-431a-bd63-7c9740b77e4b" />
<img width="944" height="684" alt="Screenshot 2026-10-02 at 9 28 39 PM" src="https://github.com/user-attachments/assets/753348ab-b466-49a2-b015-d56da22d42cd" />
