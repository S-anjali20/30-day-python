
# 📚 Day 10 — AI Research Paper Summarizer

An AI-powered desktop application built with Python that converts research papers into easy-to-understand summaries, structured notes, answers to questions, and study flashcards.

The application uses a locally running AI model through Ollama, allowing users to summarize and explore research papers without requiring a cloud AI API key.

## ✨ Features

- 📄 **PDF Text Extraction:** Upload research papers in PDF format and extract readable text.
- 🧠 **AI-Powered Summarization:** Generate structured notes covering the research objective, methodology, key findings, limitations, and conclusion.
- 💬 **Document-Based Q&A:** Ask questions about the uploaded paper and receive AI-generated answers based on relevant text passages.
- 🗂️ **Flashcard Generation:** Create question-and-answer flashcards for revision and learning.
- 💾 **Export Notes:** Save summaries, answers, and flashcards as Markdown or plain text files.
- 🖥️ **Modern Desktop Interface:** Use a clean, tab-based GUI built with CustomTkinter.
- 🔒 **Local AI Processing:** Run inference locally using Ollama instead of a cloud AI API.
- ⚠️ **Error Handling:** Handle connection failures, missing models, unreadable PDFs, and file-export errors.
- 📑 **Long-Document Support:** Split extracted text into overlapping chunks for summarization.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.12 | Core programming language |
| CustomTkinter | Desktop graphical user interface |
| Ollama | Local AI model runtime |
| Qwen 3.5 4B | Language model |
| pypdf | PDF text extraction |
| Requests | Communication with Ollama's local API |
| python-dotenv | Environment configuration |
| Threading | Run AI tasks without freezing the interface |
| pathlib | File and directory management |

## 📁 Project Structure

```text
Day10_AI_Research_Paper_Summarizer/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── outputs/
```

- `main.py` — Main application and GUI.
- `requirements.txt` — Required Python libraries.
- `.env.example` — Example Ollama configuration.
- `.gitignore` — Files excluded from Git tracking.
- `outputs/` — Folder for exported research notes.



## 🔐 Privacy and Limitations

- Research text is processed through the local Ollama service.
- No cloud AI API key is required.
- Downloading the model requires an internet connection.
- Scanned PDFs may require OCR because `pypdf` does not extract text directly from page images.
- Keyword-based retrieval may miss relevant passages that use different terminology.
- The flashcard generator uses only a subset of document chunks in this version.
- AI-generated summaries and answers may be incomplete or inaccurate.

Always verify important claims, statistics, and conclusions against the original research paper.

## 🎯 Learning Outcomes

Through this project, I practised:

- Building a desktop application using CustomTkinter.
- Extracting and preprocessing text from PDF documents.
- Integrating a locally running language model with Python.
- Writing prompts for structured AI outputs.
- Splitting long documents into smaller chunks.
- Implementing basic retrieval for document-based Q&A.
- Running background tasks in a GUI application.
- Managing configuration with environment variables.
- Handling errors and exporting generated reports.
- Building practical AI applications without relying on a cloud AI API.

## 🔮 Future Improvements

- Add OCR support for scanned research papers.
- Implement semantic search using embeddings and a vector database.
- Include source-page citations in generated answers.
- Support multiple research papers in one workspace.
- Add interactive flashcards and quiz scoring.
- Add task cancellation and improved progress reporting.
- Write automated tests for PDF processing, retrieval, and exports.
- Improve long-document summarization with hierarchical summaries.

## 📅 Day 10 of My 30-Day Python Projects Challenge

This project is part of my **30-Day Python Projects Challenge**, where I am progressing from core Python programming toward practical AI and machine learning applications.

My goal is to learn by building useful projects, documenting my progress, and continuously improving my software development skills.

##Demo
<img width="1102" height="785" alt="Screenshot 2026-10-10 at 9 09 28 PM" src="https://github.com/user-attachments/assets/0cfbe0bd-5333-495b-be37-593e0fb9f045" />


This project is intended for educational and portfolio purposes. Add a `LICENSE` file if you decide to distribute the project under a specific open-source license.
