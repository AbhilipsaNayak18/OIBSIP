import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime
import matplotlib.pyplot as plt

# ---------------- DATABASE ----------------
conn = sqlite3.connect("bmi_data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS bmi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    weight REAL,
    height REAL,
    bmi REAL,
    category TEXT,
    date TEXT
)
""")
conn.commit()

last_bmi = None
dark_mode = False

# ---------------- FUNCTIONS ----------------
def calculate_bmi():
    global last_bmi

    try:
        w = float(weight_entry.get())
        h = float(height_entry.get()) / 100

        if w <= 0 or h <= 0:
            raise ValueError

        bmi = round(w / (h*h), 2)

        if bmi < 18.5:
            cat = "Underweight"
            color = "#3498db"
        elif bmi < 25:
            cat = "Normal"
            color = "#2ecc71"
        elif bmi < 30:
            cat = "Overweight"
            color = "#f39c12"
        else:
            cat = "Obese"
            color = "#e74c3c"

        result_var.set(f"BMI: {bmi}")
        category_var.set(cat)
        result_label.config(fg=color)

        # Improvement logic
        improvement = ""
        if last_bmi is not None:
            if bmi < last_bmi:
                improvement = "⬇ Improved!"
            elif bmi > last_bmi:
                improvement = "⬆ Increased"
            else:
                improvement = "No change"

        improvement_var.set(improvement)
        last_bmi = bmi

    except:
        messagebox.showerror("Error", "Enter valid input!")

def save_data():
    if result_var.get() == "":
        messagebox.showwarning("Warning", "Calculate BMI first!")
        return

    name = name_entry.get()
    w = weight_entry.get()
    h = height_entry.get()
    bmi = result_var.get().replace("BMI: ","")
    cat = category_var.get()
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute("INSERT INTO bmi VALUES(NULL,?,?,?,?,?,?)",
                   (name, w, h, bmi, cat, date))
    conn.commit()
    load_data()

def load_data():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT * FROM bmi")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

def search():
    key = search_entry.get()

    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT * FROM bmi WHERE name LIKE ?", ('%'+key+'%',))
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

def export_csv():
    file = filedialog.asksaveasfilename(defaultextension=".csv")
    if file:
        cursor.execute("SELECT * FROM bmi")
        data = cursor.fetchall()

        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID","Name","Weight","Height","BMI","Category","Date"])
            writer.writerows(data)

        messagebox.showinfo("Done", "Exported!")

def show_graph():
    cursor.execute("SELECT date, bmi FROM bmi")
    data = cursor.fetchall()

    if not data:
        messagebox.showwarning("No Data", "No records found!")
        return

    dates = [d[0] for d in data]
    bmis = [float(d[1]) for d in data]

    plt.figure()
    plt.plot(dates, bmis, marker='o')
    plt.xticks(rotation=40)
    plt.title("BMI Trend Graph")
    plt.tight_layout()
    plt.show()

def clear():
    name_entry.delete(0, tk.END)
    weight_entry.delete(0, tk.END)
    height_entry.delete(0, tk.END)
    result_var.set("")
    category_var.set("")
    improvement_var.set("")

def toggle_dark():
    global dark_mode
    dark_mode = not dark_mode

    bg = "#121212" if dark_mode else "#f4f6f7"
    fg = "white" if dark_mode else "black"
    card = "#1e1e1e" if dark_mode else "white"

    root.configure(bg=bg)
    main.configure(bg=bg)
    left.configure(bg=card)
    right.configure(bg=card)

    for widget in left.winfo_children():
        try:
            widget.configure(bg=card, fg=fg)
        except:
            pass

# ---------------- UI ----------------
root = tk.Tk()
root.title("BMI Health Tracker")
root.geometry("1100x600")
root.configure(bg="#f4f6f7")

tk.Label(root, text="BMI Health Tracker",
         font=("Segoe UI", 24, "bold"),
         bg="#f4f6f7").pack(pady=5)

tk.Label(root, text="Track your BMI, monitor progress, and improve your health",
         font=("Segoe UI", 11),
         fg="gray",
         bg="#f4f6f7").pack()

main = tk.Frame(root, bg="#f4f6f7")
main.pack(fill="both", expand=True, padx=10, pady=10)

# LEFT PANEL
left = tk.Frame(main, bg="white", bd=2, relief="groove")
left.pack(side="left", fill="y", padx=10)

tk.Label(left, text="Enter Details",
         font=("Segoe UI", 14, "bold"),
         bg="white").pack(pady=10)

def input_field(label):
    tk.Label(left, text=label, bg="white").pack()
    e = tk.Entry(left)
    e.pack(pady=5)
    return e

name_entry = input_field("Name")
weight_entry = input_field("Weight (kg)")
height_entry = input_field("Height (cm)")

tk.Button(left, text="Calculate BMI",
          bg="#3498db", fg="white",
          command=calculate_bmi).pack(pady=5)

tk.Button(left, text="Save Result",
          bg="#2ecc71", fg="white",
          command=save_data).pack(pady=5)

tk.Button(left, text="Clear", command=clear).pack(pady=5)

tk.Button(left, text="🌙 Toggle Dark Mode",
          command=toggle_dark).pack(pady=5)

tk.Label(left, text="Result",
         font=("Segoe UI", 12, "bold"),
         bg="white").pack(pady=10)

result_var = tk.StringVar()
category_var = tk.StringVar()
improvement_var = tk.StringVar()

result_label = tk.Label(left, textvariable=result_var,
                        font=("Segoe UI", 16, "bold"),
                        bg="white")
result_label.pack()

tk.Label(left, textvariable=category_var,
         font=("Segoe UI", 12),
         bg="white").pack()

tk.Label(left, textvariable=improvement_var,
         font=("Segoe UI", 10, "italic"),
         fg="gray",
         bg="white").pack()

# RIGHT PANEL
right = tk.Frame(main, bg="white", bd=2, relief="groove")
right.pack(side="right", fill="both", expand=True)

top = tk.Frame(right, bg="white")
top.pack(fill="x", pady=5)

tk.Button(top, text="View History", command=load_data).pack(side="left", padx=5)
tk.Button(top, text="Graph", command=show_graph).pack(side="left", padx=5)
tk.Button(top, text="Export CSV", command=export_csv).pack(side="left", padx=5)

search_entry = tk.Entry(top)
search_entry.pack(side="left", padx=10)

tk.Button(top, text="Search", command=search).pack(side="left")

cols = ("ID","Name","Weight","Height","BMI","Category","Date")
tree = ttk.Treeview(right, columns=cols, show="headings")

for col in cols:
    tree.heading(col, text=col)
    tree.column(col, anchor="center")

tree.pack(fill="both", expand=True)

load_data()
root.mainloop()