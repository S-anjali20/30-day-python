# 🎧 Day 25 — SoundSpace: Local Desktop Music Player

A local desktop music player built with Python and CustomTkinter as part of my **30 Days, 30 Python Projects Challenge**.

**SoundSpace** lets users play audio files stored on their computer, organize tracks into custom playlists, control playback, view animated visualizer effects, and revisit their listening history through a modern dark-mode desktop interface.

---

## ✨ Features

- 🎵 **Local Music Playback:** Play local audio files (`MP3`, `WAV`, `OGG`) directly from your computer.
- ⏯️ **Playback Controls:** Full play, pause, skip forward/backward, shuffle, and repeat modes.
- 📑 **Playlist Management:** Create custom playlists and organize your track library.
- 🔀 **Shuffle & Repeat:** Shuffle track order or loop current tracks and playlists continuously.
- 📊 **Animated Visualizer:** Enjoy animated visual audio effects while tracks play.
- 🔍 **Search Music:** Instantly filter and search tracks by filename.
- 📜 **Listening History:** Automatically store recently played tracks and timestamps in a local SQLite database.
- 🌙 **Modern Dark Interface:** Clean, responsive desktop user interface built with CustomTkinter.
- 🔒 **Privacy-Focused:** Runs completely offline without external APIs or cloud file uploads.

---

## 🛠️ Tech Stack

| Technology / Library | Purpose |
| :--- | :--- |
| **Python** | Core application logic |
| **`customtkinter`** | Modern dark-themed desktop GUI framework |
| **`pygame`** | Cross-platform audio decoding and playback engine (`pygame.mixer`) |
| **`sqlite3`** | Local database for persistent listening history logs |
| **`mutagen`** | Audio file metadata and track duration extraction |

---

## Demo
<img width="1044" height="724" alt="Screenshot 2026-10-28 at 9 38 05 AM" src="https://github.com/user-attachments/assets/15de4690-2b81-4bef-8a4e-74c611f96085" />
