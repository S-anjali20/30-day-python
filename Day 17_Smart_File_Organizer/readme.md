# 📂 Day 17 — Smart File Organizer & Duplicate Finder

A modern desktop file management application built with Python and CustomTkinter as part of my 30 Days, 30 Python Projects Challenge.

The **Smart File Organizer** helps users clean up cluttered folders, organize files automatically, identify duplicate files using cryptographic hashing, generate storage reports, and even undo recent operations—all through a clean, responsive desktop interface.

---

## ✨ Features

- 📁 **File Organization:** Organize files by file type, modification date, or custom extensions.
- 👁️ **Move Preview:** Review the planned file movements before applying any changes to your file system.
- 🔍 **Duplicate Finder:** Detect duplicate files accurately using SHA-256 content hashing.
- 📊 **Storage Overview:** View total file counts, storage usage, and category breakdowns.
- 📄 **Storage Reports:** Export detailed storage summaries to CSV format.
- 📋 **Duplicate Reports:** Export lists of detected duplicate files to CSV for further review.
- 📜 **Operation History:** Keep track of past file organization operations in a local configuration log.
- ↩️ **Undo Operations:** Easily restore files from the latest supported move operation.
- 🌙 **Modern GUI:** Interactive, clean dark-themed desktop interface built with CustomTkinter.
- 🛡️ **Safer File Handling:** Explicit confirmation prompts before moving files and built-in protection against overwriting existing files.

---

## 🛠️ Technologies Used

| Technology / Library | Purpose |
| :--- | :--- |
| **Python** | Core programming language |
| **`customtkinter`** | Modern graphical user interface (GUI) framework |
| **`pathlib`** | Object-oriented file and directory path management |
| **`hashlib`** | Generating SHA-256 file hashes for duplicate detection |
| **`json`** | Storing local configuration and operation history |
| **`csv`** | Exporting storage and duplicate file reports |
| **`threading`** | Asynchronous background scanning to keep the UI responsive |
| **`os` & `datetime`** | File system metadata extraction and date formatting |

---

## 📂 Project Structure

```text
Day 17_Smart_File_Organizer/
│
├── main.py
├── requirements.txt
└── README.md
