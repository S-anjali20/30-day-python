"""
Day 22 — SkyTrack: Real-Time Flight Tracker
Install in your existing Python environment:
    python3 -m pip install customtkinter requests folium
Run:
    python3 main.py

Uses OpenSky Network state data. Coverage, access and rate limits may vary.
Aircraft positions are not guaranteed airline schedules or arrival estimates.
"""
import threading
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
import requests
try:
    import folium
except ImportError:
    folium = None

API_URL = "https://opensky-network.org/api/states/all"
APP_DIR = Path.home() / ".skytrack"
APP_DIR.mkdir(parents=True, exist_ok=True)
MAP_PATH = APP_DIR / "skytrack_map.html"
REGIONS = {
    "Europe (default)": (35, 71, -12, 32),
    "North America": (15, 72, -170, -50),
    "India & nearby": (5, 38, 60, 100),
    "East Asia": (5, 55, 95, 150),
    "Global (heavier request)": None,
}


def number(value):
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def parse_state(row):
    if not row or len(row) < 17:
        return None
    return {
        "icao": str(row[0] or "").strip().upper(),
        "callsign": str(row[1] or "").strip() or "Unknown",
        "country": str(row[2] or "Unknown"),
        "lon": number(row[5]), "lat": number(row[6]),
        "baro_alt": number(row[7]), "ground": bool(row[8]),
        "velocity": number(row[9]), "heading": number(row[10]),
        "vertical": number(row[11]), "geo_alt": number(row[13]),
        "squawk": str(row[14] or "—"),
    }


def altitude(meters):
    return "—" if meters is None else f"{meters:,.0f} m / {meters * 3.28084:,.0f} ft"


class SkyTrackApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SkyTrack — Real-Time Flight Tracker")
        self.geometry("1220x790")
        self.minsize(980, 660)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.aircraft = []
        self.filtered = []
        self.selected = None
        self.fetching = False
        self.refresh_seconds = 60
        self.auto_refresh = tk.BooleanVar(value=True)
        self.region = tk.StringVar(value="India & nearby")
        self.search = tk.StringVar()
        self._build_ui()
        self.after(500, self.fetch_flights)
        self.after(1500, self._schedule_refresh)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        side = ctk.CTkFrame(self, width=220, corner_radius=0)
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(side, text="✈ SkyTrack", font=ctk.CTkFont(size=25, weight="bold")).grid(
            row=0, column=0, padx=18, pady=(28, 4), sticky="w")
        ctk.CTkLabel(side, text="FLIGHT MONITOR", text_color="gray").grid(
            row=1, column=0, padx=20, pady=(4, 24), sticky="w")
        ctk.CTkLabel(side, text="Search callsign / ICAO / country").grid(
            row=2, column=0, padx=15, pady=(0, 5), sticky="w")
        entry = ctk.CTkEntry(side, textvariable=self.search, placeholder_text="e.g. AAL or India")
        entry.grid(row=3, column=0, padx=15, pady=(0, 10), sticky="ew")
        entry.bind("<KeyRelease>", lambda _e: self.apply_filter())
        ctk.CTkLabel(side, text="Region").grid(row=4, column=0, padx=15, pady=(8, 4), sticky="w")
        ctk.CTkOptionMenu(side, values=list(REGIONS), variable=self.region,
                          command=lambda _v: self.fetch_flights()).grid(
            row=5, column=0, padx=15, pady=5, sticky="ew")
        ctk.CTkButton(side, text="↻  Refresh flights", command=self.fetch_flights).grid(
            row=6, column=0, padx=15, pady=6, sticky="ew")
        ctk.CTkButton(side, text="Open live map", command=self.open_map).grid(
            row=7, column=0, padx=15, pady=6, sticky="ew")
        ctk.CTkLabel(side, text="AUTO REFRESH", text_color="gray").grid(
            row=8, column=0, padx=18, pady=(24, 5), sticky="w")
        ctk.CTkCheckBox(side, text="Refresh automatically", variable=self.auto_refresh).grid(
            row=9, column=0, padx=15, pady=5, sticky="w")
        ctk.CTkOptionMenu(side, values=["30 seconds", "60 seconds", "120 seconds", "300 seconds"],
                          command=self.change_interval).grid(row=10, column=0, padx=15, pady=5, sticky="ew")
        side.grid_rowconfigure(11, weight=1)
        ctk.CTkLabel(side, text="Data: OpenSky Network\nMap: OpenStreetMap\n\nCoverage and update\nfrequency may vary.",
                     text_color="gray", justify="left", font=ctk.CTkFont(size=11)).grid(
            row=12, column=0, padx=15, pady=18, sticky="sw")

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, padx=22, pady=20, sticky="nsew")
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=2)
        main.grid_rowconfigure(2, weight=1)
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Live Flight Dashboard",
                     font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, sticky="w")
        self.status = ctk.CTkLabel(header, text="● Ready", text_color="#5ad6a0")
        self.status.grid(row=0, column=1, sticky="e")
        self.updated = ctk.CTkLabel(header, text="Last update: not yet", text_color="gray")
        self.updated.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        cards = ctk.CTkFrame(main, fg_color="transparent")
        cards.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        for col in range(3):
            cards.grid_columnconfigure(col, weight=1)
        self.total = self._card(cards, 0, "AIRCRAFT RECEIVED")
        self.matching = self._card(cards, 1, "MATCHING SEARCH")
        self.airborne = self._card(cards, 2, "AIRBORNE")

        list_panel = ctk.CTkFrame(main, corner_radius=12)
        list_panel.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        list_panel.grid_columnconfigure(0, weight=1)
        list_panel.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(list_panel, text="Aircraft", font=ctk.CTkFont(size=19, weight="bold")).grid(
            row=0, column=0, padx=14, pady=12, sticky="w")
        self.list_frame = ctk.CTkScrollableFrame(list_panel)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.list_frame.grid_columnconfigure(0, weight=1)

        detail = ctk.CTkFrame(main, corner_radius=12)
        detail.grid(row=2, column=1, sticky="nsew", padx=(8, 0))
        detail.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(detail, text="Aircraft Details", font=ctk.CTkFont(size=19, weight="bold")).grid(
            row=0, column=0, padx=15, pady=(14, 8), sticky="w")
        self.detail_title = ctk.CTkLabel(detail, text="Select an aircraft",
                                          font=ctk.CTkFont(size=18, weight="bold"))
        self.detail_title.grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.detail_country = ctk.CTkLabel(detail, text="Flight information appears here", text_color="gray")
        self.detail_country.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="w")
        self.details = ctk.CTkFrame(detail, fg_color="transparent")
        self.details.grid(row=3, column=0, padx=12, pady=5, sticky="new")
        self.details.grid_columnconfigure(1, weight=1)
        self.show_details(None)
        ctk.CTkLabel(main, text="Select an aircraft to inspect it. The map opens in your browser.",
                     text_color="gray", anchor="w").grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(12, 0))

    def _card(self, parent, col, title):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=0, column=col, padx=(0 if col == 0 else 8, 0), sticky="ew")
        ctk.CTkLabel(card, text=title, text_color="gray",
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=14, pady=(12, 3))
        label = ctk.CTkLabel(card, text="—", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(anchor="w", padx=14, pady=(0, 12))
        return label

    def change_interval(self, value):
        self.refresh_seconds = int(value.split()[0])

    def _schedule_refresh(self):
        if not self.winfo_exists():
            return
        if self.auto_refresh.get():
            self.fetch_flights()
        self.after(self.refresh_seconds * 1000, self._schedule_refresh)

    def fetch_flights(self):
        if self.fetching:
            return
        self.fetching = True
        self.status.configure(text="● Fetching aircraft…", text_color="#f0b35b")
        threading.Thread(target=self._fetch_worker, daemon=True).start()

    def _fetch_worker(self):
        try:
            params = {}
            bounds = REGIONS[self.region.get()]
            if bounds:
                params = {"lamin": bounds[0], "lamax": bounds[1], "lomin": bounds[2], "lomax": bounds[3]}
            response = requests.get(API_URL, params=params, timeout=25,
                                    headers={"User-Agent": "SkyTrack-Student-Project/1.0"})
            if response.status_code in (401, 403):
                raise RuntimeError("OpenSky denied this request. API access/authentication rules can vary.")
            if response.status_code == 429:
                raise RuntimeError("OpenSky rate limit reached. Wait before refreshing again.")
            response.raise_for_status()
            payload = response.json()
            aircraft = [item for row in (payload.get("states") or []) if (item := parse_state(row))]
            stamp = payload.get("time")
            updated = datetime.fromtimestamp(stamp, timezone.utc).strftime("%d %b %Y, %H:%M:%S UTC") if stamp else datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M:%S UTC")
            self.after(0, self._fetch_success, aircraft, updated)
        except Exception as exc:
            self.after(0, self._fetch_error, str(exc))
        finally:
            self.after(0, self._fetch_finished)

    def _fetch_finished(self):
        self.fetching = False

    def _fetch_error(self, error):
        self.status.configure(text="● Update failed", text_color="#f0b35b")
        messagebox.showwarning("Flight data unavailable",
                               f"Could not retrieve aircraft data.\n\n{error}\n\nCheck your connection or try again later.")

    def _fetch_success(self, aircraft, updated):
        self.aircraft = aircraft
        self.updated.configure(text=f"Last update: {updated}")
        self.status.configure(text="● Data updated", text_color="#5ad6a0")
        self.apply_filter()
        self.render_map_file()

    def apply_filter(self):
        query = self.search.get().strip().lower()
        self.filtered = [a for a in self.aircraft if not query or
                         query in a["callsign"].lower() or query in a["icao"].lower()
                         or query in a["country"].lower()]
        self.total.configure(text=f"{len(self.aircraft):,}")
        self.matching.configure(text=f"{len(self.filtered):,}")
        self.airborne.configure(text=f"{sum(not a['ground'] for a in self.filtered):,}")
        self.render_list()

    def render_list(self):
        for child in self.list_frame.winfo_children():
            child.destroy()
        if not self.filtered:
            ctk.CTkLabel(self.list_frame, text="No matching aircraft.\nTry another region or clear search.",
                         text_color="gray", justify="left").grid(row=0, column=0, padx=12, pady=22, sticky="w")
            return
        for i, aircraft in enumerate(self.filtered[:250]):
            label = aircraft["callsign"] if aircraft["callsign"] != "Unknown" else aircraft["icao"]
            state = "On ground" if aircraft["ground"] else "Airborne"
            ctk.CTkButton(
                self.list_frame, text=f"✈  {label}\n    {aircraft['country']}  •  {state}",
                anchor="w", height=52, fg_color="transparent", hover_color="#263747",
                command=lambda a=aircraft: self.select_aircraft(a)
            ).grid(row=i, column=0, sticky="ew", padx=4, pady=3)
        if len(self.filtered) > 250:
            ctk.CTkLabel(self.list_frame, text="Showing first 250. Refine your search.",
                         text_color="gray").grid(row=250, column=0, pady=8)

    def show_details(self, aircraft):
        for child in self.details.winfo_children():
            child.destroy()
        if aircraft is None:
            fields = [("Callsign", "—"), ("ICAO24", "—"), ("Country", "—"), ("Status", "—"),
                      ("Altitude", "—"), ("Speed", "—"), ("Heading", "—"), ("Vertical rate", "—"),
                      ("Latitude", "—"), ("Longitude", "—"), ("Squawk", "—")]
        else:
            alt = aircraft["geo_alt"] if aircraft["geo_alt"] is not None else aircraft["baro_alt"]
            speed = aircraft["velocity"] * 3.6 if aircraft["velocity"] is not None else None
            fields = [
                ("ICAO24", aircraft["icao"]),
                ("Status", "On ground" if aircraft["ground"] else "Airborne"),
                ("Altitude", altitude(alt)),
                ("Speed", f"{speed:,.0f} km/h" if speed is not None else "—"),
                ("Heading", f"{aircraft['heading']:.0f}°" if aircraft["heading"] is not None else "—"),
                ("Vertical rate", f"{aircraft['vertical']:+.1f} m/s" if aircraft["vertical"] is not None else "—"),
                ("Latitude", f"{aircraft['lat']:.4f}" if aircraft["lat"] is not None else "—"),
                ("Longitude", f"{aircraft['lon']:.4f}" if aircraft["lon"] is not None else "—"),
                ("Squawk", aircraft["squawk"]),
            ]
        for i, (key, value) in enumerate(fields):
            ctk.CTkLabel(self.details, text=key, text_color="gray").grid(
                row=i, column=0, padx=5, pady=8, sticky="w")
            ctk.CTkLabel(self.details, text=value, anchor="e", wraplength=210).grid(
                row=i, column=1, padx=5, pady=8, sticky="e")

    def select_aircraft(self, aircraft):
        self.selected = aircraft
        self.detail_title.configure(text=aircraft["callsign"] if aircraft["callsign"] != "Unknown" else aircraft["icao"])
        self.detail_country.configure(text=aircraft["country"])
        self.show_details(aircraft)
        self.render_map_file()

    def render_map_file(self):
        if folium is None:
            return
        positioned = [a for a in self.filtered if a["lat"] is not None and a["lon"] is not None]
        if self.region.get() == "Global (heavier request)":
            center, zoom = [20, 0], 2
        elif self.selected and self.selected["lat"] is not None and self.selected["lon"] is not None:
            center, zoom = [self.selected["lat"], self.selected["lon"]], 6
        elif positioned:
            center, zoom = [positioned[0]["lat"], positioned[0]["lon"]], 4
        else:
            center, zoom = [20.5937, 78.9629], 4
        fmap = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles=(
            "https://server.arcgisonline.com/ArcGIS/rest/"
            "services/Canvas/World_Light_Gray_Base/"
            "MapServer/tile/{z}/{y}/{x}"
            ),
            attr="Tiles © Esri",
            control_scale=True
        )
        for a in positioned[:1500]:
            name = a["callsign"] if a["callsign"] != "Unknown" else a["icao"]
            alt = altitude(a["geo_alt"] if a["geo_alt"] is not None else a["baro_alt"])
            speed = f"{a['velocity'] * 3.6:.0f} km/h" if a["velocity"] is not None else "Unknown"
            popup = (f"<b>{name}</b><br>ICAO24: {a['icao']}<br>Country: {a['country']}<br>"
                     f"Status: {'On ground' if a['ground'] else 'Airborne'}<br>Altitude: {alt}<br>Speed: {speed}")
            selected = self.selected and self.selected["icao"] == a["icao"]
            folium.Marker(
                [a["lat"], a["lon"]], tooltip=name,
                popup=folium.Popup(popup, max_width=280),
                icon=folium.Icon(color="red" if selected else ("blue" if a["ground"] else "green"),
                                 icon="plane", prefix="fa")
            ).add_to(fmap)
        fmap.save(str(MAP_PATH))

    def open_map(self):
        if folium is None:
            messagebox.showerror("Missing dependency", "Install Folium:\npython3 -m pip install folium")
            return
        self.render_map_file()
        webbrowser.open(MAP_PATH.resolve().as_uri())


if __name__ == "__main__":
    app = SkyTrackApp()
    app.mainloop()
