import csv
import sqlite3
from datetime import date, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

APP_NAME = "HabitBloom"
DB_PATH = Path.home() / ".habitbloom" / "habits.db"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class HabitDatabase:
    def __init__(self, path=DB_PATH):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL DEFAULT 'General',
                    created_at TEXT NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS checkins (
                    habit_id INTEGER NOT NULL,
                    checkin_date TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 1,
                    PRIMARY KEY (habit_id, checkin_date),
                    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
                )
            """)

    def habits(self):
        return self.conn.execute("SELECT * FROM habits ORDER BY name COLLATE NOCASE").fetchall()

    def add(self, name, category):
        with self.conn:
            self.conn.execute(
                "INSERT INTO habits(name, category, created_at) VALUES (?, ?, ?)",
                (name.strip(), category.strip() or "General", date.today().isoformat())
            )

    def update(self, habit_id, name, category):
        with self.conn:
            self.conn.execute(
                "UPDATE habits SET name=?, category=? WHERE id=?",
                (name.strip(), category.strip() or "General", habit_id)
            )

    def delete(self, habit_id):
        with self.conn:
            self.conn.execute("DELETE FROM checkins WHERE habit_id=?", (habit_id,))
            self.conn.execute("DELETE FROM habits WHERE id=?", (habit_id,))

    def completed(self, habit_id, day):
        row = self.conn.execute(
            "SELECT completed FROM checkins WHERE habit_id=? AND checkin_date=?",
            (habit_id, day.isoformat())
        ).fetchone()
        return bool(row["completed"]) if row else False

    def set_completed(self, habit_id, day, value):
        with self.conn:
            if value:
                self.conn.execute(
                    """INSERT INTO checkins(habit_id, checkin_date, completed) VALUES (?, ?, 1)
                       ON CONFLICT(habit_id, checkin_date) DO UPDATE SET completed=1""",
                    (habit_id, day.isoformat())
                )
            else:
                self.conn.execute(
                    "DELETE FROM checkins WHERE habit_id=? AND checkin_date=?",
                    (habit_id, day.isoformat())
                )

    def dates(self, habit_id):
        rows = self.conn.execute(
            "SELECT checkin_date FROM checkins WHERE habit_id=? AND completed=1",
            (habit_id,)
        ).fetchall()
        return {date.fromisoformat(row["checkin_date"]) for row in rows}

    def rows_between(self, start, end):
        return self.conn.execute("""
            SELECT h.name, h.category, c.checkin_date
            FROM checkins c JOIN habits h ON h.id=c.habit_id
            WHERE c.completed=1 AND c.checkin_date BETWEEN ? AND ?
            ORDER BY c.checkin_date, h.name
        """, (start.isoformat(), end.isoformat())).fetchall()

    def close(self):
        self.conn.close()


class HabitBloomApp(ctk.CTk):
    BG = "#0b1220"
    PANEL = "#121c2d"
    PANEL2 = "#1b2940"
    ACCENT = "#8b7cff"
    GREEN = "#42d6a4"
    TEXT = "#f4f7fb"
    MUTED = "#9aa8bd"

    def __init__(self):
        super().__init__()
        self.title("HabitBloom | Habit & Wellness Tracker")
        self.geometry("1160x760")
        self.minsize(940, 650)
        self.configure(fg_color=self.BG)
        self.db = HabitDatabase()
        self.selected_day = date.today()
        self.page = "Dashboard"
        self.chart = None
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.build_ui()
        self.refresh()

    def build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        sidebar = ctk.CTkFrame(self, width=215, corner_radius=0, fg_color="#0e1727")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        ctk.CTkLabel(sidebar, text="✦ HabitBloom", text_color=self.TEXT,
                     font=ctk.CTkFont(size=25, weight="bold")).pack(anchor="w", padx=20, pady=(28, 4))
        ctk.CTkLabel(sidebar, text="SMALL STEPS, REAL PROGRESS", text_color=self.MUTED,
                     font=ctk.CTkFont(size=9, weight="bold")).pack(anchor="w", padx=21, pady=(0, 30))
        self.nav = {}
        for name in ("Dashboard", "My Habits", "Insights", "Reports"):
            b = ctk.CTkButton(
                sidebar, text="   " + name, anchor="w", height=43, corner_radius=10,
                fg_color=self.ACCENT if name == self.page else "transparent",
                hover_color=self.PANEL2, command=lambda p=name: self.change_page(p)
            )
            b.pack(fill="x", padx=12, pady=4)
            self.nav[name] = b
        ctk.CTkFrame(sidebar, height=1, fg_color="#263248").pack(fill="x", padx=18, pady=(28, 15))
        ctk.CTkLabel(sidebar, text="A DAILY REMINDER", text_color=self.MUTED,
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=21)
        ctk.CTkLabel(sidebar, text="Consistency beats\nperfection. 🌱", text_color=self.TEXT,
                     justify="left", font=ctk.CTkFont(size=15)).pack(anchor="w", padx=21, pady=10)

        main = ctk.CTkFrame(self, fg_color=self.BG, corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew", padx=24, pady=20)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.grid_columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(header, text="Your Daily Growth", text_color=self.TEXT,
                                        font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.grid(row=0, column=0, sticky="w")
        self.date_label = ctk.CTkLabel(header, text="", text_color=self.MUTED)
        self.date_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
        ctk.CTkButton(header, text="+ Add Habit", width=125, height=38, fg_color=self.ACCENT,
                      hover_color="#7667ec", command=self.add_dialog).grid(row=0, column=1, rowspan=2)
        self.content = ctk.CTkScrollableFrame(main, fg_color="transparent", corner_radius=0)
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)

    def change_page(self, page):
        self.page = page
        for name, button in self.nav.items():
            button.configure(fg_color=self.ACCENT if name == page else "transparent")
        self.title_label.configure(text={
            "Dashboard": "Your Daily Growth", "My Habits": "Manage Your Habits",
            "Insights": "Your Consistency", "Reports": "Personal Summary"
        }[page])
        self.refresh()

    def clear(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def card(self, parent, title, value, note, color=None):
        box = ctk.CTkFrame(parent, fg_color=self.PANEL, corner_radius=15)
        ctk.CTkLabel(box, text=title.upper(), text_color=self.MUTED,
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=16, pady=(15, 6))
        ctk.CTkLabel(box, text=value, text_color=color or self.TEXT,
                     font=ctk.CTkFont(size=27, weight="bold")).pack(anchor="w", padx=16)
        ctk.CTkLabel(box, text=note, text_color=self.MUTED,
                     font=ctk.CTkFont(size=11)).pack(anchor="w", padx=16, pady=(4, 15))
        return box

    def refresh(self):
        self.date_label.configure(text=self.selected_day.strftime("%A, %B %d, %Y"))
        self.clear()
        {"Dashboard": self.render_dashboard, "My Habits": self.render_habits,
         "Insights": self.render_insights, "Reports": self.render_reports}[self.page]()

    def render_dashboard(self):
        habits = self.db.habits()
        done = sum(self.db.completed(h["id"], self.selected_day) for h in habits)
        percent = round(done / len(habits) * 100) if habits else 0
        week_start = self.selected_day - timedelta(days=self.selected_day.weekday())
        week_done = len(self.db.rows_between(week_start, self.selected_day))
        stats = ctk.CTkFrame(self.content, fg_color="transparent")
        stats.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        for i in range(3):
            stats.grid_columnconfigure(i, weight=1)
        self.card(stats, "Today's progress", f"{percent}%", f"{done} of {len(habits)} habits complete", self.GREEN).grid(row=0, column=0, sticky="ew", padx=(0, 7))
        self.card(stats, "Active habits", str(len(habits)), "Routines you're building").grid(row=0, column=1, sticky="ew", padx=7)
        self.card(stats, "Check-ins this week", str(week_done), "Since Monday", self.ACCENT).grid(row=0, column=2, sticky="ew", padx=(7, 0))

        top = ctk.CTkFrame(self.content, fg_color="transparent")
        top.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top, text="Daily check-ins", text_color=self.TEXT,
                     font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, sticky="w")
        controls = ctk.CTkFrame(top, fg_color="transparent")
        controls.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(controls, text="‹", width=35, fg_color=self.PANEL2,
                      command=lambda: self.shift_day(-1)).pack(side="left", padx=2)
        ctk.CTkButton(controls, text="Today", width=58, fg_color=self.PANEL2,
                      command=self.today).pack(side="left", padx=2)
        ctk.CTkButton(controls, text="›", width=35, fg_color=self.PANEL2,
                      command=lambda: self.shift_day(1)).pack(side="left", padx=2)

        box = ctk.CTkFrame(self.content, fg_color=self.PANEL, corner_radius=15)
        box.grid(row=2, column=0, sticky="ew")
        if not habits:
            ctk.CTkLabel(box, text="No habits yet — click + Add Habit to start 🌱",
                         text_color=self.MUTED).pack(padx=20, pady=35)
        for h in habits:
            row = ctk.CTkFrame(box, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=6)
            var = tk.BooleanVar(value=self.db.completed(h["id"], self.selected_day))
            ctk.CTkCheckBox(row, text="", variable=var, width=25, checkbox_width=23,
                            checkbox_height=23, fg_color=self.GREEN,
                            command=lambda hid=h["id"], v=var: self.checkin(hid, v.get())).pack(side="left", padx=(5, 10), pady=8)
            text_box = ctk.CTkFrame(row, fg_color="transparent")
            text_box.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(text_box, text=h["name"], text_color=self.TEXT,
                         font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(text_box, text=h["category"], text_color=self.MUTED,
                         font=ctk.CTkFont(size=11)).pack(anchor="w")
            ctk.CTkLabel(row, text=f"🔥 {self.current_streak(h['id'])} day streak",
                         text_color="#ffc875").pack(side="right", padx=12)

    def render_habits(self):
        ctk.CTkLabel(self.content, text="Create and manage your routines.",
                     text_color=self.MUTED).grid(row=0, column=0, sticky="w", pady=(0, 12))
        habits = self.db.habits()
        for h in habits:
            row = ctk.CTkFrame(self.content, fg_color=self.PANEL, corner_radius=14)
            row.grid(sticky="ew", pady=5)
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(row, text=h["name"], text_color=self.TEXT,
                         font=ctk.CTkFont(size=15, weight="bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 2))
            ctk.CTkLabel(row, text=f'{h["category"]} • Current streak: {self.current_streak(h["id"])} days',
                         text_color=self.MUTED).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))
            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=1, rowspan=2, padx=10)
            ctk.CTkButton(actions, text="Edit", width=58, fg_color=self.PANEL2,
                          command=lambda item=h: self.habit_dialog(item)).pack(side="left", padx=3)
            ctk.CTkButton(actions, text="Delete", width=65, fg_color="#592b3b",
                          hover_color="#7c344b", command=lambda item=h: self.delete_habit(item)).pack(side="left", padx=3)
        if not habits:
            ctk.CTkLabel(self.content, text="Your habit list is empty.",
                         text_color=self.MUTED).grid(row=1, column=0, sticky="w")

    def render_insights(self):
        habits = self.db.habits()
        if not habits:
            ctk.CTkLabel(self.content, text="Add habits to start viewing your insights.",
                         text_color=self.MUTED).grid(row=0, column=0, sticky="w")
            return
        end = self.selected_day
        start = end - timedelta(days=6)
        done = len(self.db.rows_between(start, end))
        possible = len(habits) * 7
        rate = round(done / possible * 100) if possible else 0
        top = ctk.CTkFrame(self.content, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        top.grid_columnconfigure((0, 1), weight=1)
        self.card(top, "7-day completion", f"{rate}%", f"{done} of {possible} possible check-ins", self.GREEN).grid(row=0, column=0, sticky="ew", padx=(0, 7))
        best = max((self.longest_streak(h["id"]) for h in habits), default=0)
        self.card(top, "Longest streak", f"{best} days", "Best streak across all habits", "#ffc875").grid(row=0, column=1, sticky="ew", padx=(7, 0))

        chart_box = ctk.CTkFrame(self.content, fg_color=self.PANEL, corner_radius=15)
        chart_box.grid(row=1, column=0, sticky="ew")
        fig = Figure(figsize=(8, 3.2), dpi=100, facecolor=self.PANEL)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.PANEL)
        days = [end - timedelta(days=i) for i in range(6, -1, -1)]
        values = [sum(self.db.completed(h["id"], d) for h in habits) for d in days]
        ax.bar([d.strftime("%a") for d in days], values, color=self.ACCENT, width=.58)
        ax.set_ylim(0, max(1, len(habits)) * 1.15)
        ax.set_ylabel("Completed habits", color=self.MUTED)
        ax.tick_params(colors=self.MUTED)
        for spine in ax.spines.values():
            spine.set_color("#2a3850")
        ax.grid(axis="y", alpha=.15)
        ax.set_axisbelow(True)
        fig.tight_layout(pad=2)
        self.chart = FigureCanvasTkAgg(fig, master=chart_box)
        self.chart.draw()
        self.chart.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(self.content, text="Habit streaks", text_color=self.TEXT,
                     font=ctk.CTkFont(size=18, weight="bold")).grid(row=2, column=0, sticky="w", pady=(18, 8))
        for h in habits:
            dates = self.db.dates(h["id"])
            line = ctk.CTkFrame(self.content, fg_color=self.PANEL, corner_radius=12)
            line.grid(sticky="ew", pady=4)
            ctk.CTkLabel(line, text=h["name"], text_color=self.TEXT,
                         font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=14, pady=12)
            ctk.CTkLabel(line, text=f"{len(dates)} check-ins • 🔥 {self.current_streak(h['id'])} current • 🏆 {self.longest_streak(h['id'])} best",
                         text_color=self.MUTED).pack(side="right", padx=14)

    def render_reports(self):
        ctk.CTkLabel(self.content, text="Export check-in history and habit statistics to a CSV file.",
                     text_color=self.MUTED).grid(row=0, column=0, sticky="w", pady=(0, 15))
        panel = ctk.CTkFrame(self.content, fg_color=self.PANEL, corner_radius=15)
        panel.grid(row=1, column=0, sticky="ew")
        ctk.CTkLabel(panel, text="Report date range", text_color=self.TEXT,
                     font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(20, 12))
        inputs = ctk.CTkFrame(panel, fg_color="transparent")
        inputs.pack(anchor="w", padx=20, pady=(0, 15))
        ctk.CTkLabel(inputs, text="Start date (YYYY-MM-DD)", text_color=self.MUTED).grid(row=0, column=0, sticky="w", padx=(0, 15))
        ctk.CTkLabel(inputs, text="End date (YYYY-MM-DD)", text_color=self.MUTED).grid(row=0, column=1, sticky="w")
        self.start_entry = ctk.CTkEntry(inputs, width=165)
        self.end_entry = ctk.CTkEntry(inputs, width=165)
        self.start_entry.grid(row=1, column=0, padx=(0, 15), pady=(5, 0))
        self.end_entry.grid(row=1, column=1, pady=(5, 0))
        self.start_entry.insert(0, (date.today() - timedelta(days=6)).isoformat())
        self.end_entry.insert(0, date.today().isoformat())
        ctk.CTkButton(panel, text="Export CSV Summary", height=40, fg_color=self.ACCENT,
                      command=self.export_csv).pack(anchor="w", padx=20, pady=(0, 20))
        info = ctk.CTkFrame(self.content, fg_color=self.PANEL, corner_radius=15)
        info.grid(row=2, column=0, sticky="ew", pady=14)
        ctk.CTkLabel(info, text="Your report includes", text_color=self.TEXT,
                     font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=20, pady=(16, 6))
        ctk.CTkLabel(info, text="• Habit name and category\n• Completions within the selected period\n• Current and longest streaks\n• Individual check-in dates",
                     text_color=self.MUTED, justify="left").pack(anchor="w", padx=20, pady=(0, 16))

    def habit_dialog(self, habit=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Habit" if habit else "Add Habit")
        dialog.geometry("390x310")
        dialog.resizable(False, False)
        dialog.configure(fg_color=self.BG)
        dialog.transient(self)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text="Edit your habit" if habit else "Create a new habit",
                     text_color=self.TEXT, font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=25, pady=(24, 16))
        ctk.CTkLabel(dialog, text="Habit name", text_color=self.MUTED).pack(anchor="w", padx=25)
        name = ctk.CTkEntry(dialog, placeholder_text="e.g. Read for 20 minutes", height=38)
        name.pack(fill="x", padx=25, pady=(5, 12))
        ctk.CTkLabel(dialog, text="Category", text_color=self.MUTED).pack(anchor="w", padx=25)
        category = ctk.CTkEntry(dialog, placeholder_text="e.g. Wellness, Learning, Fitness", height=38)
        category.pack(fill="x", padx=25, pady=(5, 16))
        if habit:
            name.insert(0, habit["name"])
            category.insert(0, habit["category"])

        def save():
            n, cat = name.get().strip(), category.get().strip() or "General"
            if not n:
                messagebox.showwarning("Missing name", "Please enter a habit name.", parent=dialog)
                return
            try:
                self.db.update(habit["id"], n, cat) if habit else self.db.add(n, cat)
            except sqlite3.IntegrityError:
                messagebox.showerror("Duplicate habit", "A habit with this name already exists.", parent=dialog)
                return
            dialog.destroy()
            self.refresh()

        ctk.CTkButton(dialog, text="Save Habit", height=40, fg_color=self.ACCENT,
                      command=save).pack(fill="x", padx=25)
        name.focus_set()

    def add_dialog(self):
        self.habit_dialog()

    def delete_habit(self, habit):
        if messagebox.askyesno("Delete habit", f'Delete "{habit["name"]}" and all its check-ins?', parent=self):
            self.db.delete(habit["id"])
            self.refresh()

    def checkin(self, habit_id, value):
        self.db.set_completed(habit_id, self.selected_day, value)
        self.refresh()

    def current_streak(self, habit_id):
        dates = self.db.dates(habit_id)
        cursor = date.today() if date.today() in dates else date.today() - timedelta(days=1)
        if cursor not in dates:
            return 0
        streak = 0
        while cursor in dates:
            streak += 1
            cursor -= timedelta(days=1)
        return streak

    def longest_streak(self, habit_id):
        longest = current = 0
        previous = None
        for day in sorted(self.db.dates(habit_id)):
            current = current + 1 if previous and day == previous + timedelta(days=1) else 1
            longest = max(longest, current)
            previous = day
        return longest

    def shift_day(self, offset):
        self.selected_day += timedelta(days=offset)
        self.refresh()

    def today(self):
        self.selected_day = date.today()
        self.refresh()

    def export_csv(self):
        try:
            start = date.fromisoformat(self.start_entry.get().strip())
            end = date.fromisoformat(self.end_entry.get().strip())
        except ValueError:
            messagebox.showerror("Invalid date", "Use YYYY-MM-DD format.", parent=self)
            return
        if start > end:
            messagebox.showerror("Invalid range", "Start date must not be after end date.", parent=self)
            return
        path = filedialog.asksaveasfilename(
            parent=self, title="Save habit report", defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"habit_summary_{start}_{end}.csv"
        )
        if not path:
            return
        rows = self.db.rows_between(start, end)
        counts = {}
        for row in rows:
            counts[row["name"]] = counts.get(row["name"], 0) + 1
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(["HabitBloom - Habit & Wellness Summary"])
                writer.writerow(["Period", start.isoformat(), "to", end.isoformat()])
                writer.writerow([])
                writer.writerow(["Habit", "Category", "Completions in Period", "Current Streak", "Longest Streak"])
                for h in self.db.habits():
                    writer.writerow([h["name"], h["category"], counts.get(h["name"], 0),
                                     self.current_streak(h["id"]), self.longest_streak(h["id"])])
                writer.writerow([])
                writer.writerow(["Check-in Details"])
                writer.writerow(["Date", "Habit", "Category"])
                for row in rows:
                    writer.writerow([row["checkin_date"], row["name"], row["category"]])
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc), parent=self)
            return
        messagebox.showinfo("Export complete", f"Report saved to:\n{path}", parent=self)

    def close_app(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = HabitBloomApp()
    app.mainloop()
