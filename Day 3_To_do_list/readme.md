# 📝 Day 3 — To-Do Task Manager

A feature-rich, interactive command-line To-Do Task Manager built with Python.

This application allows users to create, view, edit, complete, search, and delete tasks seamlessly. Tasks are automatically saved to a local `tasks.json` file to ensure data persistence across program restarts. For an intuitive terminal experience, it utilizes the **Questionary** library to provide interactive arrow-key navigation menus.

---

## ✨ Features

- ➕ **Add new tasks** with custom priorities
- 📋 **View all tasks** with clear status indicators
- ✅ **Mark tasks as completed**
- ✏️ **Edit existing tasks** (update title or priority)
- ❌ **Delete tasks** with automatic sequential ID re-indexing
- 🔍 **Search tasks** by keywords
- 🚦 **Assign priorities** (High, Medium, Low)
- 💾 **Automatic JSON persistence** (saves changes instantly)
- 📂 **Auto-load saved tasks** upon startup
- 🎯 **Interactive CLI menu** powered by `questionary`
- 🛡️ **Robust input validation** and error handling

---

## 🚦 Task Priorities

Each task can be assigned one of three visual priority levels:

- 🔴 **High**
- 🟡 **Medium**
- 🟢 **Low**

### Example Display:
```text
1. Complete Python project   | 🔴 High   | ⏳ Pending
2. Upload project to GitHub  | 🟡 Medium | ✅ Completed
3. Read Python documentation | 🟢 Low    | ⏳ Pending 
```
---

## 📸 Demo
<img width="1106" height="552" alt="Screenshot 2026-10-04 at 9 54 48 AM" src="https://github.com/user-attachments/assets/080ed9fc-cd85-475c-9360-23932cf67f80" />


