import sqlite3
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "users.db"




def init_db():
    """Создаёт базу и таблицу users, если их ещё нет."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            role     TEXT    NOT NULL,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            name     TEXT    NOT NULL
        )
    """)
    
    test_users = [
        ("admin",   "admin",   "Админ Админов"),
        ("manager", "1234",    "Менеджер Менеджеров"),
        ("guest",   "guest",   "Гость Гостев"),
    ]
    for role, username, name in test_users:
        cursor.execute(
            "INSERT OR IGNORE INTO users (role, username, password, name) VALUES (?, ?, ?, ?)",
            (role, username, hash_password(username), name),
        )
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Хэширует пароль sha256 (в реальных проектах лучше bcrypt/argon2)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def authenticate(username: str, password: str):
    """Возвращает (name, role) или None, если пара логин/пароль неверна."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, role FROM users WHERE username = ? AND password = ?",
        (username, hash_password(password)),
    )
    row = cursor.fetchone()
    conn.close()
    return row  # (name, role) или None




def open_feed(user_name: str | None, role: str | None):
    """Окно-заглушка «ленты товаров»."""
    feed = tk.Tk()
    if user_name is None:
        feed.title("Лента товаров — гость")
    else:
        feed.title(f"Лента товаров — {user_name}")

    feed.geometry("400x300")

    if user_name is not None:
        greeting = tk.Label(
            feed,
            text=f"Привет, {user_name}!\nВаша роль: {role}",
            font=("Arial", 14, "bold"),
        )
        greeting.pack(pady=15)

    placeholder = tk.Label(
        feed,
        text="Тут будет лента товаров",
        font=("Arial", 12),
        fg="gray",
    )
    placeholder.pack(expand=True)

    feed.mainloop()


def on_login(entry_username: ttk.Entry, entry_password: ttk.Entry, window: tk.Tk):
    username = entry_username.get().strip()
    password = entry_password.get()

    if not username or not password:
        messagebox.showwarning("Ошибка", "Заполните логин и пароль")
        return

    user = authenticate(username, password)
    if user is None:
        messagebox.showerror("Ошибка", "Неверный логин или пароль")
        return

    name, role = user
    window.destroy()
    open_feed(name, role)




def open_login():
    login_window = tk.Tk()
    login_window.title("Авторизация")
    login_window.geometry("300x220")
    login_window.resizable(False, False)

    frame = ttk.Frame(login_window, padding=20)
    frame.pack(expand=True)

    ttk.Label(frame, text="Логин:").grid(row=0, column=0, sticky="w", pady=5)
    entry_username = ttk.Entry(frame, width=25)
    entry_username.grid(row=1, column=0, pady=5)

    ttk.Label(frame, text="Пароль:").grid(row=2, column=0, sticky="w", pady=5)
    entry_password = ttk.Entry(frame, width=25, show="*")
    entry_password.grid(row=3, column=0, pady=5)

    btn_login = ttk.Button(
        frame,
        text="Войти",
        command=lambda: on_login(entry_username, entry_password, login_window),
    )
    btn_login.grid(row=4, column=0, pady=(15, 5), sticky="ew")

    btn_guest = ttk.Button(
        frame,
        text="Войти как гость",
        command=lambda: (login_window.destroy(), open_feed(None, None)),
    )
    btn_guest.grid(row=5, column=0, pady=5, sticky="ew")


    entry_password.bind("<Return>", lambda e: on_login(entry_username, entry_password, login_window))

    login_window.mainloop()


if __name__ == "__main__":
    init_db()
    open_login()
