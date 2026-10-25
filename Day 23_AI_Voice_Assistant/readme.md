# 🎙️🤖 Day 23 — AJI: AI Voice Assistant

Meet **AJI**, a personal AI voice assistant built with Python as part of my **30 Days, 30 Python Projects Challenge**.

AJI combines voice recognition, AI-powered conversational intelligence, live web search, and desktop automation inside a modern dark-themed graphical interface. You can type messages, speak into your microphone, ask complex questions, and open your favorite websites—all from a single desktop app.

---

## ✨ Features

- 🎙️ **Voice Input:** Speak naturally into your microphone using speech recognition.
- 🔊 **Voice Responses:** Hear AI responses spoken back to you via native macOS speech output (`say`).
- 💬 **AI-Powered Conversations:** Ask questions and engage in natural conversations powered by Groq or OpenAI APIs.
- 🌐 **Live Web Search:** Augment AI knowledge with real-time web search results using DuckDuckGo (`ddgs`).
- ⚡ **Quick Desktop Commands:** Instantly check time/date or open apps like YouTube, Google, Gmail, GitHub, and ChatGPT.
- 🔎 **Google Search Automation:** Launch pre-filled Google search pages directly via text or voice commands.
- 🎨 **Modern Dark Interface:** Responsive desktop dashboard built with CustomTkinter.
- 🧠 **Contextual History:** Retain conversational context across recent messages.
- 🔇 **Speech Controls:** Easily toggle spoken audio responses on or off.
- 🧹 **Clean Slate:** Clear chat history and launch fresh conversations with one click.
- 🧵 **Non-Blocking Architecture:** Asynchronous multithreading keeps the UI 100% smooth during network calls and audio processing.

---

## 🛠️ Tech Stack

| Technology / Library | Purpose |
| :--- | :--- |
| **Python** | Core application logic |
| **`customtkinter`** | Modern dark-themed GUI framework |
| **`SpeechRecognition` & `PyAudio`** | Capturing and converting microphone audio input into text |
| **macOS `say` tool** | Text-To-Speech (TTS) voice generation |
| **Groq API / OpenAI API** | Conversational AI models |
| **`ddgs` (DuckDuckGo Search)** | Real-time live web search extraction |
| **`threading` & `queue`** | Non-blocking background worker management |

---

## Demo
<img width="1077" height="767" alt="Screenshot 2026-10-25 at 9 40 42 AM" src="https://github.com/user-attachments/assets/5031c707-d12e-4852-8c83-1fdc80b5d622" />
