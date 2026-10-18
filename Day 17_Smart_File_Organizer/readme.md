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

## 🔐 Safety and Privacy

- **Review Previews:** Always inspect the move preview before executing folder organization.
- **Test Safely:** Test operations on a sample folder prior to processing critical data.
- **Maintain Backups:** Keep external backups of essential files.
- **No Auto-Deletion:** Duplicate detection identifies matching content; it does not automatically delete files.
- **Single Threading:** Avoid running concurrent organization operations on the same directory.
- **Undo Dependencies:** Undo features rely on operation logs and require files to remain in their moved paths.
- **Local Processing:** All file operations run locally on your device with zero remote server uploads.

> **Important:** SHA-256 hash matching accurately identifies identical content, but batch file operations should always be reviewed before confirming.

---

## 📚 What I Learned

Building this project provided hands-on experience with:
- Managing file systems and paths via `pathlib`
- Computing file content hashes using `hashlib` (SHA-256)
- Grouping duplicate files based on content analysis
- Constructing desktop interfaces with CustomTkinter
- Handling file collisions and avoiding overwrite conflicts
- Executing non-blocking background scans using `threading`
- Generating structured data exports in CSV format
- Persisting operation logs using JSON serialization
- Implementing undo state management for file system actions

---

## 🚀 Future Improvements

- 🖼️ **Duplicate Review Screen:** Add visual side-by-side file previews and metadata comparisons.
- ⏰ **Scheduled Automation:** Background daemon mode for periodic folder cleanup.
- 🔎 **Advanced Filtering:** Rules for file size thresholds, extensions, and subdirectory exclusions.
- 📈 **Storage Analytics:** Interactive charts for category usage breakdowns.
- ⚙️ **Custom Rule Engine:** Configurable folder rules and custom extension groupings.
- 🧪 **Automated Testing:** Unit test suite for file system operations and hash calculations.

---

##Demo

<img width="1120" height="781" alt="Screenshot 2026-10-18 at 11 54 44 PM" src="https://github.com/user-attachments/assets/a3d46edf-6f4f-43e4-8e04-f9a98390db7d" />
