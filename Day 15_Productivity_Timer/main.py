import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, date
from pathlib import Path
import customtkinter as ctk

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "focusflow.db"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG = "#0B1020"
PANEL = "#141B2D"
PANEL_LIGHT = "#1B2540"
ACCENT = "#7C5CFC"
ACCENT_HOVER = "#6847EA"
GREEN = "#36C98F"
TEXT = "#F3F5FA"
MUTED = "#9AA6C0"
ORANGE = "#FFB454"
RED = "#FF6B78"


class FocusFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FocusFlow — Productivity Timer")
        self.geometry("1100x760")
        self.minsize(920, 680)
        self.configure(fg_color=BG)

        self.db = sqlite3.connect(DB_PATH)
        self.db.row_factory = sqlite3.Row
        self.init_db()

        self.work_minutes = 25
        self.short_break_minutes = 5
        self.long_break_minutes = 15
        self.sessions_before_long_break = 4
        self.current_mode = "Focus"
        self.remaining_seconds = self.work_minutes * 60
        self.timer_running = False
        self.timer_after_id = None
        self.session_count = self.today_completed_sessions()
        self.selected_task_id = None

        self.build_ui()
        self.refresh_tasks()
        self.refresh_stats()
        self.update_timer_display()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def init_db(self):
        with self.db:
            self.db.execute("""CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL)""")
            self.db.execute("""CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                task_id INTEGER,
                FOREIGN KEY(task_id) REFERENCES tasks(id))""")

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(22, 12))
        header.grid_columnconfigure(0, weight=1)
        title_wrap = ctk.CTkFrame(header, fg_color="transparent")
        title_wrap.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_wrap, text="FocusFlow", font=ctk.CTkFont(size=29, weight="bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(title_wrap, text="Make time for what matters.", font=ctk.CTkFont(size=13), text_color=MUTED).pack(anchor="w", pady=(2, 0))
        self.clock_label = ctk.CTkLabel(header, text="", font=ctk.CTkFont(size=13), text_color=MUTED)
        self.clock_label.grid(row=0, column=1, sticky="e")
        self.update_clock()

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 22))
        body.grid_columnconfigure((0, 1), weight=1, uniform="col")
        body.grid_rowconfigure(0, weight=1)
        left = ctk.CTkFrame(body, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(0, weight=3)
        left.grid_rowconfigure(1, weight=2)

        self.timer_card = ctk.CTkFrame(left, fg_color=PANEL, corner_radius=22)
        self.timer_card.grid(row=0, column=0, sticky="nsew", pady=(0, 14))
        mode_row = ctk.CTkFrame(self.timer_card, fg_color="transparent")
        mode_row.pack(pady=(24, 5))
        self.mode_buttons = {}
        for mode in ("Focus", "Short Break", "Long Break"):
            btn = ctk.CTkButton(mode_row, text=mode, width=112, height=34, corner_radius=10,
                                fg_color=ACCENT if mode == "Focus" else PANEL_LIGHT,
                                hover_color=ACCENT_HOVER, command=lambda m=mode: self.set_mode(m))
            btn.pack(side="left", padx=4)
            self.mode_buttons[mode] = btn
        self.timer_label = ctk.CTkLabel(self.timer_card, text="25:00", font=ctk.CTkFont(size=76, weight="bold"), text_color=TEXT)
        self.timer_label.pack(pady=(22, 0))
        self.timer_subtitle = ctk.CTkLabel(self.timer_card, text="One thing at a time.", font=ctk.CTkFont(size=14), text_color=MUTED)
        self.timer_subtitle.pack(pady=(0, 16))
        self.progress = ctk.CTkProgressBar(self.timer_card, height=8, corner_radius=5, progress_color=ACCENT, fg_color=PANEL_LIGHT)
        self.progress.pack(fill="x", padx=54, pady=(0, 20))
        self.progress.set(0)
        controls = ctk.CTkFrame(self.timer_card, fg_color="transparent")
        controls.pack(pady=(0, 18))
        self.start_button = ctk.CTkButton(controls, text="▶  Start Focus", width=160, height=45, corner_radius=13,
                                          fg_color=ACCENT, hover_color=ACCENT_HOVER, command=self.toggle_timer)
        self.start_button.pack(side="left", padx=6)
        ctk.CTkButton(controls, text="↻  Reset", width=105, height=45, corner_radius=13, fg_color=PANEL_LIGHT,
                      hover_color="#293656", command=self.reset_timer).pack(side="left", padx=6)
        ctk.CTkButton(controls, text="Skip", width=80, height=45, corner_radius=13, fg_color=PANEL_LIGHT,
                      hover_color="#293656", command=self.skip_timer).pack(side="left", padx=6)
        self.active_task_label = ctk.CTkLabel(self.timer_card, text="Current task: No task selected", font=ctk.CTkFont(size=12), text_color=MUTED)
        self.active_task_label.pack(pady=(0, 18))

        task_card = ctk.CTkFrame(left, fg_color=PANEL, corner_radius=22)
        task_card.grid(row=1, column=0, sticky="nsew")
        task_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(task_card, text="Today's tasks", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 12))
        add_row = ctk.CTkFrame(task_card, fg_color="transparent")
        add_row.grid(row=1, column=0, sticky="ew", padx=20)
        add_row.grid_columnconfigure(0, weight=1)
        self.task_entry = ctk.CTkEntry(add_row, placeholder_text="Add a task you want to focus on...", height=40, corner_radius=10)
        self.task_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.task_entry.bind("<Return>", lambda _event: self.add_task())
        ctk.CTkButton(add_row, text="+ Add", width=82, height=40, corner_radius=10, command=self.add_task).grid(row=0, column=1)
        self.task_list = ctk.CTkScrollableFrame(task_card, fg_color="transparent", corner_radius=10, height=160)
        self.task_list.grid(row=2, column=0, sticky="nsew", padx=12, pady=(10, 14))
        task_card.grid_rowconfigure(2, weight=1)

        right = ctk.CTkFrame(body, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)
        stats_card = ctk.CTkFrame(right, fg_color=PANEL, corner_radius=22)
        stats_card.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        ctk.CTkLabel(stats_card, text="Your progress", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT).pack(anchor="w", padx=20, pady=(18, 12))
        stats_grid = ctk.CTkFrame(stats_card, fg_color="transparent")
        stats_grid.pack(fill="x", padx=14, pady=(0, 16))
        stats_grid.grid_columnconfigure((0, 1), weight=1)
        self.stat_values = {}
        for index, (key, label, value, color) in enumerate([
            ("focus", "Focus minutes today", "0", ACCENT),
            ("sessions", "Sessions today", "0", GREEN),
            ("tasks", "Tasks completed", "0", ORANGE),
            ("goal", "Sessions toward break", "0 / 4", RED),
        ]):
            r, c = divmod(index, 2)
            tile = ctk.CTkFrame(stats_grid, fg_color=PANEL_LIGHT, corner_radius=14)
            tile.grid(row=r, column=c, sticky="ew", padx=5, pady=5)
            ctk.CTkLabel(tile, text=label, text_color=MUTED, font=ctk.CTkFont(size=11)).pack(anchor="w", padx=12, pady=(12, 4))
            val = ctk.CTkLabel(tile, text=value, text_color=color, font=ctk.CTkFont(size=24, weight="bold"))
            val.pack(anchor="w", padx=12, pady=(0, 12))
            self.stat_values[key] = val

        details = ctk.CTkFrame(right, fg_color=PANEL, corner_radius=22)
        details.grid(row=1, column=0, sticky="nsew")
        ctk.CTkLabel(details, text="Focus settings", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT).pack(anchor="w", padx=20, pady=(18, 12))
        settings = ctk.CTkFrame(details, fg_color="transparent")
        settings.pack(fill="x", padx=20)
        self.work_var = tk.StringVar(value="25")
        self.short_var = tk.StringVar(value="5")
        self.long_var = tk.StringVar(value="15")
        self.goal_var = tk.StringVar(value="4")
        for row, (label, variable) in enumerate([
            ("Focus (min)", self.work_var), ("Short break (min)", self.short_var),
            ("Long break (min)", self.long_var), ("Sessions per long break", self.goal_var)
        ]):
            ctk.CTkLabel(settings, text=label, text_color=MUTED, font=ctk.CTkFont(size=12)).grid(row=row, column=0, sticky="w", pady=5)
            ctk.CTkEntry(settings, textvariable=variable, width=75, height=32, corner_radius=8, justify="center").grid(row=row, column=1, sticky="e", pady=5)
        settings.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(details, text="Apply settings", height=38, corner_radius=10, command=self.apply_settings).pack(fill="x", padx=20, pady=(14, 18))
        tip = ctk.CTkFrame(details, fg_color=PANEL_LIGHT, corner_radius=14)
        tip.pack(fill="x", padx=20, pady=(0, 18))
        ctk.CTkLabel(tip, text="FOCUS TIP", text_color=ACCENT, font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=14, pady=(12, 4))
        ctk.CTkLabel(tip, text="Pick one clear task. Silence distractions.\nSmall focused sessions add up.", text_color=MUTED, justify="left", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=14, pady=(0, 12))

    def mode_duration(self, mode=None):
        mode = mode or self.current_mode
        return {"Focus": self.work_minutes, "Short Break": self.short_break_minutes, "Long Break": self.long_break_minutes}[mode]

    def set_mode(self, mode):
        if self.timer_running:
            self.pause_timer()
        self.current_mode = mode
        self.remaining_seconds = self.mode_duration() * 60
        self.update_mode_buttons()
        self.update_timer_display()
        self.timer_subtitle.configure(text="One thing at a time." if mode == "Focus" else "Recharge before the next round.")
        self.start_button.configure(text="▶  Start Focus" if mode == "Focus" else "▶  Start Break")

    def update_mode_buttons(self):
        for mode, button in self.mode_buttons.items():
            button.configure(fg_color=ACCENT if mode == self.current_mode else PANEL_LIGHT)

    def toggle_timer(self):
        if self.timer_running:
            self.pause_timer()
        else:
            self.timer_running = True
            self.start_button.configure(text="Ⅱ  Pause")
            self.timer_subtitle.configure(text="Stay with it. You've got this.")
            self.tick()

    def pause_timer(self):
        self.timer_running = False
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        self.start_button.configure(text="▶  Resume")
        self.timer_subtitle.configure(text="Paused — take a breath.")

    def reset_timer(self):
        self.timer_running = False
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        self.remaining_seconds = self.mode_duration() * 60
        self.start_button.configure(text="▶  Start Focus" if self.current_mode == "Focus" else "▶  Start Break")
        self.timer_subtitle.configure(text="One thing at a time.")
        self.update_timer_display()

    def skip_timer(self):
        if self.timer_running:
            self.pause_timer()
        self.set_mode("Short Break" if self.current_mode == "Focus" else "Focus")

    def tick(self):
        if not self.timer_running:
            return
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_timer_display()
            self.timer_after_id = self.after(1000, self.tick)
        else:
            self.complete_current_timer()

    def complete_current_timer(self):
        self.timer_running = False
        self.timer_after_id = None
        self.start_button.configure(text="▶  Start Focus" if self.current_mode == "Focus" else "▶  Start Break")
        self.bell()
        if self.current_mode == "Focus":
            with self.db:
                self.db.execute("INSERT INTO sessions (mode, duration_minutes, completed_at, task_id) VALUES (?, ?, ?, ?)",
                                ("Focus", self.mode_duration(), datetime.now().isoformat(timespec="seconds"), self.selected_task_id))
            self.refresh_stats()
            self.refresh_tasks()
            next_mode = "Long Break" if self.today_completed_sessions() % self.sessions_before_long_break == 0 else "Short Break"
            messagebox.showinfo("Focus session complete", "Great work! Your focus session has been saved.")
            self.set_mode(next_mode)
        else:
            messagebox.showinfo("Break complete", "Break's over. Ready for another focus session?")
            self.set_mode("Focus")

    def update_timer_display(self):
        mins, secs = divmod(max(0, self.remaining_seconds), 60)
        self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
        total = max(1, self.mode_duration() * 60)
        self.progress.set(1 - (self.remaining_seconds / total))
        self.title(f"FocusFlow — {mins:02d}:{secs:02d}")

    def apply_settings(self):
        try:
            work, short, long, goal = map(int, (self.work_var.get(), self.short_var.get(), self.long_var.get(), self.goal_var.get()))
            if not (1 <= work <= 180 and 1 <= short <= 60 and 1 <= long <= 90 and 1 <= goal <= 20):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid settings", "Enter whole numbers in these ranges:\nFocus 1–180, short break 1–60, long break 1–90, goal 1–20.")
            return
        self.work_minutes, self.short_break_minutes = work, short
        self.long_break_minutes, self.sessions_before_long_break = long, goal
        self.reset_timer()
        self.refresh_stats()
        messagebox.showinfo("Settings applied", "Your timer settings have been updated.")

    def add_task(self):
        title = self.task_entry.get().strip()
        if not title:
            return
        with self.db:
            cursor = self.db.execute("INSERT INTO tasks (title, created_at) VALUES (?, ?)", (title, datetime.now().isoformat(timespec="seconds")))
        self.task_entry.delete(0, "end")
        self.selected_task_id = cursor.lastrowid
        self.refresh_tasks()
        self.update_active_task()

    def refresh_tasks(self):
        for widget in self.task_list.winfo_children():
            widget.destroy()
        rows = self.db.execute("SELECT * FROM tasks ORDER BY done ASC, id DESC").fetchall()
        if not rows:
            ctk.CTkLabel(self.task_list, text="No tasks yet — add one above to get started.", text_color=MUTED, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=8, pady=12)
            self.update_active_task()
            return
        for row in rows:
            task_row = ctk.CTkFrame(self.task_list, fg_color=PANEL_LIGHT, corner_radius=10)
            task_row.pack(fill="x", padx=2, pady=4)
            var = tk.BooleanVar(value=bool(row["done"]))
            check = ctk.CTkCheckBox(task_row, text=row["title"], variable=var, onvalue=True, offvalue=False,
                                    text_color=MUTED if row["done"] else TEXT, checkbox_width=18, checkbox_height=18,
                                    command=lambda task_id=row["id"], v=var: self.toggle_task_done(task_id, v.get()))
            check.pack(side="left", fill="x", expand=True, padx=10, pady=10)
            if row["id"] == self.selected_task_id:
                ctk.CTkLabel(task_row, text="ACTIVE", text_color=GREEN, font=ctk.CTkFont(size=9, weight="bold")).pack(side="left", padx=5)
            ctk.CTkButton(task_row, text="Focus", width=58, height=28, corner_radius=8,
                          fg_color=ACCENT if row["id"] == self.selected_task_id else "#303B58", hover_color=ACCENT_HOVER,
                          command=lambda task_id=row["id"]: self.select_task(task_id)).pack(side="right", padx=8, pady=6)
        self.update_active_task()

    def toggle_task_done(self, task_id, done):
        with self.db:
            self.db.execute("UPDATE tasks SET done=? WHERE id=?", (int(done), task_id))
        self.refresh_tasks()
        self.refresh_stats()

    def select_task(self, task_id):
        self.selected_task_id = task_id
        self.refresh_tasks()
        self.update_active_task()

    def update_active_task(self):
        if not hasattr(self, "active_task_label"):
            return
        if self.selected_task_id is None:
            self.active_task_label.configure(text="Current task: No task selected")
            return
        row = self.db.execute("SELECT title FROM tasks WHERE id=?", (self.selected_task_id,)).fetchone()
        if row:
            self.active_task_label.configure(text=f"Current task: {row['title']}")
        else:
            self.selected_task_id = None
            self.active_task_label.configure(text="Current task: No task selected")

    def today_completed_sessions(self):
        today = date.today().isoformat()
        return self.db.execute("SELECT COUNT(*) AS n FROM sessions WHERE mode='Focus' AND substr(completed_at,1,10)=?", (today,)).fetchone()["n"]

    def refresh_stats(self):
        today = date.today().isoformat()
        focus = self.db.execute("SELECT COALESCE(SUM(duration_minutes),0) AS n FROM sessions WHERE mode='Focus' AND substr(completed_at,1,10)=?", (today,)).fetchone()["n"]
        sessions = self.today_completed_sessions()
        tasks_done = self.db.execute("SELECT COUNT(*) AS n FROM tasks WHERE done=1").fetchone()["n"]
        goal = getattr(self, "sessions_before_long_break", 4)
        self.stat_values["focus"].configure(text=str(focus))
        self.stat_values["sessions"].configure(text=str(sessions))
        self.stat_values["tasks"].configure(text=str(tasks_done))
        self.stat_values["goal"].configure(text=f"{min(sessions, goal)} / {goal}")
        self.session_count = sessions

    def update_clock(self):
        if self.winfo_exists():
            self.clock_label.configure(text=datetime.now().strftime("%a, %d %b  •  %I:%M %p"))
            self.after(30000, self.update_clock)

    def on_close(self):
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = FocusFlowApp()
    app.mainloop()
