
import customtkinter as ctk
import hashlib
import ipaddress
import json
import os
import re
import secrets
import string
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox
from urllib.parse import urlparse

# ---------------- CONFIGURATION ----------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

APP_NAME = "CyberShield"
BG = "#0B1020"
SIDEBAR = "#10182B"
CARD = "#151F35"
BORDER = "#283754"
GREEN = "#37E6A0"
BLUE = "#64B5F6"
YELLOW = "#FFD166"
RED = "#FF647C"
TEXT = "#F1F5F9"
MUTED = "#9BAAC4"

DATA_DIR = os.path.join(os.path.expanduser("~"), ".cybershield")
BASELINE_FILE = os.path.join(DATA_DIR, "file_baselines.json")
EVENT_FILE = os.path.join(DATA_DIR, "security_events.json")

os.makedirs(DATA_DIR, exist_ok=True)


# ---------------- HELPERS ----------------

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return default


def save_json(path, data):
    temporary_path = path + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
    os.replace(temporary_path, path)


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


# ---------------- APPLICATION ----------------

class CyberShield(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CyberShield | Security Learning Center")
        self.geometry("1180x760")
        self.minsize(980, 650)
        self.configure(fg_color=BG)

        self.baselines = load_json(BASELINE_FILE, {})
        self.events = load_json(EVENT_FILE, [])
        self.active_page = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_sidebar()
        self.content = ctk.CTkFrame(
            self, fg_color=BG, corner_radius=0
        )
        self.content.grid(
            row=0, column=1, sticky="nsew", padx=22, pady=20
        )
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self.show_dashboard()

    # ---------------- SHARED UI ----------------

    def build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self, width=230, fg_color=SIDEBAR, corner_radius=0
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text="🛡 CyberShield",
            font=("Arial", 24, "bold"), text_color=GREEN
        ).pack(padx=18, pady=(28, 4), anchor="w")

        ctk.CTkLabel(
            sidebar, text="SECURITY LEARNING CENTER",
            font=("Arial", 10, "bold"), text_color=MUTED
        ).pack(padx=20, pady=(0, 26), anchor="w")

        items = [
            ("Dashboard", self.show_dashboard),
            ("Password Analyzer", self.show_password),
            ("URL Security Check", self.show_url),
            ("File Integrity", self.show_integrity),
            ("Threat Simulator", self.show_threats),
        ]

        for label, command in items:
            ctk.CTkButton(
                sidebar,
                text=label,
                anchor="w",
                height=43,
                fg_color="transparent",
                hover_color=CARD,
                text_color=TEXT,
                font=("Arial", 14),
                command=command,
            ).pack(fill="x", padx=12, pady=4)

        ctk.CTkFrame(
            sidebar, height=1, fg_color=BORDER
        ).pack(fill="x", padx=15, pady=(22, 12))

        ctk.CTkLabel(
            sidebar,
            text="LOCAL EDUCATIONAL TOOL\nNo cloud scanning or live threat feed.",
            justify="left",
            wraplength=190,
            text_color=MUTED,
            font=("Arial", 11),
        ).pack(side="bottom", anchor="w", padx=18, pady=22)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def page_header(self, title, subtitle):
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))

        ctk.CTkLabel(
            header, text=title,
            font=("Arial", 29, "bold"), text_color=TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            header, text=subtitle,
            font=("Arial", 13), text_color=MUTED
        ).pack(anchor="w", pady=(4, 0))

    def make_card(self, parent, title, description=None):
        card = ctk.CTkFrame(
            parent, fg_color=CARD, corner_radius=14,
            border_width=1, border_color=BORDER
        )
        if title:
            ctk.CTkLabel(
                card, text=title,
                font=("Arial", 17, "bold"), text_color=TEXT
            ).pack(anchor="w", padx=18, pady=(16, 5))
        if description:
            ctk.CTkLabel(
                card, text=description,
                font=("Arial", 12), text_color=MUTED,
                wraplength=650, justify="left"
            ).pack(anchor="w", padx=18, pady=(0, 10))
        return card

    def output_box(self, parent, height=150):
        box = ctk.CTkTextbox(
            parent, height=height, fg_color="#0C1426",
            text_color=TEXT, border_color=BORDER,
            border_width=1, corner_radius=9,
            font=("Menlo", 12), wrap="word"
        )
        return box

    def log_event(self, severity, title, detail):
        self.events.insert(0, {
            "time": timestamp(),
            "severity": severity,
            "title": title,
            "detail": detail,
        })
        self.events = self.events[:200]
        try:
            save_json(EVENT_FILE, self.events)
        except OSError as error:
            messagebox.showwarning(
                "Storage warning",
                f"Event could not be saved:\n{error}"
            )

    # ---------------- DASHBOARD ----------------

    def show_dashboard(self):
        self.active_page = "Dashboard"
        self.clear_content()
        self.page_header(
            "Security Dashboard",
            "Your local cybersecurity learning workspace."
        )

        body = ctk.CTkScrollableFrame(
            self.content, fg_color="transparent"
        )
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure((0, 1), weight=1)

        stats = [
            ("FILE BASELINES", str(len(self.baselines)), GREEN),
            ("SECURITY EVENTS", str(len(self.events)), BLUE),
            ("TOOLS AVAILABLE", "04", YELLOW),
        ]

        for index, (label, value, color) in enumerate(stats):
            card = self.make_card(body, label)
            card.grid(
                row=0, column=index % 2,
                padx=6, pady=6, sticky="ew"
            )
            ctk.CTkLabel(
                card, text=value, font=("Arial", 30, "bold"),
                text_color=color
            ).pack(anchor="w", padx=18, pady=(0, 18))

        overview = self.make_card(
            body, "Explore CyberShield",
            "Choose a tool from the sidebar to start."
        )
        overview.grid(
            row=1, column=0, columnspan=2,
            padx=6, pady=12, sticky="ew"
        )

        descriptions = [
            "01  Password Analyzer — inspect password strength locally.",
            "02  URL Security Check — identify suspicious URL patterns.",
            "03  File Integrity — compare SHA-256 hashes against baselines.",
            "04  Threat Simulator — review generated educational events.",
        ]

        for description in descriptions:
            ctk.CTkLabel(
                overview, text=description, text_color=TEXT,
                font=("Arial", 13), anchor="w"
            ).pack(fill="x", padx=20, pady=7)

        note = self.make_card(
            body, "Important security note",
            "This application performs local checks and heuristic analysis. "
            "It is not an antivirus, does not consult live threat feeds, "
            "and cannot guarantee that a password or URL is safe."
        )
        note.grid(
            row=2, column=0, columnspan=2,
            padx=6, pady=8, sticky="ew"
        )

    # ---------------- PASSWORD ANALYZER ----------------

    def show_password(self):
        self.active_page = "Password Analyzer"
        self.clear_content()
        self.page_header(
            "Password Strength Analyzer",
            "Evaluate password characteristics without sending them anywhere."
        )

        card = self.make_card(
            self.content, "Analyze a password",
            "Use a test password, not a password you currently use."
        )
        card.grid(row=1, column=0, sticky="new")

        entry_row = ctk.CTkFrame(card, fg_color="transparent")
        entry_row.pack(fill="x", padx=18, pady=10)

        self.password_entry = ctk.CTkEntry(
            entry_row, placeholder_text="Enter a test password...",
            show="•", height=42
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.show_password_var = tk.BooleanVar(value=False)

        def toggle_visibility():
            self.password_entry.configure(
                show="" if self.show_password_var.get() else "•"
            )

        ctk.CTkCheckBox(
            entry_row, text="Show",
            variable=self.show_password_var,
            command=toggle_visibility
        ).pack(side="right")

        self.strength_label = ctk.CTkLabel(
            card, text="Strength: Not analyzed",
            font=("Arial", 17, "bold"), text_color=MUTED
        )
        self.strength_label.pack(anchor="w", padx=18, pady=(8, 4))

        self.strength_bar = ctk.CTkProgressBar(
            card, height=12, progress_color=GREEN
        )
        self.strength_bar.pack(fill="x", padx=18, pady=8)
        self.strength_bar.set(0)

        ctk.CTkButton(
            card, text="Analyze Password",
            fg_color="#147D5A", hover_color="#106849",
            command=self.analyze_password
        ).pack(anchor="w", padx=18, pady=12)

        self.password_result = self.output_box(card, 190)
        self.password_result.pack(fill="x", padx=18, pady=(0, 18))

    def analyze_password(self):
        password = self.password_entry.get()

        if not password:
            messagebox.showinfo("Missing password", "Enter a test password first.")
            return

        score = 0
        suggestions = []
        length = len(password)

        if length >= 8:
            score += 1
        else:
            suggestions.append("Use at least 8 characters; 14 or more is preferable.")

        if length >= 14:
            score += 1

        if re.search(r"[a-z]", password):
            score += 1
        else:
            suggestions.append("Consider including lowercase letters.")

        if re.search(r"[A-Z]", password):
            score += 1
        else:
            suggestions.append("Consider including uppercase letters.")

        if re.search(r"\d", password):
            score += 1
        else:
            suggestions.append("Consider including numbers.")

        if re.search(r"[^A-Za-z0-9]", password):
            score += 1
        else:
            suggestions.append("Consider including symbols if supported by the service.")

        if re.search(r"(.)\1{2,}", password):
            score -= 1
            suggestions.append("Avoid long runs of the same character.")

        if re.search(
            r"password|qwerty|letmein|admin|welcome|123456",
            password.lower()
        ):
            score -= 2
            suggestions.append("Avoid common password patterns.")

        score = max(0, min(6, score))

        if length < 8 or score <= 2:
            level, color = "Weak", RED
        elif length >= 14 and score >= 5:
            level, color = "Strong characteristics", GREEN
        else:
            level, color = "Moderate characteristics", YELLOW

        self.strength_label.configure(
            text=f"Assessment: {level}", text_color=color
        )
        self.strength_bar.configure(progress_color=color)
        self.strength_bar.set(score / 6)

        self.password_result.delete("1.0", "end")
        self.password_result.insert(
            "end",
            f"Length: {length} characters\n"
            f"Pattern score: {score}/6\n"
            f"Assessment: {level}\n\n"
            "Suggestions:\n"
        )

        if suggestions:
            self.password_result.insert(
                "end", "\n".join(f"• {item}" for item in suggestions)
            )
        else:
            self.password_result.insert(
                "end", "• No basic pattern issues were detected."
            )

        self.password_result.insert(
            "end",
            "\n\nThis simple heuristic is not a measure of actual entropy "
            "and does not check breached-password databases."
        )

        # Do not log or persist the password itself.
        self.log_event(
            "INFO", "Password analysis completed",
            f"Local pattern score: {score}/6; assessment: {level}"
        )

    # ---------------- URL SECURITY CHECK ----------------

    def show_url(self):
        self.active_page = "URL Security Check"
        self.clear_content()
        self.page_header(
            "URL Security Check",
            "Inspect a URL for potentially suspicious structural patterns."
        )

        card = self.make_card(
            self.content, "Analyze a URL",
            "Paste a URL as text. This tool will not open or visit it."
        )
        card.grid(row=1, column=0, sticky="new")

        self.url_entry = ctk.CTkEntry(
            card,
            placeholder_text="https://example.com/login",
            height=42
        )
        self.url_entry.pack(fill="x", padx=18, pady=10)

        ctk.CTkButton(
            card, text="Check URL",
            fg_color="#147D5A", hover_color="#106849",
            command=self.analyze_url
        ).pack(anchor="w", padx=18, pady=8)

        self.url_result = self.output_box(card, 280)
        self.url_result.pack(fill="x", padx=18, pady=(8, 18))

    def analyze_url(self):
        raw = self.url_entry.get().strip()

        if not raw:
            messagebox.showinfo("Missing URL", "Enter a URL to inspect.")
            return

        findings = []
        risk = 0

        candidate = raw if "://" in raw else "http://" + raw

        try:
            parsed = urlparse(candidate)
            host = parsed.hostname
            _ = parsed.port
        except ValueError:
            host = None
            parsed = None

        if not parsed or not host:
            self.url_result.delete("1.0", "end")
            self.url_result.insert(
                "end", "Unable to parse this input as a valid URL."
            )
            return

        if parsed.scheme.lower() not in ("http", "https"):
            findings.append("Unexpected URL scheme.")
            risk += 2

        if parsed.username is not None or parsed.password is not None:
            findings.append("URL contains user-info before the hostname.")
            risk += 3

        try:
            ipaddress.ip_address(host)
            findings.append("Hostname is a raw IP address rather than a domain.")
            risk += 2
        except ValueError:
            pass

        if "xn--" in host.lower():
            findings.append("Hostname contains an internationalized/punycode label.")
            risk += 2

        if len(host) > 50:
            findings.append("Hostname is unusually long.")
            risk += 1

        if host.count(".") >= 4:
            findings.append("Hostname contains many subdomain levels.")
            risk += 1

        if len(raw) > 180:
            findings.append("URL is unusually long.")
            risk += 1

        if "@" in raw:
            findings.append("URL contains an @ character; inspect its structure carefully.")
            risk += 1

        if re.search(r"(login|verify|account|secure|update|password)", parsed.path, re.I):
            findings.append("Path contains a login or account-related keyword.")
            risk += 1

        if parsed.scheme.lower() == "http":
            findings.append("Connection scheme is HTTP, not HTTPS.")
            risk += 1

        if re.search(r"%[0-9a-f]{2}", raw, re.I):
            findings.append("URL uses percent-encoded characters.")
            risk += 1

        if risk >= 5:
            level = "HIGHER RISK PATTERNS"
        elif risk >= 2:
            level = "SUSPICIOUS PATTERNS FOUND"
        else:
            level = "FEW HEURISTIC WARNINGS"

        self.url_result.delete("1.0", "end")
        self.url_result.insert(
            "end",
            f"Input: {raw}\n"
            f"Parsed hostname: {host}\n"
            f"Scheme: {parsed.scheme}\n"
            f"Heuristic risk points: {risk}\n"
            f"Assessment: {level}\n\nFindings:\n"
        )

        if findings:
            self.url_result.insert(
                "end", "\n".join(f"• {finding}" for finding in findings)
            )
        else:
            self.url_result.insert(
                "end", "• No configured warning patterns were detected."
            )

        self.url_result.insert(
            "end",
            "\n\nThis is not a reputation check. A URL with few warnings "
            "can still be malicious. Nothing was opened or transmitted."
        )

        severity = "WARNING" if risk >= 2 else "INFO"
        self.log_event(
            severity, "URL inspection completed",
            f"Hostname: {host}; heuristic points: {risk}"
        )

    # ---------------- FILE INTEGRITY ----------------

    def show_integrity(self):
        self.active_page = "File Integrity"
        self.clear_content()
        self.page_header(
            "File Integrity Monitor",
            "Create a local SHA-256 baseline and detect content changes."
        )

        card = self.make_card(
            self.content, "Inspect a file",
            "Choose a file you own or are authorized to inspect."
        )
        card.grid(row=1, column=0, sticky="new")

        self.file_path_var = tk.StringVar(value="No file selected")

        ctk.CTkLabel(
            card, textvariable=self.file_path_var,
            text_color=MUTED, wraplength=700, justify="left"
        ).pack(fill="x", padx=18, pady=10)

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(fill="x", padx=18, pady=8)

        ctk.CTkButton(
            buttons, text="Choose File",
            command=self.choose_file
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            buttons, text="Calculate SHA-256",
            command=self.calculate_hash
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            buttons, text="Save Baseline",
            fg_color="#147D5A", hover_color="#106849",
            command=self.save_baseline
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            buttons, text="Compare Baseline",
            command=self.compare_baseline
        ).pack(side="left", padx=8)

        self.hash_result = self.output_box(card, 230)
        self.hash_result.pack(fill="x", padx=18, pady=(8, 18))

        self.selected_file = None
        self.current_hash = None

    def choose_file(self):
        path = filedialog.askopenfilename(title="Select a file")

        if path:
            self.selected_file = path
            self.current_hash = None
            self.file_path_var.set(path)
            self.hash_result.delete("1.0", "end")
            self.hash_result.insert(
                "end", "File selected. Calculate its hash to continue."
            )

    def calculate_hash(self):
        if not self.selected_file:
            messagebox.showinfo("Select a file", "Choose a file first.")
            return

        try:
            self.current_hash = sha256_file(self.selected_file)
        except OSError as error:
            messagebox.showerror("File error", str(error))
            return

        self.hash_result.delete("1.0", "end")
        self.hash_result.insert(
            "end",
            f"File: {os.path.basename(self.selected_file)}\n\n"
            f"SHA-256:\n{self.current_hash}\n\n"
            "This digest represents the file contents at the time of hashing."
        )

    def save_baseline(self):
        if not self.selected_file:
            messagebox.showinfo("Select a file", "Choose a file first.")
            return

        if not self.current_hash:
            self.calculate_hash()
            if not self.current_hash:
                return

        self.baselines[self.selected_file] = {
            "sha256": self.current_hash,
            "saved_at": timestamp(),
        }

        try:
            save_json(BASELINE_FILE, self.baselines)
        except OSError as error:
            messagebox.showerror("Save failed", str(error))
            return

        self.log_event(
            "INFO", "File baseline saved",
            os.path.basename(self.selected_file)
        )
        self.hash_result.insert("end", "\n\nBaseline saved successfully.")

    def compare_baseline(self):
        if not self.selected_file:
            messagebox.showinfo("Select a file", "Choose a file first.")
            return

        baseline = self.baselines.get(self.selected_file)

        if not baseline:
            messagebox.showinfo(
                "No baseline",
                "Save a baseline for this file before comparing it."
            )
            return

        try:
            current = sha256_file(self.selected_file)
        except OSError as error:
            messagebox.showerror("File error", str(error))
            return

        expected = baseline["sha256"]

        self.hash_result.delete("1.0", "end")

        if secrets.compare_digest(current, expected):
            status = "UNCHANGED"
            detail = "The file matches the saved baseline."
            severity = "INFO"
        else:
            status = "CHANGED"
            detail = "The file differs from the saved baseline."
            severity = "WARNING"

        self.hash_result.insert(
            "end",
            f"Integrity status: {status}\n\n"
            f"Saved SHA-256:\n{expected}\n\n"
            f"Current SHA-256:\n{current}\n\n{detail}\n\n"
            "A changed hash indicates different file contents, not "
            "necessarily malicious activity."
        )

        self.log_event(
            severity, f"File integrity: {status}",
            os.path.basename(self.selected_file)
        )

    # ---------------- THREAT SIMULATOR ----------------

    def show_threats(self):
        self.active_page = "Threat Simulator"
        self.clear_content()
        self.page_header(
            "Threat Simulator",
            "Generate sample security events for learning and UI testing."
        )

        card = self.make_card(
            self.content, "Simulated security events",
            "These are fictional events, not alerts from your device."
        )
        card.grid(row=1, column=0, sticky="nsew")
        self.content.grid_rowconfigure(1, weight=1)

        controls = ctk.CTkFrame(card, fg_color="transparent")
        controls.pack(fill="x", padx=18, pady=8)

        ctk.CTkButton(
            controls, text="Generate Sample Events",
            fg_color="#147D5A", hover_color="#106849",
            command=self.generate_events
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            controls, text="Refresh Log",
            command=self.refresh_events
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            controls, text="Clear Log",
            fg_color="#8B3045", hover_color="#702638",
            command=self.clear_events
        ).pack(side="left", padx=8)

        self.event_output = self.output_box(card, 400)
        self.event_output.pack(
            fill="both", expand=True, padx=18, pady=(8, 18)
        )

        self.refresh_events()

    def generate_events(self):
        samples = [
            (
                "INFO", "System integrity check",
                "A sample integrity check completed successfully."
            ),
            (
                "WARNING", "Repeated login failures",
                "Simulation: multiple unsuccessful login attempts."
            ),
            (
                "HIGH", "Suspicious attachment",
                "Simulation: an unknown attachment requires review."
            ),
            (
                "WARNING", "Unexpected file modification",
                "Simulation: a monitored file changed."
            ),
            (
                "INFO", "Security policy reviewed",
                "Simulation: a local security policy was checked."
            ),
        ]

        for severity, title, detail in samples:
            self.events.insert(0, {
                "time": timestamp(),
                "severity": severity,
                "title": title,
                "detail": detail,
                "simulated": True,
            })

        self.events = self.events[:200]

        try:
            save_json(EVENT_FILE, self.events)
        except OSError as error:
            messagebox.showerror("Save failed", str(error))
            return

        self.refresh_events()

    def refresh_events(self):
        if not hasattr(self, "event_output"):
            return

        self.event_output.delete("1.0", "end")

        if not self.events:
            self.event_output.insert(
                "end", "No events yet. Generate sample events to begin."
            )
            return

        for event in self.events:
            simulated = (
                " [SIMULATED]" if event.get("simulated") else ""
            )
            self.event_output.insert(
                "end",
                f"[{event['time']}] "
                f"[{event['severity']}] "
                f"{event['title']}{simulated}\n"
                f"  {event['detail']}\n\n"
            )

    def clear_events(self):
        if not messagebox.askyesno(
            "Clear events",
            "Delete all saved security events from this application?"
        ):
            return

        self.events = []

        try:
            save_json(EVENT_FILE, self.events)
        except OSError as error:
            messagebox.showerror("Save failed", str(error))
            return

        self.refresh_events()


# ---------------- START APPLICATION ----------------

if __name__ == "__main__":
    app = CyberShield()
    app.mainloop()
