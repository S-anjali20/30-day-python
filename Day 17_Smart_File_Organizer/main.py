import csv
import hashlib
import json
import os
import shutil
import threading
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

APP_DIR = Path.home() / ".smart_file_organizer"
LOG_FILE = APP_DIR / "operations.json"
REPORT_DIR = APP_DIR / "reports"

CATEGORIES = {
    "Images": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff", ".ico", ".svg", ".heic"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md", ".tex"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods", ".tsv"},
    "Presentations": {".ppt", ".pptx", ".key", ".odp"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".webm", ".m4v"},
    "Audio": {".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp", ".h", ".hpp",
             ".cs", ".php", ".rb", ".go", ".rs", ".swift", ".kt", ".json", ".xml", ".yaml", ".yml"},
    "Installers": {".dmg", ".pkg", ".exe", ".msi", ".apk", ".deb", ".rpm"},
}


def human_size(size):
    size = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{int(size)} B" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024


def category(path):
    for name, extensions in CATEGORIES.items():
        if path.suffix.lower() in extensions:
            return name
    return "Others"


def safe_destination(path):
    if not path.exists():
        return path
    number = 1
    while True:
        candidate = path.with_name(f"{path.stem} ({number}){path.suffix}")
        if not candidate.exists():
            return candidate
        number += 1


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class FileOrganizer(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("FileWise — Smart File Organizer")
        self.geometry("1120x760")
        self.minsize(900, 620)

        APP_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        self.folder = None
        self.files = []
        self.duplicate_groups = []
        self.preview = []
        self.busy = False
        self.operations = self.load_log()
        self.mode = tk.StringVar(value="By file type")
        self.custom_extensions = tk.StringVar(value=".pdf, .png, .jpg")
        self.folder_text = tk.StringVar(value="No folder selected")
        self.status = tk.StringVar(value="Select a folder to begin.")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.build_sidebar()
        self.main = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray96", "#111318"))
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 12))
        header.grid_columnconfigure(0, weight=1)
        self.heading = ctk.CTkLabel(header, text="Overview", font=ctk.CTkFont(size=27, weight="bold"))
        self.heading.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Organize confidently. Keep control.",
                     text_color="gray60").grid(row=1, column=0, sticky="w", pady=(3, 0))
        ctk.CTkButton(header, text="Choose folder", command=self.choose_folder).grid(row=0, column=1, rowspan=2)

        self.content = ctk.CTkFrame(self.main, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=22, pady=(0, 8))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
        footer = ctk.CTkFrame(self.main, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 12))
        footer.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(footer, textvariable=self.status, anchor="w",
                     text_color="gray60").grid(row=0, column=0, sticky="ew")
        self.progress = ctk.CTkProgressBar(footer, width=150)
        self.progress.grid(row=0, column=1, padx=(10, 0))
        self.progress.set(0)
        self.show_page("Overview")

    def build_sidebar(self):
        side = ctk.CTkFrame(self, width=205, corner_radius=0)
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)
        ctk.CTkLabel(side, text="◈  FILEWISE", font=ctk.CTkFont(size=23, weight="bold")).pack(
            anchor="w", padx=18, pady=(28, 3))
        ctk.CTkLabel(side, text="Smart File Organizer", text_color="gray60").pack(
            anchor="w", padx=18, pady=(0, 26))
        for name, icon in [("Overview", "▦"), ("Organize Files", "↗"),
                           ("Duplicate Finder", "⌕"), ("Operation History", "↶")]:
            ctk.CTkButton(side, text=f"{icon}  {name}", anchor="w", height=42,
                          fg_color="transparent", text_color=("gray15", "gray90"),
                          hover_color=("gray80", "gray25"),
                          command=lambda page=name: self.show_page(page)).pack(fill="x", padx=10, pady=3)
        ctk.CTkFrame(side, height=2, fg_color=("gray80", "gray30")).pack(fill="x", padx=14, pady=18)
        ctk.CTkButton(side, text="📂  Select folder", command=self.choose_folder).pack(fill="x", padx=12)
        ctk.CTkLabel(side, text="Your files stay on your device.\nDuplicates are never auto-deleted.",
                     justify="left", wraplength=165, text_color="gray60").pack(
            side="bottom", anchor="w", padx=16, pady=18)

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def show_page(self, page):
        self.page = page
        self.heading.configure(text=page)
        self.clear_content()
        if page == "Overview":
            self.page_overview()
        elif page == "Organize Files":
            self.page_organize()
        elif page == "Duplicate Finder":
            self.page_duplicates()
        else:
            self.page_history()

    def make_card(self, parent, title, value, subtitle, col):
        card = ctk.CTkFrame(parent, corner_radius=14)
        card.grid(row=0, column=col, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(card, text=title, text_color="gray60").pack(anchor="w", padx=14, pady=(14, 4))
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold"))
        value_label.pack(anchor="w", padx=14)
        ctk.CTkLabel(card, text=subtitle, text_color="gray60").pack(anchor="w", padx=14, pady=(3, 13))
        return value_label

    def page_overview(self):
        box = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        box.grid(row=0, column=0, sticky="nsew")
        cards = ctk.CTkFrame(box, fg_color="transparent")
        cards.pack(fill="x")
        cards.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")
        self.card_files = self.make_card(cards, "FILES SCANNED", "0", "Files in selected folder", 0)
        self.card_size = self.make_card(cards, "TOTAL SIZE", "0 B", "Combined file size", 1)
        self.card_dupes = self.make_card(cards, "DUPLICATE SPACE", "0 B", "Extra copies only", 2)

        folderbox = ctk.CTkFrame(box, corner_radius=14)
        folderbox.pack(fill="x", padx=5, pady=(12, 8))
        ctk.CTkLabel(folderbox, text="Selected workspace", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=16, pady=(14, 5))
        ctk.CTkLabel(folderbox, textvariable=self.folder_text, wraplength=800,
                     justify="left", text_color="gray60").pack(anchor="w", padx=16, pady=(0, 12))
        actions = ctk.CTkFrame(folderbox, fg_color="transparent")
        actions.pack(fill="x", padx=10, pady=(0, 12))
        ctk.CTkButton(actions, text="Scan folder", command=self.start_scan).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Export storage report", command=self.export_storage,
                      fg_color=("gray75", "gray25"), text_color=("gray10", "gray95")).pack(side="left", padx=4)
        breakdown = ctk.CTkFrame(box, corner_radius=14)
        breakdown.pack(fill="both", expand=True, padx=5, pady=8)
        ctk.CTkLabel(breakdown, text="File type breakdown", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=16, pady=(14, 6))
        self.breakdown = ctk.CTkTextbox(breakdown, height=230, wrap="none")
        self.breakdown.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.update_dashboard()

    def page_organize(self):
        box = ctk.CTkFrame(self.content, corner_radius=14)
        box.grid(row=0, column=0, sticky="nsew")
        box.grid_columnconfigure(0, weight=1)
        box.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(box, text="Preview before you move files",
                     font=ctk.CTkFont(size=17, weight="bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(15, 8))
        settings = ctk.CTkFrame(box, fg_color="transparent")
        settings.grid(row=1, column=0, sticky="ew", padx=12, pady=4)
        ctk.CTkLabel(settings, text="Organize by").pack(side="left", padx=4)
        ctk.CTkOptionMenu(settings, variable=self.mode,
                          values=["By file type", "By modification date", "Custom extensions"],
                          command=self.toggle_custom).pack(side="left", padx=6)
        self.custom_entry = ctk.CTkEntry(settings, textvariable=self.custom_extensions, width=235,
                                         placeholder_text=".pdf, .png, .jpg")
        self.custom_entry.pack(side="left", padx=6)
        self.toggle_custom()
        ctk.CTkLabel(box, text="Custom extensions go into a 'Custom' folder; unmatched files use their usual category.",
                     text_color="gray60", wraplength=800).grid(row=1, column=0, sticky="w", padx=16, pady=(42, 2))
        area = ctk.CTkFrame(box, fg_color="transparent")
        area.grid(row=2, column=0, sticky="nsew", padx=12, pady=6)
        area.grid_columnconfigure(0, weight=1)
        area.grid_rowconfigure(1, weight=1)
        toolbar = ctk.CTkFrame(area, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 7))
        ctk.CTkButton(toolbar, text="Preview changes", command=self.make_preview).pack(side="left", padx=3)
        ctk.CTkButton(toolbar, text="Apply moves", command=self.apply_moves,
                      fg_color="#167d55", hover_color="#116443").pack(side="left", padx=3)
        ctk.CTkButton(toolbar, text="Clear", command=self.clear_preview,
                      fg_color=("gray75", "gray25"), text_color=("gray10", "gray95")).pack(side="left", padx=3)
        self.preview_count = ctk.CTkLabel(toolbar, text="No preview", text_color="gray60")
        self.preview_count.pack(side="right", padx=6)
        self.preview_text = ctk.CTkTextbox(area, wrap="none")
        self.preview_text.grid(row=1, column=0, sticky="nsew")
        self.preview_text.insert("1.0", "Select a folder, scan it, then preview the proposed moves.")
        self.preview_text.configure(state="disabled")

    def toggle_custom(self, *_):
        if hasattr(self, "custom_entry"):
            self.custom_entry.configure(state="normal" if self.mode.get() == "Custom extensions" else "disabled")

    def page_duplicates(self):
        box = ctk.CTkFrame(self.content, corner_radius=14)
        box.grid(row=0, column=0, sticky="nsew")
        box.grid_columnconfigure(0, weight=1)
        box.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(box, text="SHA-256 duplicate finder", font=ctk.CTkFont(size=17, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=16, pady=(15, 5))
        toolbar = ctk.CTkFrame(box, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="e", padx=12, pady=(10, 4))
        ctk.CTkButton(toolbar, text="Scan duplicates", command=self.start_duplicate_scan).pack(side="left", padx=3)
        ctk.CTkButton(toolbar, text="Export report", command=self.export_duplicates,
                      fg_color=("gray75", "gray25"), text_color=("gray10", "gray95")).pack(side="left", padx=3)
        self.duplicate_summary = ctk.CTkLabel(box, text="Files are reported, never deleted automatically.",
                                              text_color="gray60")
        self.duplicate_summary.grid(row=0, column=0, sticky="w", padx=16, pady=(45, 0))
        self.duplicate_text = ctk.CTkTextbox(box, wrap="none")
        self.duplicate_text.grid(row=1, column=0, sticky="nsew", padx=12, pady=(12, 12))
        self.duplicate_text.insert("1.0", "Scan a folder first, then click Scan duplicates.")
        self.duplicate_text.configure(state="disabled")

    def page_history(self):
        box = ctk.CTkFrame(self.content, corner_radius=14)
        box.grid(row=0, column=0, sticky="nsew")
        box.grid_columnconfigure(0, weight=1)
        box.grid_rowconfigure(1, weight=1)
        top = ctk.CTkFrame(box, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        ctk.CTkLabel(top, text="File move history", font=ctk.CTkFont(size=17, weight="bold")).pack(side="left", padx=4)
        ctk.CTkButton(top, text="Undo latest operation", command=self.undo_latest,
                      fg_color="#9a5b18", hover_color="#75440f").pack(side="right", padx=4)
        ctk.CTkButton(top, text="Refresh", command=self.refresh_history,
                      fg_color=("gray75", "gray25"), text_color=("gray10", "gray95")).pack(side="right", padx=4)
        self.history_text = ctk.CTkTextbox(box, wrap="none")
        self.history_text.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.refresh_history()

    def choose_folder(self):
        choice = filedialog.askdirectory(title="Choose a folder to scan")
        if not choice:
            return
        self.folder = Path(choice).expanduser().resolve()
        self.folder_text.set(str(self.folder))
        self.files, self.duplicate_groups, self.preview = [], [], []
        self.status.set("Folder selected. Scan it to analyze files.")
        self.update_dashboard()
        if self.page == "Organize Files":
            self.clear_preview()
        if self.page == "Duplicate Finder":
            self.set_text(self.duplicate_text, "Folder changed. Scan for duplicates again.")

    def scan_folder(self, folder):
        records = []
        skip_dirs = {".git", ".venv", "venv", "__pycache__", "node_modules"}
        for root, dirs, names in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for name in names:
                path = Path(root) / name
                try:
                    if not path.is_file() or path.is_symlink():
                        continue
                    resolved = path.resolve()
                    if APP_DIR == resolved or APP_DIR in resolved.parents:
                        continue
                    stat = path.stat()
                    records.append({
                        "path": str(path), "name": path.name, "size": stat.st_size,
                        "mtime": stat.st_mtime, "extension": path.suffix.lower() or "[no extension]",
                        "category": category(path),
                    })
                except OSError:
                    continue
        return records

    def start_scan(self):
        if not self.folder:
            messagebox.showinfo("Choose a folder", "Select a folder first.")
            return
        if self.busy:
            return
        self.busy = True
        folder = self.folder
        self.status.set("Scanning folder…")
        self.progress.set(0.25)

        def worker():
            try:
                records = self.scan_folder(folder)
                self.after(0, lambda: self.scan_finished(folder, records))
            except Exception as exc:
                self.after(0, lambda msg=str(exc): self.scan_failed(msg))
        threading.Thread(target=worker, daemon=True).start()

    def scan_finished(self, folder, records):
        self.busy = False
        self.progress.set(1)
        if folder != self.folder:
            return
        self.files = records
        self.preview = []
        self.status.set(f"Scan complete: {len(records)} files found.")
        self.update_dashboard()
        if self.page == "Organize Files":
            self.clear_preview()
        if self.page == "Duplicate Finder":
            self.set_text(self.duplicate_text, "Scan updated. Click Scan duplicates.")
        self.after(1000, lambda: self.progress.set(0))

    def scan_failed(self, error):
        self.busy = False
        self.progress.set(0)
        messagebox.showerror("Scan failed", error)
        self.status.set("Scan failed.")

    def update_dashboard(self):
        if not hasattr(self, "card_files"):
            return
        total = sum(f["size"] for f in self.files)
        dup_space = sum(g[0]["size"] * (len(g) - 1) for g in self.duplicate_groups)
        self.card_files.configure(text=str(len(self.files)))
        self.card_size.configure(text=human_size(total))
        self.card_dupes.configure(text=human_size(dup_space))
        counts = defaultdict(lambda: [0, 0])
        for item in self.files:
            counts[item["category"]][0] += 1
            counts[item["category"]][1] += item["size"]
        lines = ["CATEGORY                 FILES      TOTAL SIZE", "-" * 52]
        if not self.files:
            lines.append("No files scanned yet.")
        else:
            for name, (num, size) in sorted(counts.items(), key=lambda item: item[1][1], reverse=True):
                lines.append(f"{name:<22} {num:>6}      {human_size(size):>10}")
            lines.append("-" * 52)
            lines.append(f"{'TOTAL':<22} {len(self.files):>6}      {human_size(total):>10}")
        if hasattr(self, "breakdown"):
            self.set_text(self.breakdown, "\n".join(lines))

    def target_category(self, path):
        mode = self.mode.get()
        if mode == "By modification date":
            date = datetime.fromtimestamp(path.stat().st_mtime)
            return f"{date.year}-{date.month:02d}"
        if mode == "Custom extensions":
            extensions = {x.strip().lower() for x in self.custom_extensions.get().split(",") if x.strip()}
            extensions = {x if x.startswith(".") else "." + x for x in extensions}
            return "Custom" if path.suffix.lower() in extensions else category(path)
        return category(path)

    def make_preview(self):
        if not self.folder:
            messagebox.showinfo("Choose a folder", "Select a folder first.")
            return
        if not self.files:
            messagebox.showinfo("Scan first", "Scan the folder before generating a preview.")
            return
        planned, skipped = [], 0
        for item in self.files:
            source = Path(item["path"])
            try:
                if not source.exists() or source.is_symlink():
                    skipped += 1
                    continue
                dest_dir = self.folder / self.target_category(source)
                if source.parent.resolve() == dest_dir.resolve() or dest_dir in source.parents:
                    skipped += 1
                    continue
                dest = safe_destination(dest_dir / source.name)
                planned.append({"source": str(source), "destination": str(dest), "size": item["size"]})
            except OSError:
                skipped += 1
        self.preview = planned
        lines = [f"Folder: {self.folder}", f"Mode: {self.mode.get()}",
                 f"Planned moves: {len(planned)} | Skipped: {skipped}", "", "=" * 88]
        for move in planned:
            lines += [move["source"], "  → " + move["destination"], f"  Size: {human_size(move['size'])}", ""]
        if not planned:
            lines.append("No moves needed for these settings.")
        self.set_text(self.preview_text, "\n".join(lines))
        self.preview_count.configure(text=f"{len(planned)} planned move(s)")
        self.status.set("Preview ready. Review all paths before applying.")

    def clear_preview(self):
        self.preview = []
        if hasattr(self, "preview_text"):
            self.set_text(self.preview_text, "Select a folder, scan it, then preview the proposed moves.")
            self.preview_count.configure(text="No preview")

    def apply_moves(self):
        if self.busy:
            return
        if not self.preview:
            messagebox.showinfo("No preview", "Generate and review a preview first.")
            return
        if not messagebox.askyesno("Confirm moves", f"Move {len(self.preview)} files?\n\n"
                "Files will not be deleted, and existing files will not be overwritten."):
            return
        op = {"id": str(uuid.uuid4()), "timestamp": datetime.now().isoformat(timespec="seconds"),
              "type": "organize", "root": str(self.folder), "moves": [], "undone": False}
        moved, skipped, errors = 0, 0, []
        for item in self.preview:
            src, planned_dest = Path(item["source"]), Path(item["destination"])
            try:
                if not src.exists() or src.is_symlink():
                    skipped += 1
                    continue
                planned_dest.parent.mkdir(parents=True, exist_ok=True)
                dest = safe_destination(planned_dest)
                shutil.move(str(src), str(dest))
                op["moves"].append({"source": str(src), "destination": str(dest), "size": item["size"]})
                moved += 1
            except (OSError, shutil.Error) as exc:
                errors.append(f"{src}: {exc}")
        if op["moves"]:
            self.operations.append(op)
            self.save_log()
        self.clear_preview()
        self.status.set(f"Moved {moved} file(s); skipped {skipped}.")
        if errors:
            messagebox.showwarning("Some moves failed", "\n".join(errors[:8]))
        else:
            messagebox.showinfo("Organization complete", f"Moved {moved} file(s). Skipped {skipped}.")
        self.start_scan()
        if self.page == "Operation History":
            self.refresh_history()

    def start_duplicate_scan(self):
        if not self.folder:
            messagebox.showinfo("Choose a folder", "Select a folder first.")
            return
        if self.busy:
            return
        if not self.files:
            messagebox.showinfo("Scan first", "Scan the folder from Overview first.")
            return
        self.busy = True
        self.status.set("Calculating SHA-256 hashes…")
        self.progress.set(0.2)
        records = list(self.files)

        def worker():
            size_groups = defaultdict(list)
            for item in records:
                size_groups[item["size"]].append(item)
            hashes = defaultdict(list)
            errors = []
            for size, items in size_groups.items():
                if len(items) < 2:
                    continue
                for item in items:
                    path = Path(item["path"])
                    try:
                        if path.is_file() and not path.is_symlink():
                            hashes[(size, file_hash(path))].append(item)
                    except OSError as exc:
                        errors.append(f"{path}: {exc}")
            groups = [group for group in hashes.values() if len(group) > 1]
            self.after(0, lambda: self.duplicates_finished(groups, errors))
        threading.Thread(target=worker, daemon=True).start()

    def duplicates_finished(self, groups, errors):
        self.busy = False
        self.progress.set(1)
        self.duplicate_groups = groups
        extra = sum(len(g) - 1 for g in groups)
        space = sum(g[0]["size"] * (len(g) - 1) for g in groups)
        lines = [f"Duplicate groups: {len(groups)}", f"Extra copies: {extra}",
                 f"Potential duplicate space: {human_size(space)}", "",
                 "Matching SHA-256 hashes indicate identical file contents.", "=" * 88]
        for number, group in enumerate(groups, 1):
            digest = file_hash(Path(group[0]["path"]))
            lines += [f"\nGROUP {number} — {human_size(group[0]['size'])} per file", f"SHA-256: {digest}"]
            lines.extend("  " + item["path"] for item in group)
        if not groups:
            lines.append("No duplicates found.")
        if errors:
            lines += ["", f"Could not read {len(errors)} file(s):"] + errors[:10]
        self.set_text(self.duplicate_text, "\n".join(lines))
        self.duplicate_summary.configure(text=f"{len(groups)} group(s) · {human_size(space)} possible savings")
        self.status.set(f"Duplicate scan complete: {len(groups)} group(s).")
        self.update_dashboard()
        self.after(1000, lambda: self.progress.set(0))

    def export_storage(self):
        if not self.files:
            messagebox.showinfo("No data", "Scan a folder before exporting a storage report.")
            return
        name = f"storage_report_{datetime.now():%Y%m%d_%H%M%S}.csv"
        target = filedialog.asksaveasfilename(defaultextension=".csv", initialdir=str(REPORT_DIR),
                                              initialfile=name, filetypes=[("CSV files", "*.csv")])
        if not target:
            return
        try:
            with open(target, "w", newline="", encoding="utf-8-sig") as stream:
                writer = csv.DictWriter(stream, fieldnames=["path", "name", "category", "extension",
                    "size_bytes", "size_readable", "modified"])
                writer.writeheader()
                for item in self.files:
                    writer.writerow({"path": item["path"], "name": item["name"], "category": item["category"],
                        "extension": item["extension"], "size_bytes": item["size"],
                        "size_readable": human_size(item["size"]),
                        "modified": datetime.fromtimestamp(item["mtime"]).isoformat(timespec="seconds")})
            messagebox.showinfo("Export complete", f"Storage report saved to:\n{target}")
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc))

    def export_duplicates(self):
        if not self.duplicate_groups:
            messagebox.showinfo("No data", "Run a duplicate scan first.")
            return
        name = f"duplicate_report_{datetime.now():%Y%m%d_%H%M%S}.csv"
        target = filedialog.asksaveasfilename(defaultextension=".csv", initialdir=str(REPORT_DIR),
                                              initialfile=name, filetypes=[("CSV files", "*.csv")])
        if not target:
            return
        try:
            with open(target, "w", newline="", encoding="utf-8-sig") as stream:
                writer = csv.writer(stream)
                writer.writerow(["group", "path", "size_bytes", "sha256"])
                for number, group in enumerate(self.duplicate_groups, 1):
                    digest = file_hash(Path(group[0]["path"]))
                    for item in group:
                        writer.writerow([number, item["path"], item["size"], digest])
            messagebox.showinfo("Export complete", f"Duplicate report saved to:\n{target}")
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc))

    def load_log(self):
        try:
            data = json.loads(LOG_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def save_log(self):
        temporary = LOG_FILE.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.operations, indent=2), encoding="utf-8")
        temporary.replace(LOG_FILE)

    def refresh_history(self):
        if not hasattr(self, "history_text"):
            return
        lines = ["Local operation log:", str(LOG_FILE), "=" * 88]
        if not self.operations:
            lines.append("No moves recorded yet.")
        for op in reversed(self.operations):
            lines += [f"\n[{ 'UNDONE' if op.get('undone') else 'ACTIVE' }] {op.get('timestamp', '')}",
                      f"Operation: {op.get('id', '')}", f"Folder: {op.get('root', '')}",
                      f"Moves: {len(op.get('moves', []))}"]
            for move in op.get("moves", [])[:100]:
                lines += ["  " + move["source"], "    → " + move["destination"]]
            if len(op.get("moves", [])) > 100:
                lines.append("  … more moves omitted from this view")
        self.set_text(self.history_text, "\n".join(lines))

    def undo_latest(self):
        op = next((x for x in reversed(self.operations) if not x.get("undone") and x.get("moves")), None)
        if not op:
            messagebox.showinfo("Nothing to undo", "No active move operation was found.")
            return
        if not messagebox.askyesno("Undo latest operation",
                f"Try to restore {len(op['moves'])} file(s) to original locations?\n"
                "Files will not overwrite existing files. Missing or conflicting files are skipped."):
            return
        restored, skipped, errors = 0, 0, []
        for move in reversed(op["moves"]):
            current, original = Path(move["destination"]), Path(move["source"])
            try:
                if not current.exists() or current.is_symlink() or original.exists():
                    skipped += 1
                    continue
                original.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(current), str(original))
                restored += 1
            except (OSError, shutil.Error) as exc:
                errors.append(f"{current}: {exc}")
        op["undone"] = restored == len(op["moves"])
        op["undo_timestamp"] = datetime.now().isoformat(timespec="seconds")
        op["undo_restored"], op["undo_skipped"] = restored, skipped
        self.save_log()
        self.refresh_history()
        self.status.set(f"Undo complete: restored {restored}, skipped {skipped}.")
        if self.folder:
            self.start_scan()
        result = f"Restored {restored} file(s). Skipped {skipped}."
        if errors:
            result += "\n\nErrors:\n" + "\n".join(errors[:8])
        messagebox.showinfo("Undo complete", result)

    @staticmethod
    def set_text(widget, text):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")


if __name__ == "__main__":
    app = FileOrganizer()
    app.mainloop()
