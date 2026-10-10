# 🤖 AI Resume Analyzer & Job Matcher

An AI-powered desktop application built with Python that analyzes resumes, compares skills against a job description, and provides personalized feedback using Groq AI.

## ✨ Features

* **📄 Resume Upload:** Upload a resume in PDF format.
* **📝 Job Description Matching:** Paste a job description to identify relevant skills.
* **🎯 Resume Match Score:** Calculate a match score based on the skills found in the resume.
* **✅ Matched Skills:** Display skills that match the job requirements.
* **❌ Missing Skills:** Identify relevant skills that may be missing from the resume.
* **🧠 AI-Powered Feedback:** Use Groq AI to generate suggestions for improving the resume.
* **💾 Save Analysis Report:** Save the analysis results as a text file.
* **🖥️ Desktop GUI:** Simple graphical interface built with CustomTkinter.
* **🔐 API Key Protection:** Store API credentials in a `.env` file instead of hardcoding them.

## 🛠️ Technologies & Libraries Used

* **Python** — Core programming language
* **CustomTkinter** — Modern desktop GUI
* **Groq** — AI-generated resume feedback
* **pypdf** — Extract text from PDF resumes
* **python-dotenv** — Load environment variables securely





## 🚀 How to Use

1. Launch the application.
2. Upload your resume in PDF format.
3. Paste the job description into the provided text area.
4. Start the analysis.
5. Review your match score, matched skills, and missing skills.
6. Read the AI-generated suggestions if Groq feedback is available.
7. Save the report for future reference.

## 🧮 How the Match Score Works

The application uses a predefined skill keyword list to compare the resume with the job description.

The score is based on the proportion of detected job-related skills that are also found in the resume. It is a basic keyword-based estimate, not a professional hiring assessment.

## 🎓 Learning Outcomes

Through this project, I practiced:

* Building desktop applications using Python.
* Extracting text from PDF documents.
* Working with environment variables and API keys.
* Integrating a large language model through an API.
* Handling API errors and missing responses.
* Comparing text using keyword matching.
* Generating and saving analysis reports.

## 🔮 Future Improvements

* Add support for DOCX resumes.
* Expand the skill database for different job roles.
* Improve semantic matching beyond exact keywords.
* Add resume section detection and formatting suggestions.
* Compare multiple job descriptions.
* Export reports in PDF format.
* Add resume privacy controls and local processing options.

## ⚠️ Disclaimer

This project provides basic resume feedback for educational purposes. The match score is based on limited keyword matching and does not predict hiring outcomes. AI feedback may be incomplete or inaccurate. Always verify suggestions and include only truthful qualifications in your resume.

## Demo
<img width="1123" height="844" alt="Screenshot 2026-10-10 at 9 46 45 AM" src="https://github.com/user-attachments/assets/e96d7406-6ff7-4dfd-9497-727222cf5c74" />

