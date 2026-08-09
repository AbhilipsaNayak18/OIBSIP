import tkinter as tk
from tkinter import messagebox, filedialog
import string
import secrets
import pyperclip

# ---------------- WINDOW ----------------
root = tk.Tk()
root.title("🔥 Advanced Password Generator")
root.geometry("520x650")

dark_mode = True

# ---------------- COLORS ----------------
def apply_theme():
    bg = "#1e1e2f" if dark_mode else "#f5f5f5"
    fg = "white" if dark_mode else "black"

    root.config(bg=bg)
    for widget in root.winfo_children():
        try:
            widget.config(bg=bg, fg=fg)
        except:
            pass

# ---------------- VARIABLES ----------------
length_var = tk.IntVar(value=12)
upper_var = tk.BooleanVar(value=True)
lower_var = tk.BooleanVar(value=True)
digit_var = tk.BooleanVar(value=True)
symbol_var = tk.BooleanVar(value=False)
exclude_var = tk.BooleanVar(value=False)
show_password = tk.BooleanVar(value=False)

password_history = []

# ---------------- FUNCTIONS ----------------
def generate_password():
    length = length_var.get()

    if length < 8:
        messagebox.showerror("Error", "Minimum length is 8")
        return

    char_sets = []
    password_chars = []

    if upper_var.get():
        chars = string.ascii_uppercase
        char_sets.append(chars)
        password_chars.append(secrets.choice(chars))

    if lower_var.get():
        chars = string.ascii_lowercase
        char_sets.append(chars)
        password_chars.append(secrets.choice(chars))

    if digit_var.get():
        chars = string.digits
        char_sets.append(chars)
        password_chars.append(secrets.choice(chars))

    if symbol_var.get():
        chars = string.punctuation
        char_sets.append(chars)
        password_chars.append(secrets.choice(chars))

    if not char_sets:
        messagebox.showerror("Error", "Select at least one character type")
        return

    all_chars = ''.join(char_sets)

    if exclude_var.get():
        for ch in "0O1l":
            all_chars = all_chars.replace(ch, '')

    while len(password_chars) < length:
        password_chars.append(secrets.choice(all_chars))

    secrets.SystemRandom().shuffle(password_chars)
    password = ''.join(password_chars)

    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)

    update_strength(password)
    save_history(password)

    pyperclip.copy(password)

def update_strength(password):
    score = 0

    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in string.punctuation for c in password):
        score += 1

    if score <= 2:
        strength_label.config(text="Weak", fg="red")
    elif score <= 4:
        strength_label.config(text="Medium", fg="orange")
    else:
        strength_label.config(text="Strong", fg="green")

def copy_password():
    pwd = password_entry.get()
    if pwd:
        pyperclip.copy(pwd)
        messagebox.showinfo("Copied", "Password copied!")

def save_history(password):
    global password_history
    password_history.insert(0, password)

    if len(password_history) > 5:
        password_history = password_history[:5]

    history_box.delete(0, tk.END)
    for p in password_history:
        history_box.insert(tk.END, p)

def toggle_visibility():
    if show_password.get():
        password_entry.config(show="")
    else:
        password_entry.config(show="*")

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()

def save_to_file():
    passwords = history_box.get(0, tk.END)
    if not passwords:
        messagebox.showwarning("No Data", "No passwords to save")
        return

    file = filedialog.asksaveasfilename(defaultextension=".txt",
                                        filetypes=[("Text Files", "*.txt")])
    if file:
        with open(file, "w") as f:
            for p in passwords:
                f.write(p + "\n")
        messagebox.showinfo("Saved", "Passwords saved successfully!")

# ---------------- UI ----------------
title = tk.Label(root, text="🔐 Password Generator", font=("Arial", 18, "bold"))
title.pack(pady=10)

password_entry = tk.Entry(root, font=("Arial", 14), width=30, show="*")
password_entry.pack(pady=10)

tk.Checkbutton(root, text="Show Password", variable=show_password,
               command=toggle_visibility).pack()

tk.Button(root, text="Generate Password", command=generate_password,
          bg="#4CAF50", fg="white").pack(pady=10)

tk.Button(root, text="Copy", command=copy_password,
          bg="#2196F3", fg="white").pack(pady=5)

tk.Button(root, text="💾 Save to File", command=save_to_file,
          bg="#9C27B0", fg="white").pack(pady=5)

tk.Button(root, text="🌙 Toggle Theme", command=toggle_theme).pack(pady=5)

# Length
tk.Label(root, text="Length").pack()
tk.Scale(root, from_=8, to=32, orient="horizontal",
         variable=length_var).pack()

# Options
tk.Checkbutton(root, text="Uppercase", variable=upper_var).pack(anchor='w', padx=120)
tk.Checkbutton(root, text="Lowercase", variable=lower_var).pack(anchor='w', padx=120)
tk.Checkbutton(root, text="Numbers", variable=digit_var).pack(anchor='w', padx=120)
tk.Checkbutton(root, text="Symbols", variable=symbol_var).pack(anchor='w', padx=120)
tk.Checkbutton(root, text="Exclude 0,O,l,1", variable=exclude_var).pack(anchor='w', padx=120)

# Strength
tk.Label(root, text="Strength").pack(pady=5)
strength_label = tk.Label(root, text="--", font=("Arial", 12, "bold"))
strength_label.pack()

# History
tk.Label(root, text="Last 5 Passwords").pack()
history_box = tk.Listbox(root, height=5)
history_box.pack(pady=10)

apply_theme()
root.mainloop()