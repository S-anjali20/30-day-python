import os
import re
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from dotenv import load_dotenv
from groq import Groq, APIConnectionError, APIStatusError, APITimeoutError
from pypdf import PdfReader

load_dotenv()

APP_TITLE = "AI Resume Analyzer & Job Matcher"
DEFAULT_MODEL = "openai/gpt-oss-120b" 

SKILLS = [
    "python", "java", "c++", "c#", "javascript", "typescript", "sql", "html", "css",
    "react", "node.js", "flask", "django", "fastapi", "machine learning", "deep learning",
    "artificial intelligence", "data analysis", "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "natural language processing", "nlp", "computer vision",
    "excel", "power bi", "tableau", "aws", "azure", "google cloud", "docker", "kubernetes",
    "git", "github", "linux", "rest api", "api", "mongodb", "postgresql", "mysql",
    "blockchain", "solidity", "smart contracts", "cybersecurity", "networking",
    "data structures", "algorithms", "object-oriented programming", "oop",
    "communication", "leadership", "problem solving", "project management",
    "agile", "testing", "selenium", "figma"
]


def normalize(text):
    text = text.lower().replace("nodejs", "node.js").replace("powerbi", "power bi")
    return re.sub(r"\s+", " ", text)


def extract_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if not text:
        raise ValueError("No selectable text found. This may be a scanned PDF; use a text-based PDF.")
    return text


def find_skills(text):
    normalized = normalize(text)
    found = set()
    for skill in SKILLS:
        pattern = r"(?<![a-z0-9+#.])" + re.escape(skill) + r"(?![a-z0-9+#.])"
        if re.search(pattern, normalized):
            found.add(skill)
    return found


def calculate_match(resume_text, job_text):
    resume_skills = find_skills(resume_text)
    job_skills = find_skills(job_text)
    matched = resume_skills & job_skills
    missing = job_skills - resume_skills
    score = round(len(matched) / len(job_skills) * 100) if job_skills else 0
    note = (
        "Score = detected job skills also found in the resume ÷ detected job skills × 100."
        if job_skills else
        "No skills from the built-in skill list were detected in the job description. "
        "Add terms to SKILLS in main.py."
    )
    return {
        "score": score, "resume_skills": sorted(resume_skills),
        "job_skills": sorted(job_skills), "matched": sorted(matched),
        "missing": sorted(missing), "extra": sorted(resume_skills - job_skills),
        "note": note,
    }


def generate_ai_feedback(resume_text, job_text, results):
    """Return feedback and a status string; API errors do not discard local results."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    model = os.getenv("GROQ_MODEL", DEFAULT_MODEL).strip()

    if not api_key or api_key.lower() in {"your_groq_api_key_here", "your_api_key_here"}:
        return (
            "AI feedback is unavailable because GROQ_API_KEY is not configured. "
            "Add your Groq key to .env. Local skill matching is still available.",
            "Local analysis complete — configure Groq for AI feedback."
        )

    prompt = f"""
Give concise, honest resume feedback based only on the supplied text. Never invent
qualifications or suggest the candidate claim skills they do not have. The score is a
rough keyword estimate, not a hiring prediction.

Keyword match score: {results['score']}%
Matched skills: {', '.join(results['matched']) or 'None detected'}
Potentially missing skills: {', '.join(results['missing']) or 'None detected'}

RESUME:
{resume_text[:10000]}

JOB DESCRIPTION:
{job_text[:7000]}

Use headings:
1. Overall assessment
2. Three tailored resume improvements
3. Skills to learn
4. Keywords to include only if truthful
5. One short next-step plan
"""
    try:
        client = Groq(api_key=api_key, timeout=35.0, max_retries=1)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You provide practical, truthful career feedback."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        feedback = response.choices[0].message.content or "The model returned an empty response."
        return feedback.strip(), f"Analysis complete using Groq model: {model}"

    except APIStatusError as exc:
        code = exc.status_code
        if code == 401:
            message = "Invalid Groq API key. Check GROQ_API_KEY in .env; do not use an OpenAI key."
        elif code == 403:
            message = "Groq denied access. Check account access, permissions, and model availability."
        elif code == 404:
            message = f"Model '{model}' was not found. Check https://console.groq.com/docs/models and update GROQ_MODEL."
        elif code == 429:
            message = "Groq rate limit or quota reached. Check Groq Console limits and retry later."
        else:
            message = f"Groq returned HTTP {code}. Check the key, model ID, account limits, and service status."
        return f"AI feedback unavailable: {message}\n\nYour local skill analysis is complete.", f"Local analysis complete — Groq API error {code}."
    except (APIConnectionError, APITimeoutError) as exc:
        label = "connection failed" if isinstance(exc, APIConnectionError) else "request timed out"
        return (
            f"Groq {label}. Check your internet connection and try again. "
            "Your local skill analysis is complete.",
            f"Local analysis complete — Groq {label}."
        )
    except Exception as exc:
        return (
            f"AI feedback failed ({type(exc).__name__}). Check your Groq settings and installed packages. "
            "Your local skill analysis is complete.",
            "Local analysis complete — AI feedback could not be generated."
        )


class ResumeAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1120x820")
        self.minsize(900, 680)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.last_report = ""
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        header = ctk.CTkFrame(self, corner_radius=16)
        header.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text=APP_TITLE, font=ctk.CTkFont(size=25, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(16, 3), sticky="w"
        )
        ctk.CTkLabel(
            header, text="Compare skills • estimate keyword match • optional Groq AI feedback"
        ).grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")

        inputs = ctk.CTkFrame(self, corner_radius=16)
        inputs.grid(row=1, column=0, padx=18, pady=8, sticky="ew")
        inputs.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(inputs, text="Resume", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=14, pady=(14, 5), sticky="w"
        )
        ctk.CTkLabel(inputs, text="Job description", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=1, padx=14, pady=(14, 5), sticky="w"
        )
        self.resume_box = ctk.CTkTextbox(inputs, height=180, wrap="word")
        self.resume_box.grid(row=1, column=0, padx=(14, 7), pady=(0, 8), sticky="nsew")
        self.resume_box.insert("1.0", "Upload a PDF resume, or paste resume text here...")
        self.job_box = ctk.CTkTextbox(inputs, height=180, wrap="word")
        self.job_box.grid(row=1, column=1, padx=(7, 14), pady=(0, 8), sticky="nsew")
        self.job_box.insert("1.0", "Paste the job description here...")
        ctk.CTkButton(inputs, text="Upload Resume PDF", command=self.upload_pdf, width=180).grid(
            row=2, column=0, padx=14, pady=(2, 14), sticky="w"
        )
        self.file_label = ctk.CTkLabel(inputs, text="No PDF selected", anchor="w")
        self.file_label.grid(row=2, column=0, padx=(205, 12), pady=(2, 14), sticky="ew")

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, padx=18, pady=(4, 8), sticky="ew")
        actions.grid_columnconfigure(0, weight=1)
        self.analyze_button = ctk.CTkButton(
            actions, text="Analyze Resume", height=42, command=self.start_analysis,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.analyze_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.save_button = ctk.CTkButton(
            actions, text="Save Report", height=42, state="disabled", command=self.save_report
        )
        self.save_button.grid(row=0, column=1, padx=(8, 0))
        self.status_label = ctk.CTkLabel(
            self, text="Local matching works without a Groq key; AI feedback requires Groq API access."
        )
        self.status_label.grid(row=3, column=0, padx=20, pady=(0, 5), sticky="w")

        results_frame = ctk.CTkFrame(self, corner_radius=16)
        results_frame.grid(row=4, column=0, padx=18, pady=(4, 18), sticky="nsew")
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)
        self.score_label = ctk.CTkLabel(
            results_frame, text="Match score: —", font=ctk.CTkFont(size=21, weight="bold")
        )
        self.score_label.grid(row=0, column=0, padx=16, pady=(14, 8), sticky="w")
        self.output_box = ctk.CTkTextbox(results_frame, wrap="word")
        self.output_box.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="nsew")
        self.output_box.insert("1.0", "Your analysis will appear here.")

    def upload_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not path:
            return
        try:
            text = extract_pdf_text(path)
        except Exception as exc:
            messagebox.showerror("Could not read PDF", str(exc))
            return
        self.resume_box.delete("1.0", "end")
        self.resume_box.insert("1.0", text)
        self.file_label.configure(text=Path(path).name)

    def start_analysis(self):
        resume = self.resume_box.get("1.0", "end").strip()
        job = self.job_box.get("1.0", "end").strip()
        if not resume or resume.startswith("Upload a PDF resume"):
            messagebox.showwarning("Resume required", "Upload a PDF or paste resume text.")
            return
        if not job or job == "Paste the job description here...":
            messagebox.showwarning("Job description required", "Paste the job description first.")
            return
        self.analyze_button.configure(state="disabled", text="Analyzing...")
        self.save_button.configure(state="disabled")
        self.status_label.configure(text="Matching skills and requesting optional Groq feedback...")
        threading.Thread(target=self._worker, args=(resume, job), daemon=True).start()

    def _worker(self, resume, job):
        # Local analysis is completed regardless of API availability.
        results = calculate_match(resume, job)
        feedback, status = generate_ai_feedback(resume, job, results)
        report = self.format_report(results, feedback)
        self.after(0, lambda: self.show_results(results, report, status))

    @staticmethod
    def format_report(results, feedback):
        def listing(items):
            return ", ".join(items) if items else "None detected"
        return (
            f"AI RESUME ANALYZER & JOB MATCHER\n{'=' * 38}\n\n"
            f"MATCH SCORE: {results['score']}%\n{results['note']}\n\n"
            f"MATCHED SKILLS ({len(results['matched'])})\n{listing(results['matched'])}\n\n"
            f"POTENTIALLY MISSING JOB SKILLS ({len(results['missing'])})\n{listing(results['missing'])}\n\n"
            f"OTHER SKILLS FOUND IN RESUME ({len(results['extra'])})\n{listing(results['extra'])}\n\n"
            f"GROQ AI FEEDBACK\n{'-' * 38}\n{feedback}\n\n"
            "DISCLAIMER\nThis score uses a limited keyword list and is not a hiring prediction. "
            "Only include truthful qualifications in your resume.\n"
        )

    def show_results(self, results, report, status):
        self.last_report = report
        self.score_label.configure(text=f"Match score: {results['score']}%")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", report)
        self.analyze_button.configure(state="normal", text="Analyze Resume")
        self.save_button.configure(state="normal")
        self.status_label.configure(text=status)

    def save_report(self):
        if not self.last_report:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text report", "*.txt")],
            initialfile="resume_analysis_report.txt"
        )
        if not path:
            return
        try:
            Path(path).write_text(self.last_report, encoding="utf-8")
            messagebox.showinfo("Report saved", f"Report saved to:\n{path}")
        except OSError as exc:
            messagebox.showerror("Save failed", str(exc))


if __name__ == "__main__":
    ResumeAnalyzerApp().mainloop()
