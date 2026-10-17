# 💸 Day 16 — PennyWise: Smart Expense & Budget Manager

A desktop finance tracker built with Python as part of my **30 Days, 30 Python Projects Challenge**. 🚀

**PennyWise** helps users manage their personal finances by tracking income and expenses, setting monthly budgets, visualizing spending patterns, and exporting transaction records to CSV.

## ✨ Features

- 💰 **Income & Expense Tracking** — Record income and expenses easily.
- 🏷️ **Transaction Categories** — Organize transactions with categories, dates, and optional notes.
- 📊 **Monthly Financial Summary** — View total income, expenses, and net balance.
- 🎯 **Budget Management** — Set a monthly budget and monitor spending with visual progress.
- 🍩 **Spending Visualization** — Explore category-wise expenses using a donut chart.
- 🔍 **Transaction Filtering** — Filter transactions by type.
- 🗑️ **Delete Transactions** — Remove selected transaction records.
- 📄 **CSV Export** — Export transaction history for further analysis.
- 💾 **SQLite Database** — Store financial records locally and retain them between sessions.
- 🌙 **Modern Dark UI** — A desktop interface built with CustomTkinter.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| CustomTkinter | Modern desktop GUI |
| SQLite | Local database storage |
| Matplotlib | Spending charts and visualization |
| Tkinter | GUI utilities and dialogs |


## 💾 Data Storage & Privacy

PennyWise stores transaction records locally in an SQLite database named `expenses.db`.

- No bank account connection is required.
- Financial records are not uploaded to a remote server by the application.
- Data persists locally between application sessions.

**Note:** The displayed net balance is calculated as recorded income minus recorded expenses for the selected month. It is not a verified bank balance.

## 🎓 What I Learned

Building PennyWise helped me gain practical experience with:

- SQLite database operations and CRUD functionality
- SQL aggregation for financial summaries
- Input validation and transaction handling
- CSV file generation and data export
- Embedding Matplotlib charts in a desktop GUI
- Event-driven programming with Python GUI libraries
- Organizing data for a real-world personal finance application

## 🔮 Future Improvements

- 📅 Month selector and date-range filters
- 🎯 Category-specific budgets
- 🔁 Recurring transactions
- ✏️ Search and edit existing transactions
- 📈 Weekly and yearly spending analytics
- 🧪 Automated testing
- 📊 Budget comparison and spending trend reports

##Demo
<img width="1178" height="808" alt="Screenshot 2026-10-17 at 7 59 14 PM" src="https://github.com/user-attachments/assets/826d08e3-b7a3-439b-a594-9891bda59d23" />


