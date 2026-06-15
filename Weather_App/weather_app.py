import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
from datetime import datetime

# ---------- CONFIGURATION ----------
API_KEY = "aeb2da95a65f92c7e1d78b4073e22a2b"   # Replace with your OpenWeatherMap key
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
# ----------------------------------

# Emoji mapping for weather conditions (based on OpenWeatherMap icon codes)
def get_weather_emoji(icon_code):
    mapping = {
        "01d": "☀️", "01n": "🌙",
        "02d": "⛅", "02n": "☁️",
        "03d": "☁️", "03n": "☁️",
        "04d": "☁️", "04n": "☁️",
        "09d": "🌧️", "09n": "🌧️",
        "10d": "🌦️", "10n": "🌧️",
        "11d": "⛈️", "11n": "⛈️",
        "13d": "❄️", "13n": "❄️",
        "50d": "🌫️", "50n": "🌫️"
    }
    return mapping.get(icon_code, "🌡️")

def fetch_weather_and_forecast(location):
    # ---- Current weather ----
    if location.isdigit():
        params = {"zip": f"{location},us", "appid": API_KEY, "units": "metric"}
    else:
        params = {"q": location, "appid": API_KEY, "units": "metric"}

    try:
        resp = requests.get(CURRENT_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

        city = data["name"]
        country = data["sys"]["country"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind_speed = data["wind"]["speed"]
        desc = data["weather"][0]["description"].capitalize()
        icon_code = data["weather"][0]["icon"]
        emoji = get_weather_emoji(icon_code)

        # Update current weather display
        current_text = (
            f"{emoji} {city}, {country}\n"
            f"🌡️ {temp}°C (feels like {feels_like}°C)\n"
            f"💧 Humidity: {humidity}%\n"
            f"⚡ Pressure: {pressure} hPa\n"
            f"💨 Wind: {wind_speed} m/s\n"
            f"☁️ {desc}"
        )
        label_current.config(text=current_text)

        # ---- 5‑day forecast (3‑hour intervals) ----
        forecast_params = {
            "lat": data["coord"]["lat"],
            "lon": data["coord"]["lon"],
            "appid": API_KEY,
            "units": "metric"
        }
        forecast_resp = requests.get(FORECAST_URL, params=forecast_params)
        forecast_resp.raise_for_status()
        forecast_data = forecast_resp.json()

        # Clear previous forecast
        forecast_textbox.config(state=tk.NORMAL)
        forecast_textbox.delete(1.0, tk.END)

        # Group forecast by day (simple grouping)
        last_date = None
        for entry in forecast_data["list"]:
            dt = datetime.fromtimestamp(entry["dt"])
            date_str = dt.strftime("%a, %d %b")
            time_str = dt.strftime("%H:%M")
            temp_f = entry["main"]["temp"]
            desc_f = entry["weather"][0]["description"].capitalize()
            icon_f = entry["weather"][0]["icon"]
            emoji_f = get_weather_emoji(icon_f)

            if date_str != last_date:
                forecast_textbox.insert(tk.END, f"\n📅 {date_str}\n", "date")
                last_date = date_str

            forecast_textbox.insert(
                tk.END,
                f"   {time_str}  {emoji_f}  {temp_f}°C  -  {desc_f}\n"
            )

        forecast_textbox.config(state=tk.DISABLED)

    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401:
            messagebox.showerror("API Error", "Invalid API key.")
        elif resp.status_code == 404:
            messagebox.showerror("Location Error", f"'{location}' not found.")
        else:
            messagebox.showerror("HTTP Error", str(e))
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Network Error", "No internet connection.")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

def get_location_from_ip():
    """Use ipinfo.io to get approximate city name from IP address."""
    try:
        resp = requests.get("https://ipinfo.io/json", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        city = data.get("city", "")
        if city:
            entry_location.delete(0, tk.END)
            entry_location.insert(0, city)
            fetch_weather_and_forecast(city)
        else:
            messagebox.showinfo("Auto‑detect", "Could not detect your city. Please enter manually.")
    except Exception:
        messagebox.showerror("Auto‑detect Error", "Failed to detect location. Check your internet.")

# ---------- BUILD GUI ----------
root = tk.Tk()
root.title("Advanced Weather App")
root.geometry("600x500")
root.resizable(True, True)

# Style
bg_color = "#f0f4fa"
root.configure(bg=bg_color)

# Header frame
header = tk.Frame(root, bg=bg_color)
header.pack(pady=10)

tk.Label(header, text="🌤️ Weather App", font=("Segoe UI", 20, "bold"), bg=bg_color).pack()

# Input frame
input_frame = tk.Frame(root, bg=bg_color)
input_frame.pack(pady=10)

tk.Label(input_frame, text="City or ZIP:", font=("Segoe UI", 11), bg=bg_color).grid(row=0, column=0, padx=5)
entry_location = tk.Entry(input_frame, width=25, font=("Segoe UI", 11))
entry_location.grid(row=0, column=1, padx=5)
entry_location.bind("<Return>", lambda event: fetch_weather_and_forecast(entry_location.get().strip()))

btn_frame = tk.Frame(input_frame, bg=bg_color)
btn_frame.grid(row=0, column=2, padx=10)

tk.Button(btn_frame, text="Get Weather", command=lambda: fetch_weather_and_forecast(entry_location.get().strip()),
          bg="#4CAF50", fg="white", font=("Segoe UI", 10), padx=10).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="📍 Auto‑Detect", command=get_location_from_ip,
          bg="#2196F3", fg="white", font=("Segoe UI", 10), padx=10).pack(side=tk.LEFT)

# Current weather display
current_frame = tk.Frame(root, bg="white", relief=tk.GROOVE, bd=2)
current_frame.pack(pady=10, padx=20, fill=tk.X)

label_current = tk.Label(current_frame, text="", font=("Segoe UI", 12), justify=tk.LEFT, bg="white", padx=10, pady=10)
label_current.pack(anchor="w")

# Forecast header
tk.Label(root, text="📆 5‑Day Forecast (3‑hour steps)", font=("Segoe UI", 14, "bold"), bg=bg_color).pack(pady=(10,0))

# Scrollable forecast area
forecast_frame = tk.Frame(root)
forecast_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

forecast_textbox = scrolledtext.ScrolledText(forecast_frame, height=12, font=("Consolas", 10), wrap=tk.WORD)
forecast_textbox.pack(fill=tk.BOTH, expand=True)

# Configure tag for date headings
forecast_textbox.tag_config("date", foreground="blue", font=("Segoe UI", 11, "bold"))

# Disable editing initially
forecast_textbox.config(state=tk.DISABLED)

# Run
root.mainloop()