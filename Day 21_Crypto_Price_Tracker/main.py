

import json
import sqlite3
import threading
import time
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
import requests

try:
    from plyer import notification
except ImportError:
    notification = None

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError:
    FigureCanvasTkAgg = None
    Figure = None


APP_DIR = Path.home() / ".cryptopulse"
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = APP_DIR / "cryptopulse.db"
API_URL = "https://api.coingecko.com/api/v3/simple/price"

COINS = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Solana (SOL)": "solana",
    "BNB (BNB)": "binancecoin",
    "XRP (XRP)": "ripple",
    "Dogecoin (DOGE)": "dogecoin",
    "Cardano (ADA)": "cardano",
    "Polygon (POL)": "polygon-ecosystem-token",
    "Chainlink (LINK)": "chainlink",
    "Litecoin (LTC)": "litecoin",
}
COIN_NAMES = {coin_id: name for name, coin_id in COINS.items()}
DEFAULT_WATCHLIST = ["bitcoin", "ethereum", "solana", "dogecoin"]


def format_price(value):
    if value is None:
        return "—"
    if value >= 1000:
        return f"${value:,.2f}"
    if value >= 1:
        return f"${value:,.4f}"
    return f"${value:,.6f}"


class CryptoPulseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CryptoPulse — Crypto Tracker")
        self.geometry("1180x780")
        self.minsize(980, 680)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.watchlist = set(DEFAULT_WATCHLIST)
        self.prices = {}
        self.previous_prices = {}
        self.alerts = []
        self.refresh_seconds = 60
        self.refresh_job_active = False
        self.stop_event = threading.Event()
        self.last_updated = "Not updated yet"
        self.status_text = "Ready"
        self._init_db()
        self._load_state()
        self._build_ui()
        self._render_watchlist()
        self._render_alerts()
        self._update_summary()
        self.after(700, self.refresh_prices)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- persistence ----------
    def _init_db(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coin_id TEXT NOT NULL,
                    price REAL NOT NULL,
                    checked_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coin_id TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    target REAL NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    triggered INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)

    def _load_state(self):
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                "SELECT id, coin_id, direction, target, enabled, triggered, created_at FROM alerts"
            ).fetchall()
        self.alerts = [
            {
                "id": r[0], "coin_id": r[1], "direction": r[2], "target": r[3],
                "enabled": bool(r[4]), "triggered": bool(r[5]), "created_at": r[6]
            }
            for r in rows
        ]

    def _save_alert(self, coin_id, direction, target):
        now = datetime.now().isoformat(timespec="seconds")
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                """INSERT INTO alerts (coin_id, direction, target, enabled, triggered, created_at)
                   VALUES (?, ?, ?, 1, 0, ?)""",
                (coin_id, direction, target, now),
            )
            alert_id = cur.lastrowid
        self.alerts.append({
            "id": alert_id, "coin_id": coin_id, "direction": direction,
            "target": target, "enabled": True, "triggered": False, "created_at": now
        })

    def _update_alert_db(self, alert):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "UPDATE alerts SET enabled=?, triggered=? WHERE id=?",
                (int(alert["enabled"]), int(alert["triggered"]), alert["id"]),
            )

    # ---------- UI ----------
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=210, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(8, weight=1)
        ctk.CTkLabel(sidebar, text="◈ CryptoPulse", font=ctk.CTkFont(size=23, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(28, 4), sticky="w"
        )
        ctk.CTkLabel(sidebar, text="MARKET WATCH", text_color="gray", font=ctk.CTkFont(size=11, weight="bold")).grid(
            row=1, column=0, padx=20, pady=(22, 8), sticky="w"
        )
        ctk.CTkButton(sidebar, text="↻  Refresh prices", command=self.refresh_prices).grid(
            row=2, column=0, padx=16, pady=6, sticky="ew"
        )
        ctk.CTkButton(sidebar, text="＋  Add to watchlist", command=self.open_add_coin).grid(
            row=3, column=0, padx=16, pady=6, sticky="ew"
        )
        ctk.CTkButton(sidebar, text="＋  Create price alert", command=self.open_add_alert).grid(
            row=4, column=0, padx=16, pady=6, sticky="ew"
        )
        ctk.CTkLabel(sidebar, text="SETTINGS", text_color="gray", font=ctk.CTkFont(size=11, weight="bold")).grid(
            row=5, column=0, padx=20, pady=(24, 8), sticky="w"
        )
        self.interval_var = tk.StringVar(value="60 seconds")
        ctk.CTkOptionMenu(
            sidebar, values=["30 seconds", "60 seconds", "120 seconds", "300 seconds"],
            variable=self.interval_var, command=self.change_interval
        ).grid(row=6, column=0, padx=16, pady=6, sticky="ew")
        ctk.CTkLabel(sidebar, text="Data: CoinGecko public API\nHistory stored locally in SQLite",
                     justify="left", text_color="gray", font=ctk.CTkFont(size=11)).grid(
            row=9, column=0, padx=18, pady=20, sticky="sw"
        )

        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, padx=24, pady=22, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(3, weight=1)

        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Market Dashboard", font=ctk.CTkFont(size=28, weight="bold")).grid(
            row=0, column=0, sticky="w"
        )
        self.status_label = ctk.CTkLabel(header, text="● Ready", text_color="#5ad6a0")
        self.status_label.grid(row=0, column=1, sticky="e", padx=8)
        self.updated_label = ctk.CTkLabel(header, text="Last update: Not updated yet", text_color="gray")
        self.updated_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

        summary = ctk.CTkFrame(self.main, fg_color="transparent")
        summary.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        for col in range(3):
            summary.grid_columnconfigure(col, weight=1)
        self.total_card = self._stat_card(summary, 0, "WATCHLIST ASSETS", "0")
        self.alert_card = self._stat_card(summary, 1, "ACTIVE ALERTS", "0")
        self.price_card = self._stat_card(summary, 2, "PRICES LOADED", "0")

        controls = ctk.CTkFrame(self.main, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        ctk.CTkLabel(controls, text="Your Watchlist", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        ctk.CTkButton(controls, text="Price history", width=120, command=self.show_history).pack(side="right")

        self.list_frame = ctk.CTkScrollableFrame(self.main, corner_radius=12)
        self.list_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 14))
        self.list_frame.grid_columnconfigure(0, weight=1)

        bottom = ctk.CTkFrame(self.main, corner_radius=12)
        bottom.grid(row=4, column=0, sticky="ew")
        bottom.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(bottom, text="Price Alerts", font=ctk.CTkFont(size=19, weight="bold")).grid(
            row=0, column=0, padx=16, pady=(12, 5), sticky="w"
        )
        self.alert_frame = ctk.CTkScrollableFrame(bottom, height=130, fg_color="transparent")
        self.alert_frame.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="ew")
        self.alert_frame.grid_columnconfigure(0, weight=1)

    def _stat_card(self, parent, column, title, value):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=0, column=column, padx=(0 if column == 0 else 8, 0), sticky="ew")
        ctk.CTkLabel(card, text=title, text_color="gray", font=ctk.CTkFont(size=11, weight="bold")).pack(
            anchor="w", padx=16, pady=(14, 4)
        )
        label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=25, weight="bold"))
        label.pack(anchor="w", padx=16, pady=(0, 14))
        return label

    def _set_status(self, text, good=True):
        self.status_label.configure(text=f"● {text}", text_color="#5ad6a0" if good else "#f0b35b")

    def _update_summary(self):
        self.total_card.configure(text=str(len(self.watchlist)))
        self.alert_card.configure(text=str(sum(1 for a in self.alerts if a["enabled"] and not a["triggered"])))
        self.price_card.configure(text=str(len(self.prices)))
        self.updated_label.configure(text=f"Last update: {self.last_updated}")

    # ---------- market data ----------
    def refresh_prices(self):
        if self.refresh_job_active:
            return
        self.refresh_job_active = True
        self._set_status("Fetching prices…")
        threading.Thread(target=self._fetch_prices_worker, daemon=True).start()

    def _fetch_prices_worker(self):
        try:
            ids = sorted(self.watchlist)
            if not ids:
                self.after(0, self._refresh_failed, "Your watchlist is empty.")
                return
            response = requests.get(
                API_URL,
                params={"ids": ",".join(ids), "vs_currencies": "usd", "include_24hr_change": "true"},
                timeout=15,
                headers={"User-Agent": "CryptoPulse-Student-Project/1.0"},
            )
            response.raise_for_status()
            payload = response.json()
            parsed = {}
            for coin_id, values in payload.items():
                if "usd" in values:
                    parsed[coin_id] = {
                        "price": float(values["usd"]),
                        "change": values.get("usd_24h_change"),
                    }
            if not parsed:
                raise ValueError("The API returned no prices for the selected assets.")
            now = datetime.now().isoformat(timespec="seconds")
            with sqlite3.connect(DB_PATH) as conn:
                for coin_id, data in parsed.items():
                    conn.execute(
                        "INSERT INTO price_history (coin_id, price, checked_at) VALUES (?, ?, ?)",
                        (coin_id, data["price"], now),
                    )
            self.after(0, self._refresh_success, parsed, now)
        except requests.RequestException as exc:
            self.after(0, self._refresh_failed, f"Network/API error: {exc}")
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            self.after(0, self._refresh_failed, f"Could not read price data: {exc}")
        finally:
            self.after(0, self._finish_refresh)

    def _finish_refresh(self):
        self.refresh_job_active = False

    def _refresh_failed(self, error):
        self._set_status("Update failed", good=False)
        messagebox.showwarning("Price update failed", error + "\n\nCheck your internet connection and try again.")

    def _refresh_success(self, parsed, now):
        self.previous_prices = dict(self.prices)
        self.prices.update(parsed)
        self.last_updated = datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
        self._set_status("Live data updated")
        self._render_watchlist()
        self._check_alerts()
        self._render_alerts()
        self._update_summary()
        self.after(self.refresh_seconds * 1000, self.refresh_prices)

    def change_interval(self, value):
        self.refresh_seconds = int(value.split()[0])
        self._set_status(f"Refresh interval: {self.refresh_seconds}s")
        # Next scheduled refresh uses the new interval.

    # ---------- watchlist ----------
    def _render_watchlist(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        if not self.watchlist:
            ctk.CTkLabel(self.list_frame, text="Your watchlist is empty. Add an asset to begin.",
                         text_color="gray").grid(row=0, column=0, padx=18, pady=28)
            return

        header = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="ASSET", text_color="gray", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=10)
        ctk.CTkLabel(header, text="PRICE (USD)", text_color="gray", font=ctk.CTkFont(size=11, weight="bold"), width=140).grid(row=0, column=1, sticky="e", padx=10)
        ctk.CTkLabel(header, text="24H CHANGE", text_color="gray", font=ctk.CTkFont(size=11, weight="bold"), width=110).grid(row=0, column=2, sticky="e", padx=10)

        for index, coin_id in enumerate(sorted(self.watchlist), start=1):
            row = ctk.CTkFrame(self.list_frame, corner_radius=10)
            row.grid(row=index, column=0, sticky="ew", padx=6, pady=4)
            row.grid_columnconfigure(0, weight=1)
            name = COIN_NAMES.get(coin_id, coin_id.title())
            ctk.CTkLabel(row, text=name, font=ctk.CTkFont(size=14, weight="bold")).grid(
                row=0, column=0, sticky="w", padx=14, pady=12
            )
            data = self.prices.get(coin_id)
            price = data["price"] if data else None
            ctk.CTkLabel(row, text=format_price(price), width=140, anchor="e",
                         font=ctk.CTkFont(size=14)).grid(row=0, column=1, padx=10)
            change = data.get("change") if data else None
            change_text = f"{change:+.2f}%" if isinstance(change, (int, float)) else "—"
            change_color = "#5ad6a0" if isinstance(change, (int, float)) and change >= 0 else "#ff7777"
            ctk.CTkLabel(row, text=change_text, width=110, anchor="e", text_color=change_color).grid(
                row=0, column=2, padx=10
            )
            ctk.CTkButton(row, text="Remove", width=72, height=28, fg_color="#54383d",
                          hover_color="#74434a", command=lambda cid=coin_id: self.remove_coin(cid)).grid(
                row=0, column=3, padx=(8, 12), pady=8
            )

    def open_add_coin(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add asset")
        dialog.geometry("370x220")
        dialog.transient(self)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text="Add cryptocurrency", font=ctk.CTkFont(size=20, weight="bold")).pack(
            padx=20, pady=(20, 10)
        )
        available = [name for name, cid in COINS.items() if cid not in self.watchlist]
        if not available:
            ctk.CTkLabel(dialog, text="All built-in assets are already in your watchlist.").pack(pady=12)
            ctk.CTkButton(dialog, text="Close", command=dialog.destroy).pack(pady=10)
            return
        var = tk.StringVar(value=available[0])
        ctk.CTkOptionMenu(dialog, values=available, variable=var, width=260).pack(pady=8)

        def add():
            coin_id = COINS[var.get()]
            self.watchlist.add(coin_id)
            dialog.destroy()
            self._render_watchlist()
            self._update_summary()
            self.refresh_prices()

        ctk.CTkButton(dialog, text="Add to watchlist", command=add).pack(pady=12)

    def remove_coin(self, coin_id):
        self.watchlist.discard(coin_id)
        self._render_watchlist()
        self._update_summary()

    # ---------- alerts ----------
    def open_add_alert(self):
        if not self.watchlist:
            messagebox.showinfo("Watchlist needed", "Add a cryptocurrency to your watchlist first.")
            return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create price alert")
        dialog.geometry("410x330")
        dialog.transient(self)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text="Create a price alert", font=ctk.CTkFont(size=21, weight="bold")).pack(
            padx=20, pady=(20, 12)
        )
        coin_names = [COIN_NAMES.get(cid, cid.title()) for cid in sorted(self.watchlist)]
        name_to_id = {COIN_NAMES.get(cid, cid.title()): cid for cid in sorted(self.watchlist)}
        coin_var = tk.StringVar(value=coin_names[0])
        direction_var = tk.StringVar(value="Falls below")
        target_var = tk.StringVar()
        ctk.CTkLabel(dialog, text="Cryptocurrency").pack(anchor="w", padx=28)
        ctk.CTkOptionMenu(dialog, values=coin_names, variable=coin_var, width=340).pack(padx=25, pady=(4, 10))
        ctk.CTkLabel(dialog, text="Alert when price").pack(anchor="w", padx=28)
        ctk.CTkOptionMenu(dialog, values=["Falls below", "Rises above"], variable=direction_var, width=340).pack(
            padx=25, pady=(4, 10)
        )
        ctk.CTkLabel(dialog, text="Target price (USD)").pack(anchor="w", padx=28)
        ctk.CTkEntry(dialog, textvariable=target_var, placeholder_text="e.g. 60000", width=340).pack(
            padx=25, pady=(4, 8)
        )

        def create():
            try:
                target = float(target_var.get().strip().replace(",", ""))
                if target <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid target", "Enter a valid positive price.", parent=dialog)
                return
            direction = "below" if direction_var.get() == "Falls below" else "above"
            self._save_alert(name_to_id[coin_var.get()], direction, target)
            dialog.destroy()
            self._render_alerts()
            self._update_summary()
            self._set_status("Price alert created")

        ctk.CTkButton(dialog, text="Save alert", command=create).pack(pady=12)

    def _check_alerts(self):
        for alert in self.alerts:
            if not alert["enabled"] or alert["triggered"]:
                continue
            data = self.prices.get(alert["coin_id"])
            if not data:
                continue
            price = data["price"]
            reached = (alert["direction"] == "below" and price <= alert["target"]) or (
                alert["direction"] == "above" and price >= alert["target"]
            )
            if reached:
                alert["triggered"] = True
                self._update_alert_db(alert)
                coin = COIN_NAMES.get(alert["coin_id"], alert["coin_id"].title())
                direction = "fell to or below" if alert["direction"] == "below" else "rose to or above"
                title = "CryptoPulse price alert"
                body = f"{coin} {direction} {format_price(alert['target'])}. Current: {format_price(price)}"
                self._notify(title, body)
                messagebox.showinfo(title, body)

    def _notify(self, title, body):
        if notification is None:
            return
        try:
            notification.notify(title=title, message=body, app_name="CryptoPulse", timeout=10)
        except Exception:
            # Desktop notification APIs vary by operating system and permissions.
            pass

    def _render_alerts(self):
        for widget in self.alert_frame.winfo_children():
            widget.destroy()
        if not self.alerts:
            ctk.CTkLabel(self.alert_frame, text="No alerts yet. Create one to get notified when a target is reached.",
                         text_color="gray").grid(row=0, column=0, padx=10, pady=14, sticky="w")
            return
        for i, alert in enumerate(reversed(self.alerts)):
            coin = COIN_NAMES.get(alert["coin_id"], alert["coin_id"].title())
            condition = "below" if alert["direction"] == "below" else "above"
            state = "Triggered" if alert["triggered"] else ("Active" if alert["enabled"] else "Paused")
            color = "#5ad6a0" if alert["triggered"] else ("#f0b35b" if alert["enabled"] else "gray")
            row = ctk.CTkFrame(self.alert_frame, fg_color="transparent")
            row.grid(row=i, column=0, sticky="ew", pady=3)
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(row, text=f"{coin}  •  {condition} {format_price(alert['target'])}",
                         anchor="w").grid(row=0, column=0, sticky="w", padx=8)
            ctk.CTkLabel(row, text=state, text_color=color, width=75).grid(row=0, column=1, padx=4)
            if not alert["triggered"]:
                ctk.CTkButton(row, text="Pause" if alert["enabled"] else "Resume", width=70, height=26,
                              command=lambda a=alert: self.toggle_alert(a)).grid(row=0, column=2, padx=3)
            ctk.CTkButton(row, text="Delete", width=60, height=26, fg_color="#54383d",
                          hover_color="#74434a", command=lambda a=alert: self.delete_alert(a)).grid(
                row=0, column=3, padx=(3, 8)
            )

    def toggle_alert(self, alert):
        alert["enabled"] = not alert["enabled"]
        self._update_alert_db(alert)
        self._render_alerts()
        self._update_summary()

    def delete_alert(self, alert):
        self.alerts = [a for a in self.alerts if a["id"] != alert["id"]]
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM alerts WHERE id=?", (alert["id"],))
        self._render_alerts()
        self._update_summary()

    # ---------- history ----------
    def show_history(self):
        if Figure is None or FigureCanvasTkAgg is None:
            messagebox.showinfo("Matplotlib not installed",
                                "Install chart support with: python3 -m pip install matplotlib")
            return
        if not self.watchlist:
            messagebox.showinfo("No assets", "Add an asset to your watchlist first.")
            return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Price history")
        dialog.geometry("850x560")
        dialog.transient(self)
        ctk.CTkLabel(dialog, text="Stored price history", font=ctk.CTkFont(size=22, weight="bold")).pack(
            padx=20, pady=15
        )
        coin_names = [COIN_NAMES.get(cid, cid.title()) for cid in sorted(self.watchlist)]
        name_to_id = {COIN_NAMES.get(cid, cid.title()): cid for cid in sorted(self.watchlist)}
        selected = tk.StringVar(value=coin_names[0])
        chooser = ctk.CTkOptionMenu(dialog, values=coin_names, variable=selected)
        chooser.pack(pady=(0, 8))
        chart_frame = ctk.CTkFrame(dialog)
        chart_frame.pack(fill="both", expand=True, padx=15, pady=12)

        def draw(*_):
            for child in chart_frame.winfo_children():
                child.destroy()
            coin_id = name_to_id[selected.get()]
            with sqlite3.connect(DB_PATH) as conn:
                rows = conn.execute(
                    "SELECT price, checked_at FROM price_history WHERE coin_id=? ORDER BY id DESC LIMIT 100",
                    (coin_id,),
                ).fetchall()
            rows.reverse()
            if not rows:
                ctk.CTkLabel(chart_frame, text="No stored history yet. Refresh prices a few times first.").pack(pady=35)
                return
            fig = Figure(figsize=(8, 4.2), dpi=100)
            ax = fig.add_subplot(111)
            x_values = list(range(1, len(rows) + 1))
            y_values = [r[0] for r in rows]
            ax.plot(x_values, y_values, marker="o", markersize=3)
            ax.set_title(f"{COIN_NAMES.get(coin_id, coin_id.title())} — stored price checks")
            ax.set_xlabel("Price check (oldest → newest)")
            ax.set_ylabel("Price (USD)")
            ax.grid(True, alpha=0.25)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        chooser.configure(command=lambda _: draw())
        draw()

    def on_close(self):
        self.stop_event.set()
        self.destroy()


if __name__ == "__main__":
    app = CryptoPulseApp()
    app.mainloop()
