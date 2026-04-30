import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

# Файл для хранения истории
HISTORY_FILE = "history.json"

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # Загрузка истории
        self.history = self.load_history()

        # Переменные
        self.password_length = tk.IntVar(value=12)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)

        # Интерфейс
        self.create_widgets()
        self.update_history_table()

    # ------------------- Генерация пароля -------------------
    def generate_password(self):
        length = self.password_length.get()

        # Проверка длины
        if length < 4:
            messagebox.showwarning("Ошибка", "Минимальная длина пароля — 4 символа.")
            return
        if length > 50:
            messagebox.showwarning("Ошибка", "Максимальная длина пароля — 50 символов.")
            return

        # Сбор символов
        chars = ""
        if self.use_digits.get():
            chars += string.digits
        if self.use_letters.get():
            chars += string.ascii_letters
        if self.use_symbols.get():
            chars += string.punctuation

        if not chars:
            messagebox.showwarning("Ошибка", "Выберите хотя бы один тип символов.")
            return

        # Генерация
        password = ''.join(random.choice(chars) for _ in range(length))

        # Вывод
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

        # Сохранение в историю
        self.save_to_history(password, length)

    # ------------------- Работа с историей -------------------
    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_history_to_file(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)

    def save_to_history(self, password, length):
        entry = {
            "password": password,
            "length": length,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "digits": self.use_digits.get(),
            "letters": self.use_letters.get(),
            "symbols": self.use_symbols.get()
        }
        self.history.insert(0, entry)  # новые сверху
        if len(self.history) > 20:     # ограничим историю
            self.history = self.history[:20]
        self.save_history_to_file()
        self.update_history_table()

    def clear_history(self):
        if messagebox.askyesno("Очистка", "Удалить всю историю паролей?"):
            self.history = []
            self.save_history_to_file()
            self.update_history_table()

    # ------------------- GUI -------------------
    def create_widgets(self):
        # Рамка генерации
        gen_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        gen_frame.pack(fill="x", padx=10, pady=5)

        # Ползунок длины
        ttk.Label(gen_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w")
        self.length_scale = ttk.Scale(gen_frame, from_=4, to=50, variable=self.password_length, orient="horizontal")
        self.length_scale.grid(row=0, column=1, padx=10, sticky="ew")
        self.length_label = ttk.Label(gen_frame, textvariable=self.password_length)
        self.length_label.grid(row=0, column=2)
        gen_frame.columnconfigure(1, weight=1)

        # Чекбоксы
        ttk.Checkbutton(gen_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(gen_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(gen_frame, text="Спецсимволы (!@#$...)", variable=self.use_symbols).grid(row=1, column=2, sticky="w")

        # Кнопка генерации
        ttk.Button(gen_frame, text="Сгенерировать пароль", command=self.generate_password).grid(row=2, column=0, columnspan=3, pady=10)

        # Поле для пароля
        self.password_entry = ttk.Entry(gen_frame, font=("Courier", 12), width=40)
        self.password_entry.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")
        gen_frame.columnconfigure(0, weight=1)

        # Кнопка копирования (простая)
        ttk.Button(gen_frame, text="Копировать в буфер", command=self.copy_to_clipboard).grid(row=4, column=0, columnspan=3)

        # История
        history_frame = ttk.LabelFrame(self.root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Таблица
        columns = ("date", "password", "length", "charset")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)
        self.tree.heading("date", text="Дата/время")
        self.tree.heading("password", text="Пароль")
        self.tree.heading("length", text="Длина")
        self.tree.heading("charset", text="Типы символов")
        self.tree.column("password", width=200)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка очистки истории
        ttk.Button(history_frame, text="Очистить историю", command=self.clear_history).pack(pady=5)

    def update_history_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for entry in self.history:
            charset = ""
            if entry["digits"]: charset += "Цифры "
            if entry["letters"]: charset += "Буквы "
            if entry["symbols"]: charset += "Спецсимволы "
            if not charset: charset = "Нет"
            self.tree.insert("", "end", values=(
                entry["date"],
                entry["password"],
                entry["length"],
                charset.strip()
            ))

    def copy_to_clipboard(self):
        pwd = self.password_entry.get()
        if pwd:
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена")
        else:
            messagebox.showwarning("Внимание", "Нет сгенерированного пароля")

# ------------------- Запуск -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()