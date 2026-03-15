import requests
import tkinter as tk
from tkinter import filedialog, messagebox

# ВСТАВЬ СЮДА АДРЕС СВОЕГО СЕРВЕРА Render
SERVER = ""

token = None
attempts = 0


def login():

    global token, attempts

    login = login_entry.get()
    password = password_entry.get()

    try:

        r = requests.post(
            SERVER + "/api/login",
            json={"login": login, "password": password}
        )

        if r.status_code == 200:

            data = r.json()

            token = data["token"]
            attempts = data["attempts"]

            status_label.config(text="Login successful")
            attempts_label.config(text=f"Attempts: {attempts}")

        else:
            messagebox.showerror("Error", "Login failed")

    except:
        messagebox.showerror("Error", "Server connection failed")


def scan_file():

    global attempts

    if token is None:
        messagebox.showerror("Error", "Login first")
        return

    file_path = filedialog.askopenfilename()

    if not file_path:
        return

    try:

        files = {"file": open(file_path, "rb")}

        headers = {"Authorization": token}

        r = requests.post(
            SERVER + "/api/scan",
            files=files,
            headers=headers
        )

        result_label.config(text=r.text)

        if "File scanned" in r.text:
            attempts -= 1
            attempts_label.config(text=f"Attempts: {attempts}")

    except:
        messagebox.showerror("Error", "Scan failed")


# GUI

root = tk.Tk()
root.title("Antivirus Client")
root.geometry("350x300")

tk.Label(root, text="Login").pack(pady=5)
login_entry = tk.Entry(root)
login_entry.pack()

tk.Label(root, text="Password").pack(pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.pack()

tk.Button(root, text="Login", command=login).pack(pady=10)

attempts_label = tk.Label(root, text="Attempts: 0")
attempts_label.pack()

tk.Button(root, text="Scan File", command=scan_file).pack(pady=10)

status_label = tk.Label(root, text="")
status_label.pack()

result_label = tk.Label(root, text="")
result_label.pack()

root.mainloop()