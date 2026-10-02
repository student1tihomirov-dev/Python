import os
import random
import tkinter as tk
from tkinter import ttk, messagebox

USERS = [
    {"login": "admin", "password": "admin", "role": "Администратор", "locked": False, "attempts": 0},
    {"login": "ivanov", "password": "1234", "role": "Пользователь", "locked": True, "attempts": 3},
    {"login": "petrov", "password": "qwerty", "role": "Пользователь", "locked": False, "attempts": 0},
]

def all_users():
    return USERS

def find_user(login, password):
    for u in USERS:
        if u["login"] == login and u["password"] == password:
            return u
    return None

def login_exists(login):
    for u in USERS:
        if u["login"] == login:
            return True
    return False

def add_user(login, password, role):
    USERS.append({"login": login, "password": password, "role": role, "locked": False, "attempts": 0})

def register_fail(login):
    for u in USERS:
        if u["login"] == login:
            u["attempts"] = u["attempts"] + 1
            if u["attempts"] >= 3:
                u["locked"] = True
                return True
            return False
    return False

def reset_attempts(login):
    for u in USERS:
        if u["login"] == login:
            u["attempts"] = 0
            return True
    return False

def unlock_user(login):
    for u in USERS:
        if u["login"] == login:
            u["locked"] = False
            u["attempts"] = 0
            return True
    return False

CURRENT_USER = None
BG = "#f9f1e5"
FIELD_BG = "#ffffff"
FIELD_FG = "#22262b"
PRIMARY_BG = "#1e5fd0"
PRIMARY_FG = "#ffffff"
SECOND_BG = "#e5e7eb"
SECOND_FG = "#111827"
FONT_TITLE = ("Arial", 16, "bold")
FONT_LABEL = ("Arial", 11, "bold")
FONT_BUTTON = ("Arial", 12, "bold")

root = tk.Tk()
root.title("Учебное приложение")
root.geometry("640x650")
root.configure(bg=BG)

container = tk.Frame(root, bg=BG)
container.pack(fill="both", expand=True, padx=20, pady=20)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAPTCHA_DIR = os.path.join(BASE_DIR, "captcha")
CORRECT_ORDER = [1, 2, 4, 3]
PIECE_SIZE = 110
captcha_images = {}
captcha_host = None
captcha_slots = []
captcha_piece_buttons = {}
captcha_placed = []
captcha_shuffled = []
captcha_passed = True

ENTRY_LOGIN = None

def clear_screen():
    for w in container.winfo_children():
        w.destroy()

def make_title(text):
    return tk.Label(container, text=text, bg=BG, fg=FIELD_FG, font=FONT_TITLE)

def make_label(text):
    return tk.Label(container, text=text, bg=BG, fg=FIELD_FG, font=FONT_LABEL, anchor="w")

def make_entry(password=False):
    entry = tk.Entry(container, font=FONT_BUTTON, bg=FIELD_BG, fg=FIELD_FG,
                     insertbackground=FIELD_FG, relief="solid", borderwidth=1)
    if password:
        entry.configure(show="*")
    return entry

def make_button(text, command, primary=True, parent=None):
    host = container if parent is None else parent
    if primary:
        return tk.Button(host, text=text, command=command,
                         bg=PRIMARY_BG, fg=PRIMARY_FG,
                         activebackground="#174ea6", activeforeground=PRIMARY_FG,
                         font=FONT_BUTTON, relief="flat", cursor="hand2")

    return tk.Button(host, text=text, command=command,
                     bg=SECOND_BG, fg=SECOND_FG,
                     activebackground="#d7dade", activeforeground=SECOND_FG,
                     font=FONT_LABEL, relief="flat", cursor="hand2")

def try_login(login, password):
    global CURRENT_USER
    login = login.strip()
    if not login or not password:
        messagebox.showwarning("Внимание", "Заполните логин и пароль.")
        return
    if not captcha_passed:
        messagebox.showwarning("Капча", "Сначала соберите капчу, затем нажимайте «Войти».")
        return
    user = find_user(login, password)
    if user is None:
        became_locked = register_fail(login)
        if became_locked:
            messagebox.showerror("Блокировка", "Вы заблокированы. Обратитесь к администратору")
        else:
            messagebox.showerror("Ошибка входа", "Вы ввели неверный логин или пароль. Пожалуйста проверьте ещё раз введенные данные")
        return
    if user["locked"]:
        messagebox.showerror("Блокировка", "Вы заблокированы. Обратитесь к администратору")
        return
    reset_attempts(login)
    CURRENT_USER = user
    messagebox.showinfo("Авторизация", "Вы успешно авторизовались")
    user_role = user["role"]
    if user_role == "Администратор":
        open_admin()
    else:
        open_user()

def open_login():
    global ENTRY_LOGIN
    clear_screen()
    make_title("Вход в систему").pack(pady=(0, 10))
    make_label("Логин").pack(fill="x")
    ENTRY_LOGIN = make_entry()
    ENTRY_LOGIN.pack(fill="x", pady=(0, 8))
    ENTRY_LOGIN.insert(0, "admin")
    make_label("Пароль").pack(fill="x")
    entry_pass = make_entry(password=True)
    entry_pass.pack(fill="x", pady=(0, 12))
    make_button("Войти", lambda: try_login(ENTRY_LOGIN.get(), entry_pass.get())).pack(fill="x", ipady=6)
    make_button("О программе", open_about, primary=False).pack(fill="x", pady=(8, 0), ipady=4)

def open_about():
    clear_screen()
    tk.Label(container, text="Учебное приложение", bg=BG, fg=PRIMARY_BG, font=("Arial", 20, "bold")).pack(pady=(30, 6))
    tk.Label(container, text="Модуль 4. Демонстрационный экзамен 09.02.07", bg=BG, fg=FIELD_FG, font=FONT_BUTTON).pack(pady=(0, 4))
    tk.Label(container, text="Версия 1.0, данные пока хранятся в списке", bg=BG, fg=FIELD_FG, font=FONT_LABEL).pack(pady=(0, 25))
    make_button("Назад", open_login, primary=False).pack(ipadx=30, ipady=5)

def open_user():
    clear_screen()
    make_title("Рабочее место пользователя").pack(pady=(0, 10))
    make_label("Вы вошли как: " + CURRENT_USER["login"]).pack(fill="x", pady=(0, 6))
    make_label("Роль: " + CURRENT_USER["role"]).pack(fill="x", pady=(0, 20))
    make_button("Выйти", open_login, primary=False).pack(ipadx=24, ipady=4)

def unlock_selected(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Внимание", "Сначала выберите строку в таблице.")
        return
    login = tree.item(selected[0])["values"][0]
    unlock_user(login)
    messagebox.showinfo("Готово", "Пользователь " + str(login) + " разблокирован.")
    open_admin()

def open_admin():
    clear_screen()
    make_title("Панель администратора").pack(pady=(0, 5))
    make_label("Вы вошли как: " + CURRENT_USER["login"]).pack(fill="x", pady=(0, 10))
    tree = ttk.Treeview(container, columns=("login", "role", "locked"), show="headings", height=8)
    tree.heading("login", text="Логин")
    tree.heading("role", text="Роль")
    tree.heading("locked", text="Заблокирован")
    tree.column("login", width=180, anchor="w")
    tree.column("role", width=160, anchor="w")
    tree.column("locked", width=120, anchor="center")
    for u in all_users():
        tree.insert("", "end", values=(u["login"], u["role"], "да" if u["locked"] else "нет"))
    tree.pack(fill="both", expand=True, pady=(0, 10))
    row = tk.Frame(container, bg=BG)
    row.pack(fill="x")
    make_button("Добавить", open_add_user, parent=row).pack(side="left", padx=(0, 6))
    make_button("Разблокировать", lambda: unlock_selected(tree), primary=False, parent=row).pack(side="left", padx=(0, 6))
    make_button("Оформление", open_style, primary=False, parent=row).pack(side="left", padx=(0, 6))
    make_button("Выйти", open_login, primary=False, parent=row).pack(side="right")

def save_user(login, password, role):
    login = login.strip()
    if not login or not password:
        messagebox.showwarning("Внимание", "Логин и пароль не могут быть пустыми.")
        return
    if login_exists(login):
        messagebox.showerror("Ошибка", "Такой логин уже существует.")
        return
    add_user(login, password, role)
    messagebox.showinfo("Готово", "Пользователь " + login + " добавлен.")
    open_admin()

def open_add_user():
    clear_screen()
    make_title("Новый пользователь").pack(pady=(0, 15))
    make_label("Логин").pack(fill="x")
    e_login = make_entry()
    e_login.pack(fill="x", pady=(0, 10))
    make_label("Пароль").pack(fill="x")
    e_pass = make_entry()
    e_pass.pack(fill="x", pady=(0, 10))
    make_label("Роль").pack(fill="x")
    combo_role = ttk.Combobox(container, values=["Пользователь", "Администратор"], state="readonly", font=FONT_BUTTON)
    combo_role.current(0)
    combo_role.pack(fill="x", pady=(0, 15))
    make_button("Сохранить", lambda: save_user(e_login.get(), e_pass.get(), combo_role.get())).pack(fill="x", ipady=6)
    make_button("Отмена", open_admin, primary=False).pack(fill="x", pady=(8, 0), ipady=4)

def open_style():
    clear_screen()
    make_title("Оформление").pack(pady=(0, 15))
    make_label("Кнопки меняют цвет плашки ниже.").pack(fill="x", pady=(0, 12))
    preview = tk.Frame(container, bg=FIELD_BG, height=120)
    preview.pack(fill="x", pady=(0, 15))
    preview.pack_propagate(False)
    make_button("Красный", lambda: preview.configure(bg="#ffd6d6"), primary=False).pack(fill="x", ipady=4, pady=(0, 6))
    make_button("Зелёный", lambda: preview.configure(bg="#d6f5e0"), primary=False).pack(fill="x", ipady=4, pady=(0, 6))
    make_button("Синий", lambda: preview.configure(bg="#d6e4ff"), primary=False).pack(fill="x", ipady=4, pady=(0, 6))
    make_button("Назад", open_admin, primary=False).pack(ipadx=30, ipady=5, pady=(10, 0))

open_login()
root.mainloop()
