
import csv
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import date, datetime
from pathlib import Path

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# -------------------- CONFIGURATION --------------------

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "expenses.db"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG = "#0B1020"
PANEL = "#141B2D"
PANEL_LIGHT = "#1B2540"
ACCENT = "#7C5CFC"
GREEN = "#36C98F"
RED = "#FF6B78"
ORANGE = "#FFB454"
TEXT = "#F3F5FA"
MUTED = "#9AA6C0"

CATEGORIES = [
    "Food", "Transport", "Shopping", "Bills",
    "Education", "Health", "Entertainment",
    "Travel", "Salary", "Freelance", "Other"
]


class PennyWise(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("PennyWise - Expense Manager")
        self.geometry("1180x780")
        self.minsize(950, 650)
        self.configure(fg_color=BG)

        self.db = sqlite3.connect(DB_PATH)
        self.db.row_factory = sqlite3.Row

        self.initialize_database()

        self.selected_month = date.today().strftime("%Y-%m")
        self.transaction_vars = {}

        self.build_ui()
        self.refresh_all()

        self.protocol("WM_DELETE_WINDOW", self.close_app)

    # -------------------- DATABASE --------------------

    def initialize_database(self):
        with self.db:
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    note TEXT DEFAULT '',
                    transaction_date TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            self.db.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    month TEXT PRIMARY KEY,
                    amount REAL NOT NULL
                )
            """)

    # -------------------- USER INTERFACE --------------------

    def build_ui(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(
            row=0, column=0, sticky="ew",
            padx=25, pady=(20, 12)
        )
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="PennyWise 💸",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=TEXT
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="A clearer picture of your money.",
            text_color=MUTED
        ).grid(row=1, column=0, sticky="w")

        self.month_label = ctk.CTkLabel(
            header, text="", text_color=MUTED
        )
        self.month_label.grid(row=0, column=1, rowspan=2)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(
            row=1, column=0, sticky="nsew",
            padx=25, pady=(0, 20)
        )

        main.grid_columnconfigure(0, weight=3, uniform="main")
        main.grid_columnconfigure(1, weight=2, uniform="main")
        main.grid_rowconfigure(1, weight=1)

        # Summary cards
        summary = ctk.CTkFrame(main, fg_color="transparent")
        summary.grid(
            row=0, column=0, columnspan=2,
            sticky="ew", pady=(0, 14)
        )

        for col in range(4):
            summary.grid_columnconfigure(col, weight=1)

        self.summary_values = {}

        cards = [
            ("income", "Monthly Income", "₹0.00", GREEN),
            ("expenses", "Monthly Expenses", "₹0.00", RED),
            ("balance", "Net Balance", "₹0.00", ACCENT),
            ("budget", "Budget Remaining", "Not set", ORANGE)
        ]

        for i, (key, title, value, color) in enumerate(cards):

            card = ctk.CTkFrame(
                summary, fg_color=PANEL, corner_radius=15
            )
            card.grid(
                row=0, column=i, sticky="ew",
                padx=(0 if i == 0 else 5, 5 if i < 3 else 0)
            )

            ctk.CTkLabel(
                card, text=title, text_color=MUTED,
                font=ctk.CTkFont(size=11)
            ).pack(anchor="w", padx=12, pady=(13, 5))

            value_label = ctk.CTkLabel(
                card, text=value, text_color=color,
                font=ctk.CTkFont(size=20, weight="bold")
            )
            value_label.pack(anchor="w", padx=12, pady=(0, 13))

            self.summary_values[key] = value_label

        # Left column
        left = ctk.CTkFrame(main, fg_color="transparent")
        left.grid(
            row=1, column=0, sticky="nsew",
            padx=(0, 10)
        )
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)

        self.build_add_transaction(left)
        self.build_transaction_history(left)

        # Right column
        right = ctk.CTkFrame(main, fg_color="transparent")
        right.grid(
            row=1, column=1, sticky="nsew",
            padx=(10, 0)
        )
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        self.build_budget(right)
        self.build_chart(right)

    def build_add_transaction(self, parent):

        card = ctk.CTkFrame(
            parent, fg_color=PANEL, corner_radius=18
        )
        card.grid(row=0, column=0, sticky="ew", pady=(0, 14))

        ctk.CTkLabel(
            card, text="Add a transaction",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT
        ).grid(
            row=0, column=0, columnspan=2,
            sticky="w", padx=18, pady=(16, 12)
        )

        self.kind_var = tk.StringVar(value="Expense")
        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Food")
        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.note_var = tk.StringVar()

        ctk.CTkSegmentedButton(
            card,
            values=["Expense", "Income"],
            variable=self.kind_var,
            selected_color=ACCENT
        ).grid(
            row=1, column=0, columnspan=2,
            sticky="ew", padx=18, pady=(0, 12)
        )

        ctk.CTkLabel(
            card, text="Amount (₹)", text_color=MUTED
        ).grid(row=2, column=0, sticky="w", padx=18)

        ctk.CTkLabel(
            card, text="Category", text_color=MUTED
        ).grid(row=2, column=1, sticky="w", padx=8)

        ctk.CTkEntry(
            card, textvariable=self.amount_var,
            placeholder_text="e.g. 250.00", height=38
        ).grid(
            row=3, column=0, sticky="ew",
            padx=(18, 8), pady=(4, 10)
        )

        ctk.CTkOptionMenu(
            card, variable=self.category_var,
            values=CATEGORIES, height=38,
            fg_color=PANEL_LIGHT
        ).grid(
            row=3, column=1, sticky="ew",
            padx=(0, 18), pady=(4, 10)
        )

        ctk.CTkLabel(
            card, text="Date (YYYY-MM-DD)", text_color=MUTED
        ).grid(row=4, column=0, sticky="w", padx=18)

        ctk.CTkLabel(
            card, text="Note (optional)", text_color=MUTED
        ).grid(row=4, column=1, sticky="w", padx=8)

        ctk.CTkEntry(
            card, textvariable=self.date_var, height=38
        ).grid(
            row=5, column=0, sticky="ew",
            padx=(18, 8), pady=(4, 12)
        )

        ctk.CTkEntry(
            card, textvariable=self.note_var,
            placeholder_text="What was it for?", height=38
        ).grid(
            row=5, column=1, sticky="ew",
            padx=(0, 18), pady=(4, 12)
        )

        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            card, text="+ Save transaction",
            height=40, fg_color=ACCENT,
            command=self.add_transaction
        ).grid(
            row=6, column=0, columnspan=2,
            sticky="ew", padx=18, pady=(0, 17)
        )

    def build_transaction_history(self, parent):

        card = ctk.CTkFrame(
            parent, fg_color=PANEL, corner_radius=18
        )
        card.grid(row=1, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=16, pady=14)
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top, text="Transactions",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            top, text="Export CSV", width=95, height=30,
            command=self.export_csv
        ).grid(row=0, column=1, padx=4)

        ctk.CTkButton(
            top, text="Delete selected", width=120, height=30,
            fg_color="#702C40", hover_color="#8C3550",
            command=self.delete_selected
        ).grid(row=0, column=2, padx=4)

        filter_row = ctk.CTkFrame(card, fg_color="transparent")
        filter_row.grid(
            row=1, column=0, sticky="ew",
            padx=16, pady=(0, 8)
        )

        ctk.CTkLabel(
            filter_row, text="Filter:", text_color=MUTED
        ).pack(side="left", padx=(0, 8))

        self.filter_var = tk.StringVar(value="All")

        ctk.CTkOptionMenu(
            filter_row, variable=self.filter_var,
            values=["All", "Expense", "Income"],
            width=120, height=30,
            command=lambda _value: self.refresh_transactions()
        ).pack(side="left")

        self.transactions_frame = ctk.CTkScrollableFrame(
            card, fg_color="transparent"
        )
        self.transactions_frame.grid(
            row=2, column=0, sticky="nsew",
            padx=10, pady=(0, 12)
        )

    def build_budget(self, parent):

        card = ctk.CTkFrame(
            parent, fg_color=PANEL, corner_radius=18
        )
        card.grid(row=0, column=0, sticky="ew", pady=(0, 14))

        ctk.CTkLabel(
            card, text="Monthly budget",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=18, pady=(16, 10))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=18)

        self.budget_var = tk.StringVar()

        ctk.CTkEntry(
            row, textvariable=self.budget_var,
            placeholder_text="Budget in ₹", height=38
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            row, text="Save", width=70, height=38,
            command=self.save_budget
        ).pack(side="right")

        self.budget_progress = ctk.CTkProgressBar(
            card, height=8, progress_color=GREEN
        )
        self.budget_progress.pack(
            fill="x", padx=18, pady=(14, 5)
        )

        self.budget_status = ctk.CTkLabel(
            card, text="Set a monthly spending limit.",
            text_color=MUTED, font=ctk.CTkFont(size=12)
        )
        self.budget_status.pack(
            anchor="w", padx=18, pady=(0, 16)
        )

    def build_chart(self, parent):

        card = ctk.CTkFrame(
            parent, fg_color=PANEL, corner_radius=18
        )
        card.grid(row=1, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            card, text="Spending by category",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=18, pady=14)

        self.chart_holder = ctk.CTkFrame(
            card, fg_color="transparent"
        )
        self.chart_holder.grid(
            row=1, column=0, sticky="nsew",
            padx=8, pady=(0, 8)
        )

        self.chart_note = ctk.CTkLabel(
            card, text="Add expenses to see your breakdown.",
            text_color=MUTED, font=ctk.CTkFont(size=12)
        )
        self.chart_note.grid(
            row=2, column=0, sticky="w",
            padx=18, pady=(0, 14)
        )

    # -------------------- TRANSACTIONS --------------------

    def add_transaction(self):

        try:
            amount = float(self.amount_var.get().strip())

            if amount <= 0:
                raise ValueError

            tx_date = datetime.strptime(
                self.date_var.get().strip(), "%Y-%m-%d"
            ).date()

        except ValueError:
            messagebox.showerror(
                "Invalid input",
                "Enter a positive amount and a valid date in YYYY-MM-DD format."
            )
            return

        kind = self.kind_var.get()
        category = self.category_var.get()
        note = self.note_var.get().strip()

        if kind == "Income" and category not in (
            "Salary", "Freelance", "Other"
        ):
            category = "Salary" if category == "Food" else "Other"

        with self.db:
            self.db.execute(
                """
                INSERT INTO transactions
                (kind, amount, category, note,
                 transaction_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    kind, amount, category, note,
                    tx_date.isoformat(),
                    datetime.now().isoformat(timespec="seconds")
                )
            )

        self.amount_var.set("")
        self.note_var.set("")
        self.selected_month = tx_date.strftime("%Y-%m")

        self.refresh_all()

    def month_totals(self):

        rows = self.db.execute(
            """
            SELECT kind, SUM(amount) AS total
            FROM transactions
            WHERE substr(transaction_date, 1, 7) = ?
            GROUP BY kind
            """,
            (self.selected_month,)
        ).fetchall()

        totals = {"Income": 0.0, "Expense": 0.0}

        for row in rows:
            totals[row["kind"]] = row["total"] or 0.0

        return totals

    # -------------------- BUDGET --------------------

    def get_budget(self):

        row = self.db.execute(
            "SELECT amount FROM budgets WHERE month = ?",
            (self.selected_month,)
        ).fetchone()

        return row["amount"] if row else 0.0

    def save_budget(self):

        try:
            amount = float(self.budget_var.get().strip())

            if amount < 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid budget",
                "Enter a valid budget amount greater than or equal to zero."
            )
            return

        with self.db:
            self.db.execute(
                """
                INSERT INTO budgets (month, amount)
                VALUES (?, ?)
                ON CONFLICT(month) DO UPDATE
                SET amount = excluded.amount
                """,
                (self.selected_month, amount)
            )

        self.refresh_all()

        messagebox.showinfo(
            "Budget saved",
            f"Monthly budget saved for {self.selected_month}."
        )

    # -------------------- DASHBOARD --------------------

    @staticmethod
    def money(amount):
        return f"₹{amount:,.2f}"

    def refresh_all(self):

        self.month_label.configure(
            text=f"Showing: {self.selected_month}"
        )

        totals = self.month_totals()
        income = totals["Income"]
        expenses = totals["Expense"]
        budget = self.get_budget()
        remaining = budget - expenses

        self.summary_values["income"].configure(
            text=self.money(income)
        )
        self.summary_values["expenses"].configure(
            text=self.money(expenses)
        )
        self.summary_values["balance"].configure(
            text=self.money(income - expenses)
        )
        self.summary_values["budget"].configure(
            text=self.money(remaining) if budget > 0 else "Not set",
            text_color=RED if budget > 0 and remaining < 0 else ORANGE
        )

        self.budget_var.set(
            f"{budget:.2f}" if budget > 0 else ""
        )

        if budget > 0:
            ratio = expenses / budget

            self.budget_progress.set(min(1.0, ratio))
            self.budget_progress.configure(
                progress_color=RED if ratio >= 1 else GREEN
            )

            status = (
                f"{self.money(expenses)} of {self.money(budget)} spent "
                f"({ratio:.0%})."
            )

            if ratio > 1:
                status += " Budget exceeded!"

            self.budget_status.configure(text=status)

        else:
            self.budget_progress.set(0)
            self.budget_status.configure(
                text="Set a monthly spending limit."
            )

        self.refresh_transactions()
        self.refresh_chart()

    # -------------------- TRANSACTION HISTORY --------------------

    def refresh_transactions(self):

        for widget in self.transactions_frame.winfo_children():
            widget.destroy()

        self.transaction_vars = {}
        kind_filter = self.filter_var.get()

        if kind_filter == "All":
            rows = self.db.execute(
                """
                SELECT * FROM transactions
                WHERE substr(transaction_date, 1, 7) = ?
                ORDER BY transaction_date DESC, id DESC
                """,
                (self.selected_month,)
            ).fetchall()
        else:
            rows = self.db.execute(
                """
                SELECT * FROM transactions
                WHERE substr(transaction_date, 1, 7) = ?
                  AND kind = ?
                ORDER BY transaction_date DESC, id DESC
                """,
                (self.selected_month, kind_filter)
            ).fetchall()

        if not rows:
            ctk.CTkLabel(
                self.transactions_frame,
                text="No transactions for this month yet.",
                text_color=MUTED
            ).pack(anchor="w", padx=10, pady=14)
            return

        for row in rows:

            item = ctk.CTkFrame(
                self.transactions_frame,
                fg_color=PANEL_LIGHT, corner_radius=10
            )
            item.pack(fill="x", padx=2, pady=4)

            var = tk.BooleanVar(value=False)
            self.transaction_vars[row["id"]] = var

            ctk.CTkCheckBox(
                item, text="", variable=var,
                width=18, checkbox_width=16,
                checkbox_height=16
            ).pack(side="left", padx=(8, 2), pady=10)

            details = ctk.CTkFrame(
                item, fg_color="transparent"
            )
            details.pack(
                side="left", fill="x", expand=True,
                padx=4, pady=7
            )

            ctk.CTkLabel(
                details,
                text=row["note"] or row["category"],
                text_color=TEXT,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w")

            ctk.CTkLabel(
                details,
                text=f"{row['category']} · {row['transaction_date']}",
                text_color=MUTED,
                font=ctk.CTkFont(size=10)
            ).pack(anchor="w")

            color = GREEN if row["kind"] == "Income" else RED
            sign = "+" if row["kind"] == "Income" else "−"

            ctk.CTkLabel(
                item,
                text=f"{sign}{self.money(row['amount'])}",
                text_color=color,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="right", padx=10)

    def delete_selected(self):

        selected = [
            tx_id
            for tx_id, var in self.transaction_vars.items()
            if var.get()
        ]

        if not selected:
            messagebox.showinfo(
                "Nothing selected",
                "Select one or more transactions using their checkboxes."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm deletion",
            f"Delete {len(selected)} selected transaction(s)?"
        )

        if not confirm:
            return

        with self.db:
            self.db.executemany(
                "DELETE FROM transactions WHERE id = ?",
                [(tx_id,) for tx_id in selected]
            )

        self.refresh_all()

    # -------------------- CHART --------------------

    def refresh_chart(self):

        for widget in self.chart_holder.winfo_children():
            widget.destroy()

        rows = self.db.execute(
            """
            SELECT category, SUM(amount) AS total
            FROM transactions
            WHERE kind = 'Expense'
              AND substr(transaction_date, 1, 7) = ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (self.selected_month,)
        ).fetchall()

        if not rows:
            self.chart_note.configure(
                text="Add expenses to see your breakdown."
            )
            return

        labels = [row["category"] for row in rows]
        values = [row["total"] for row in rows]

        colors = [
            "#7C5CFC", "#36C98F", "#FFB454",
            "#FF6B78", "#68B8FF", "#C792EA",
            "#80CBC4", "#F48FB1", "#B0BEC5",
            "#DCE775", "#FF8A65"
        ]

        fig = Figure(
            figsize=(4.2, 3.0),
            dpi=100,
            facecolor=PANEL
        )

        ax = fig.add_subplot(111)
        ax.set_facecolor(PANEL)

        wedges, _ = ax.pie(
            values,
            startangle=90,
            colors=colors[:len(values)],
            wedgeprops={
                "width": 0.38,
                "edgecolor": PANEL
            }
        )

        ax.legend(
            wedges,
            labels,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.18),
            ncol=2,
            fontsize=8,
            frameon=False,
            labelcolor=TEXT
        )

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(
            fig, master=self.chart_holder
        )
        canvas.draw()
        canvas.get_tk_widget().pack(
            fill="both", expand=True
        )

        self.chart_note.configure(
            text=f"{len(rows)} spending categories this month"
        )

    # -------------------- CSV EXPORT --------------------

    def export_csv(self):

        rows = self.db.execute(
            """
            SELECT transaction_date, kind, category, amount, note
            FROM transactions
            WHERE substr(transaction_date, 1, 7) = ?
            ORDER BY transaction_date, id
            """,
            (self.selected_month,)
        ).fetchall()

        if not rows:
            messagebox.showinfo(
                "Nothing to export",
                "There are no transactions for this month."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Export transactions",
            defaultextension=".csv",
            initialfile=f"pennywise_{self.selected_month}.csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not path:
            return

        with open(
            path, "w", newline="", encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Date", "Type", "Category",
                "Amount (INR)", "Note"
            ])

            for row in rows:
                writer.writerow([
                    row["transaction_date"],
                    row["kind"],
                    row["category"],
                    f"{row['amount']:.2f}",
                    row["note"]
                ])

        messagebox.showinfo(
            "Export complete",
            f"Transactions exported to:\n{path}"
        )

    # -------------------- CLOSE APP --------------------

    def close_app(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = PennyWise()
    app.mainloop()
