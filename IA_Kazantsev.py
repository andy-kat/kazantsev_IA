import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

API_URL = "https://open.er-api.com/v6/latest/RUB"
HISTORY_FILE = "conversion_history.json"

# --- Загрузка курсов валют ---
def load_currencies():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        if data.get("result") != "success":
            raise Exception("API returned error")
        rates = data.get("rates", {})
        codes = sorted([code for code in rates.keys() if code != "RUB"])
        codes.insert(0, "RUB")
        return codes, rates
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить курсы валют: {e}")
        return [], {}

# --- Работа с историей ---
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

def add_to_history(record):
    history = load_history()
    history.append(record)
    if len(history) > 50:  # Ограничиваем размер истории
        history = history[-50:]
    save_history(history)

# --- Основная логика конвертации ---
def convert():
    amount_str = amount_var.get().strip()
    from_curr = from_currency_var.get()
    to_curr = to_currency_var.get()

    # Валидация
    if not amount_str:
        result_var.set("Введите сумму")
        return
    try:
        amount = float(amount_str)
        if amount <= 0:
            result_var.set("Сумма должна быть положительной")
            return
    except ValueError:
        result_var.set("Введите корректное число")
        return

    if from_curr == to_curr:
        result_var.set(f"{amount:,.2f} {from_curr}")
        add_to_history({
            "from": from_curr, "to": to_curr, "amount": amount,
            "result": amount, "rate": 1.0
        })
        return

    # Получаем курс
    try:
        if from_curr == "RUB":
            rate = rates[to_curr]
            converted = amount * rate
            rate_for_history = rate
        elif to_curr == "RUB":
            rate = rates[from_curr]
            converted = amount / rate
            rate_for_history = 1 / rate
        else:
            # Конвертация через RUB (кросс-курс)
            rate_from = rates[from_curr]  # 1 from_curr в RUB
            rate_to = rates[to_curr]      # 1 RUB в to_curr
            converted = (amount / rate_from) * rate_to
            rate_for_history = rate_to / rate_from

        result_var.set(f"{converted:,.2f} {to_curr}")
        
        # Сохраняем в историю
        add_to_history({
            "from": from_curr, "to": to_curr, "amount": amount,
            "result": converted, "rate": rate_for_history
        })
    except KeyError:
        result_var.set("Ошибка: курс недоступен")
    except ZeroDivisionError:
        result_var.set("Ошибка: деление на ноль")

# --- GUI ---
root = tk.Tk()
root.title("Конвертер валют")
root.geometry("700x450")
root.resizable(False, False)

currencies, rates = load_currencies()
if not currencies:
    root.destroy()
else:
    # Переменные
    amount_var = tk.StringVar()
    from_currency_var = tk.StringVar(value="RUB")
    to_currency_var = tk.StringVar(value="RUB")
    result_var = tk.StringVar()

    # Виджеты ввода
    tk.Label(root, text="Сумма:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    tk.Entry(root, textvariable=amount_var).grid(row=0, column=1, padx=10, pady=10, sticky="we", columnspan=2)

    tk.Label(root, text="Из:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    ttk.Combobox(root, textvariable=from_currency_var,
                 values=currencies, state="readonly", width=6).grid(row=1, column=1, padx=10, pady=5, sticky="w")

    tk.Label(root, text="В:").grid(row=1, column=2, padx=10, pady=5, sticky="e")
    ttk.Combobox(root, textvariable=to_currency_var,
                 values=currencies, state="readonly", width=6).grid(row=1, column=3, padx=10, pady=5, sticky="w")

    tk.Button(root, text="Перевести", command=convert).grid(row=2, column=0, columnspan=4, pady=15)
    
    tk.Label(root, textvariable=result_var,
             font=("Arial", 14), fg="#006600").grid(row=3, column=0, columnspan=4, pady=5)

    # Таблица истории (Treeview)
    history_tree = ttk.Treeview(root, columns=("from", "to", "amount", "rate", "result"), show='headings')
    
    history_tree.heading("from", text="Из")
    history_tree.heading("to", text="В")
    history_tree.heading("amount", text="Сумма")
    history_tree.heading("rate", text="Курс")
    history_tree.heading("result", text="Результат")
    
    history_tree.column("from", width=80)
    history_tree.column("to", width=80)
    history_tree.column("amount", width=120)
    history_tree.column("rate", width=120)
    history_tree.column("result", width=120)
    
    history_tree.grid(row=4, column=0, columnspan=4, pady=(20, 5), sticky="nsew")
    
    # Загрузка истории в таблицу при старте
    for item in load_history():
        history_tree.insert("", tk.END,
                            values=(item["from"], item["to"], f"{item['amount']:,.2f}",
                                    f"{item['rate']:.4f}", f"{item['result']:,.2f}"))
    
    # Атрибуция (по требованию API)
    attribution_label = tk.Label(
       root,
       text="Курсы предоставлены ExchangeRate-API",
       font=("Arial", 8),
       fg="#555",
       cursor="hand2"
   )
    attribution_label.grid(row=5, column=0, columnspan=4, pady=(0, 10))
    attribution_label.bind("<Button-1>", lambda e: root.clipboard_clear() or root.clipboard_append("https://www.exchangerate-api.com"))

# Запуск приложения
if currencies:
    root.mainloop()
