import requests
import customtkinter as ctk
from datetime import datetime


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class WeatherApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("🌦️ Weather Dashboard")
        self.geometry("900x800")
        self.resizable(False, False)

        self.weather_data = None

        self.create_ui()

    def create_ui(self):

        self.title_label = ctk.CTkLabel(
            self,
            text="🌦️ WEATHER DASHBOARD",
            font=("Arial", 28, "bold")
        )

        self.title_label.pack(
            pady=(20, 8)
        )

        self.search_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.search_frame.pack(
            pady=8
        )

        self.city_entry = ctk.CTkEntry(
            self.search_frame,
            width=450,
            height=42,
            placeholder_text="🔍 Enter city name..."
        )

        self.city_entry.grid(
            row=0,
            column=0,
            padx=8
        )

        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Search",
            width=120,
            height=42,
            command=self.get_weather
        )

        self.search_button.grid(
            row=0,
            column=1,
            padx=8
        )

        self.city_entry.bind(
            "<Return>",
            lambda event: self.get_weather()
        )

        self.location_label = ctk.CTkLabel(
            self,
            text="📍 Search for a city",
            font=("Arial", 18, "bold")
        )

        self.location_label.pack(
            pady=(10, 2)
        )

        self.weather_icon_label = ctk.CTkLabel(
            self,
            text="🌤️",
            font=("Arial", 52)
        )

        self.weather_icon_label.pack(
            pady=(2, 0)
        )

        self.temperature_label = ctk.CTkLabel(
            self,
            text="-- °C",
            font=("Arial", 40, "bold")
        )

        self.temperature_label.pack()

        self.condition_label = ctk.CTkLabel(
            self,
            text="Search for weather information",
            font=("Arial", 17)
        )

        self.condition_label.pack(
            pady=(0, 10)
        )

        self.cards_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.cards_frame.pack(
            pady=5
        )

        self.humidity_card = self.create_card(
            self.cards_frame,
            "💧 Humidity",
            "-- %"
        )

        self.humidity_card.grid(
            row=0,
            column=0,
            padx=8
        )

        self.wind_card = self.create_card(
            self.cards_frame,
            "💨 Wind",
            "-- km/h"
        )

        self.wind_card.grid(
            row=0,
            column=1,
            padx=8
        )

        self.feels_card = self.create_card(
            self.cards_frame,
            "🌡️ Feels Like",
            "-- °C"
        )

        self.feels_card.grid(
            row=0,
            column=2,
            padx=8
        )

        self.buttons_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.buttons_frame.pack(
            pady=(12, 8)
        )

        self.current_button = ctk.CTkButton(
            self.buttons_frame,
            text="🌡️ Current Weather",
            width=200,
            height=40,
            command=self.show_current
        )

        self.current_button.grid(
            row=0,
            column=0,
            padx=10
        )

        self.forecast_button = ctk.CTkButton(
            self.buttons_frame,
            text="📅 5-Day Forecast",
            width=200,
            height=40,
            command=self.show_forecast
        )

        self.forecast_button.grid(
            row=0,
            column=1,
            padx=10
        )

        

        self.result_frame = ctk.CTkFrame(
            self,
            width=820,
            height=270,
            corner_radius=15
        )

        self.result_frame.pack(
            pady=5,
            padx=30,
            fill="x"
        )

        self.result_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 13)
        )

        self.status_label.pack(
            pady=5
        )

        self.show_welcome()

    def create_card(self, parent, title, value):

        card = ctk.CTkFrame(
            parent,
            width=190,
            height=85,
            corner_radius=12
        )

        card.pack_propagate(False)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 14, "bold")
        )

        title_label.pack(
            pady=(10, 2)
        )

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 19, "bold")
        )

        value_label.pack()

        card.value_label = value_label

        return card

    def clear_result_frame(self):

        for widget in self.result_frame.winfo_children():
            widget.destroy()

    def show_welcome(self):

        self.clear_result_frame()

        label = ctk.CTkLabel(
            self.result_frame,
            text=(
                "🌍 Search for a city to view weather information\n\n"
                "Use the buttons above to explore current weather,\n"
                "5-day forecast, and sunrise/sunset times."
            ),
            font=("Arial", 16),
            justify="center"
        )

        label.pack(
            expand=True
        )

    def get_weather(self):

        city = self.city_entry.get().strip()

        if not city:

            self.status_label.configure(
                text="❌ Please enter a city name."
            )

            return

        self.status_label.configure(
            text=f"🌐 Fetching weather for {city}..."
        )

        self.search_button.configure(
            state="disabled"
        )

        self.update_idletasks()

        try:

            geocoding_url = (
                "https://geocoding-api.open-meteo.com/v1/search"
            )

            geocoding_params = {
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            }

            response = requests.get(
                geocoding_url,
                params=geocoding_params,
                timeout=10
            )

            response.raise_for_status()

            location_data = response.json()

            if "results" not in location_data:

                self.status_label.configure(
                    text="❌ City not found."
                )

                self.search_button.configure(
                    state="normal"
                )

                return

            location = location_data["results"][0]

            latitude = location["latitude"]
            longitude = location["longitude"]

            self.city_name = location["name"]

            self.country = location.get(
                "country",
                ""
            )

            weather_url = (
                "https://api.open-meteo.com/v1/forecast"
            )

            weather_params = {

                "latitude": latitude,
                "longitude": longitude,

                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "weather_code,"
                    "wind_speed_10m"
                ),

                "daily": (
                    "weather_code,"
                    "temperature_2m_max,"
                    "temperature_2m_min,"
                    "sunrise,"
                    "sunset"
                ),

                "forecast_days": 5,

                "timezone": "auto",

                "temperature_unit": "celsius",

                "wind_speed_unit": "kmh"
            }

            weather_response = requests.get(
                weather_url,
                params=weather_params,
                timeout=10
            )

            weather_response.raise_for_status()

            self.weather_data = weather_response.json()

            self.update_main_weather()

            self.show_current()

            self.status_label.configure(
                text=f"✅ Weather updated for {self.city_name}"
            )

        except requests.exceptions.RequestException:

            self.status_label.configure(
                text="❌ Unable to connect to weather service."
            )

        except Exception as error:

            self.status_label.configure(
                text=f"❌ Something went wrong: {error}"
            )

        finally:

            self.search_button.configure(
                state="normal"
            )

    def update_main_weather(self):

        current = self.weather_data["current"]

        temperature = current[
            "temperature_2m"
        ]

        humidity = current[
            "relative_humidity_2m"
        ]

        feels = current[
            "apparent_temperature"
        ]

        wind = current[
            "wind_speed_10m"
        ]

        code = current[
            "weather_code"
        ]

        condition = self.weather_description(
            code
        )

        icon = self.weather_icon(
            code
        )

        self.location_label.configure(
            text=f"📍 {self.city_name}, {self.country}"
        )

        self.weather_icon_label.configure(
            text=icon
        )

        self.temperature_label.configure(
            text=f"{temperature} °C"
        )

        self.condition_label.configure(
            text=condition
        )

        self.humidity_card.value_label.configure(
            text=f"{humidity}%"
        )

        self.wind_card.value_label.configure(
            text=f"{wind} km/h"
        )

        self.feels_card.value_label.configure(
            text=f"{feels} °C"
        )

    def show_current(self):

        if not self.weather_data:

            self.status_label.configure(
                text="❌ Search for a city first."
            )

            return

        self.clear_result_frame()

        current = self.weather_data["current"]

        temperature = current[
            "temperature_2m"
        ]

        feels = current[
            "apparent_temperature"
        ]

        humidity = current[
            "relative_humidity_2m"
        ]

        wind = current[
            "wind_speed_10m"
        ]

        condition = self.weather_description(
            current["weather_code"]
        )

        title = ctk.CTkLabel(
            self.result_frame,
            text="🌡️ CURRENT WEATHER",
            font=("Arial", 20, "bold")
        )

        title.pack(
            pady=(15, 10)
        )

        details_frame = ctk.CTkFrame(
            self.result_frame,
            fg_color="transparent"
        )

        details_frame.pack(
            expand=True
        )

        details = [
            ("🌡️ Temperature", f"{temperature} °C"),
            ("🔥 Feels Like", f"{feels} °C"),
            ("💧 Humidity", f"{humidity}%"),
            ("💨 Wind", f"{wind} km/h"),
            ("☁️ Condition", condition)
        ]

        for title_text, value in details:

            row = ctk.CTkFrame(
                details_frame,
                fg_color="transparent"
            )

            row.pack(
                pady=1
            )

            ctk.CTkLabel(
                row,
                text=title_text,
                width=180,
                anchor="e",
                font=("Arial", 14)
            ).grid(
                row=0,
                column=0,
                padx=8
            )

            ctk.CTkLabel(
                row,
                text=value,
                width=180,
                anchor="w",
                font=("Arial", 14, "bold")
            ).grid(
                row=0,
                column=1,
                padx=8
            )

    def show_forecast(self):

        if not self.weather_data:

            self.status_label.configure(
                text="❌ Search for a city first."
            )

            return

        self.clear_result_frame()

        title = ctk.CTkLabel(
            self.result_frame,
            text="📅 5-DAY FORECAST",
            font=("Arial", 20, "bold")
        )

        title.pack(
            pady=(12, 8)
        )

        forecast_frame = ctk.CTkFrame(
            self.result_frame,
            fg_color="transparent"
        )

        forecast_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=5
        )

        daily = self.weather_data["daily"]

        dates = daily["time"]
        codes = daily["weather_code"]
        maximum = daily["temperature_2m_max"]
        minimum = daily["temperature_2m_min"]

        for i in range(5):

            card = ctk.CTkFrame(
                forecast_frame,
                width=140,
                height=145,
                corner_radius=12
            )

            card.grid(
                row=0,
                column=i,
                padx=5,
                sticky="nsew"
            )

            forecast_frame.grid_columnconfigure(
                i,
                weight=1
            )

            date = datetime.strptime(
                dates[i],
                "%Y-%m-%d"
            )

            day = date.strftime("%a")

            icon = self.weather_icon(
                codes[i]
            )

            condition = self.weather_description(
                codes[i]
            )

            ctk.CTkLabel(
                card,
                text=day,
                font=("Arial", 15, "bold")
            ).pack(
                pady=(10, 2)
            )

            ctk.CTkLabel(
                card,
                text=date.strftime("%d %b"),
                font=("Arial", 11)
            ).pack()

            ctk.CTkLabel(
                card,
                text=icon,
                font=("Arial", 30)
            ).pack(
                pady=2
            )

            ctk.CTkLabel(
                card,
                text=f"{maximum[i]}° / {minimum[i]}°",
                font=("Arial", 14, "bold")
            ).pack(
                pady=2
            )

            ctk.CTkLabel(
                card,
                text=condition,
                font=("Arial", 10)
            ).pack(
                pady=(0, 8)
            )



    def weather_icon(self, code):

        icons = {

            0: "☀️",

            1: "🌤️",
            2: "⛅",
            3: "☁️",

            45: "🌫️",
            48: "🌫️",

            51: "🌦️",
            53: "🌦️",
            55: "🌧️",

            61: "🌧️",
            63: "🌧️",
            65: "🌧️",

            71: "🌨️",
            73: "🌨️",
            75: "❄️",

            80: "🌦️",
            81: "🌧️",
            82: "⛈️",

            95: "⛈️",
            96: "⛈️",
            99: "⛈️"
        }

        return icons.get(
            code,
            "🌍"
        )

    def weather_description(self, code):

        descriptions = {

            0: "Clear Sky",

            1: "Mainly Clear",
            2: "Partly Cloudy",
            3: "Overcast",

            45: "Fog",
            48: "Rime Fog",

            51: "Light Drizzle",
            53: "Drizzle",
            55: "Heavy Drizzle",

            61: "Light Rain",
            63: "Rain",
            65: "Heavy Rain",

            71: "Light Snow",
            73: "Snow",
            75: "Heavy Snow",

            80: "Rain Showers",
            81: "Rain Showers",
            82: "Heavy Rain Showers",

            95: "Thunderstorm",
            96: "Thunderstorm + Hail",
            99: "Heavy Thunderstorm"
        }

        return descriptions.get(
            code,
            "Unknown"
        )


if __name__ == "__main__":

    app = WeatherApp()

    app.mainloop()