import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import re
from datetime import datetime


DATA_FILE = "data/expenses.json"
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
expenses = []  # Список для хранения расходов

def load_data():
    """Загружает данные из файла JSON при запуске."""
    global expenses
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                expenses = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            expenses = []

def save_data():
    """Сохраняет список расходов в файл JSON."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(expenses, f, ensure_ascii=False, indent=4)

def add_expense():
    """Обрабатывает нажатие кнопки 'Добавить расход'."""
    amount_str = amount_entry.get()
    category = category_var.get()
    date_str = date_entry.get()

    # Валидация суммы
    if not amount_str.replace('.', '', 1).isdigit() or float(amount_str) <= 0:
        messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
        return

    # Валидация даты (формат ГГГГ-ММ-ДД)
    if not re.match(r"\d{4}-\d{2}-\d{2}", date_str):
        messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД")
        return

    # Добавляем расход в список и сохраняем
    expenses.append({
        "amount": float(amount_str),
        "category": category,
        "date": date_str
    })
    save_data()
    update_table()

def update_table(*args):
    
    # Очищаем таблицу
    for i in tree.get_children():
        tree.delete(i)

    # Копируем список для фильтрации
    filtered = expenses.copy()

    # Фильтр по категории
    cat = filter_category.get()
    if cat != "Все":
        filtered = [e for e in filtered if e["category"] == cat]

    # Фильтр по дате
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()

    if re.match(r"\d{4}-\d{2}-\d{2}", start_date) and re.match(r"\d{4}-\d{2}-\d{2}", end_date):
        filtered = [e for e in filtered if start_date <= e["date"] <= end_date]

    # Заполняем таблицу отфильтрованными данными
    for e in filtered:
        tree.insert("", "end", values=(f"{e['amount']:.2f}", e["category"], e["date"]))

    # Подсчёт и вывод суммы
    total = sum(e["amount"] for e in filtered)
    messagebox.showinfo("Сумма расходов", f"Итого за выбранный период: {total:.2f} ₽")


# --- Создание графического интерфейса (GUI) ---
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("1000x500")

categories = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Прочее"]


# Добавление расхода
frame_add = ttk.LabelFrame(root, text="Добавить расход")
frame_add.pack(pady=10, fill="x")

ttk.Label(frame_add, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
amount_entry = ttk.Entry(frame_add)
amount_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_add, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
category_var = tk.StringVar()
category_menu = ttk.Combobox(frame_add, textvariable=category_var, values=categories)
category_menu.grid(row=0, column=3, padx=5, pady=5)
category_menu.current(0)

ttk.Label(frame_add, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
date_entry = ttk.Entry(frame_add)
date_entry.grid(row=0, column=5, padx=5, pady=5)

ttk.Button(frame_add, text="Добавить расход", command=add_expense).grid(row=0, column=6, padx=5, pady=5)


# Фильтрация и сумма
frame_filter = ttk.Frame(root)
frame_filter.pack(pady=10, fill="x")

ttk.Label(frame_filter, text="Фильтр по категории:").grid(row=0, column=0)
filter_category = tk.StringVar()
filter_menu = ttk.Combobox(frame_filter, textvariable=filter_category,
                          values=["Все"] + categories)
filter_menu.grid(row=0, column=1)
filter_menu.current(0)

filter_category.trace("w", update_table)

ttk.Label(frame_filter, text="С:").grid(row=0, column=2)
start_date_entry = ttk.Entry(frame_filter)
start_date_entry.insert(0, "2024-01-01")
start_date_entry.grid(row=0, column=3)

ttk.Label(frame_filter, text="По:").grid(row=0, column=4)
end_date_entry = ttk.Entry(frame_filter)
end_date_entry.insert(0, "2026-12-31")
end_date_entry.grid(row=0, column=5)

ttk.Button(frame_filter, text="Обновить", command=update_table).grid(row=0, column=6)


# Таблица расходов
tree = ttk.Treeview(root, columns=("Сумма", "Категория", "Дата"), show="headings")
tree.heading("Сумма", text="Сумма")
tree.heading("Категория", text="Категория")
tree.heading("Дата", text="Дата")
tree.pack(fill="both", expand=True)



load_data()      
update_table()   

root.mainloop()
