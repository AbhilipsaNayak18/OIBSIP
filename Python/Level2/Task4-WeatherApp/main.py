import tkinter as tk
from tkinter import messagebox, filedialog
import requests
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime
import sqlite3

API_KEY = "7389a78b1eb75aee3d91c2a99e84c9f9"

# ---------------- DATABASE ----------------
conn = sqlite3.connect("weather.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS history(city TEXT)")
conn.commit()

# ---------------- WINDOW ----------------
root = tk.Tk()
root.title("🌦 Professional Weather App")
root.geometry("800x800")

dark_mode = True
unit = "metric"

# ---------------- FUNCTIONS ----------------
def format_time(ts):
    return datetime.fromtimestamp(ts).strftime("%H:%M")

def save_history(city):
    cursor.execute("INSERT INTO history VALUES(?)", (city,))
    conn.commit()
    load_history()

def load_history():
    cursor.execute("SELECT city FROM history ORDER BY rowid DESC LIMIT 5")
    data = cursor.fetchall()
    history_label.config(text="Recent: " + ", ".join([i[0] for i in data]))

def fetch_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit}"
        data = requests.get(url).json()

        if data["cod"] != 200:
            raise Exception(data["message"])

        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        desc = data["weather"][0]["description"]
        icon = data["weather"][0]["icon"]
        sunrise = format_time(data["sys"]["sunrise"])
        sunset = format_time(data["sys"]["sunset"])
        country = data["sys"]["country"]

        unit_symbol = "°C" if unit == "metric" else "°F"

        result_text.set(f"{desc.capitalize()} • {temp}{unit_symbol}")
        location_text.set(f"{city}, {country}")

        details_text.set(
            f"Feels Like: {feels}{unit_symbol}\nHumidity: {humidity}%\nPressure: {pressure} hPa\n"
            f"Wind: {wind} m/s\nSunrise: {sunrise}\nSunset: {sunset}"
        )

        # ICON
        img_data = requests.get(f"http://openweathermap.org/img/wn/{icon}@2x.png").content
        img = Image.open(BytesIO(img_data))
        img = ImageTk.PhotoImage(img)
        icon_label.config(image=img)
        icon_label.image = img

        # FORECAST
        f_data = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={unit}"
        ).json()

        hourly = "⏰ Hourly:\n"
        for i in range(6):
            t = f_data["list"][i]
            time = t["dt_txt"].split()[1][:5]
            hourly += f"{time} → {t['main']['temp']}{unit_symbol}, {t['weather'][0]['description']}\n"

        daily = "📅 5-Day:\n"
        for i in range(0, 40, 8):
            t = f_data["list"][i]
            date = t["dt_txt"].split()[0]
            daily += f"{date} → {t['main']['temp']}{unit_symbol}, {t['weather'][0]['description']}\n"

        forecast_text.set(hourly + "\n" + daily)

        save_history(city)
        status_label.config(text="Loaded successfully", fg="green")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def get_weather():
    city = city_entry.get()
    if not city:
        messagebox.showwarning("Input Error", "Enter city")
        return
    fetch_weather(city)

def auto_location():
    try:
        city = requests.get("https://ipinfo.io/json").json()["city"]
        city_entry.delete(0, tk.END)
        city_entry.insert(0, city)
        fetch_weather(city)
    except:
        messagebox.showerror("Error", "Location failed")

def clear():
    city_entry.delete(0, tk.END)
    result_text.set("")
    location_text.set("")
    details_text.set("")
    forecast_text.set("")
    icon_label.config(image="")

def toggle_unit():
    global unit
    unit = "imperial" if unit == "metric" else "metric"
    get_weather()

def export_report():
    file = filedialog.asksaveasfilename(defaultextension=".txt")
    if file:
        with open(file, "w") as f:
            f.write(location_text.get() + "\n")
            f.write(result_text.get() + "\n")
            f.write(details_text.get() + "\n")
            f.write(forecast_text.get())
        messagebox.showinfo("Saved", "Report exported!")

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode

    bg = "#0f172a" if dark_mode else "#f1f5f9"
    fg = "white" if dark_mode else "black"
    card = "#1e293b" if dark_mode else "#e2e8f0"

    root.config(bg=bg)
    top_frame.config(bg=bg)
    card_frame.config(bg=card)

    for w in [title, result_label, location_label, details_label]:
        w.config(bg=card, fg=fg)

# ---------------- UI ----------------
title = tk.Label(root, text="🌦 Professional Weather App", font=("Arial", 20, "bold"))
title.pack(pady=10)

top_frame = tk.Frame(root)
top_frame.pack()

city_entry = tk.Entry(top_frame, width=25)
city_entry.grid(row=0, column=0)

tk.Button(top_frame, text="Get", command=get_weather).grid(row=0, column=1)
tk.Button(top_frame, text="Clear", command=clear).grid(row=0, column=2)
tk.Button(top_frame, text="Refresh", command=get_weather).grid(row=0, column=3)
tk.Button(top_frame, text="Auto", command=auto_location).grid(row=0, column=4)
tk.Button(top_frame, text="°C/°F", command=toggle_unit).grid(row=0, column=5)
tk.Button(top_frame, text="Theme", command=toggle_theme).grid(row=0, column=6)
tk.Button(top_frame, text="Export", command=export_report).grid(row=0, column=7)

status_label = tk.Label(root, text="")
status_label.pack()

card_frame = tk.Frame(root, bd=2, relief="ridge")
card_frame.pack(fill="both", expand=True, padx=10, pady=10)

icon_label = tk.Label(card_frame)
icon_label.pack()

result_text = tk.StringVar()
result_label = tk.Label(card_frame, textvariable=result_text, font=("Arial", 16))
result_label.pack()

location_text = tk.StringVar()
location_label = tk.Label(card_frame, textvariable=location_text)
location_label.pack()

details_text = tk.StringVar()
details_label = tk.Label(card_frame, textvariable=details_text, justify="left")
details_label.pack()

forecast_text = tk.StringVar()
forecast_label = tk.Label(card_frame, textvariable=forecast_text, justify="left")
forecast_label.pack()

history_label = tk.Label(root, text="Recent:")
history_label.pack()

load_history()

root.mainloop()