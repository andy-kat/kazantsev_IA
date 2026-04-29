import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = "https://open.er-api.com/v6/latest/RUB"

root = tk.Tk()
root.title("Перевод валют")
root.geometry("400x220")
root.resizable(False, False)

amount_var = tk.StringVar()
currency_var = tk.StringVar()
result_var = tk.StringVar()
currencies = []

def load_currencies():
   try:
       response = requests.get(API_URL)
       response.raise_for_status()
       data = response.json()
       if data.get("result") != "success":
           raise Exception("API returned error")
       rates = data.get("rates", {})
       codes = sorted([code for code in rates.keys() if code != "RUB"])
       codes.insert(0, "RUB")  # рубли по умолчанию первым
       return codes, rates
   except Exception as e:
       messagebox.showerror("Ошибка", f"Не удалось загрузить курсы валют: {e}")
       root.destroy()
       return [], {}

def convert():
   try:
       amount = float(amount_var.get())
   except ValueError:
       result_var.set("Введите число")
       return
   target = currency_var.get()
   if target not in rates:
       result_var.set("Выберите валюту")
       return
   rate = rates[target]
   print(amount,rate)
   converted = amount * rate
   result_var.set(f"{converted:,.2f} {target}")

currencies, rates = load_currencies()
if not currencies:
   exit()

currency_menu = ttk.Combobox(root, textvariable=currency_var, values=currencies, state="readonly", width=6)
currency_menu.current(0)

# Виджеты
tk.Label(root, text="Сумма в RUB:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
tk.Entry(root, textvariable=amount_var).grid(row=0, column=1, padx=10, pady=10, sticky="we", columnspan=2)

tk.Label(root, text="Выберите валюту из списка:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
currency_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")

tk.Button(root, text="Перевести", command=convert).grid(row=2, column=0, columnspan=3, pady=15)

tk.Label(root, textvariable=result_var, font=("Arial", 14), fg="#006600").grid(row=3, column=0, columnspan=3, pady=5)

# Атрибуция (по требованию API)
attribution_label = tk.Label(
   root,
   text="Курсы предоставлены ExchangeRate-API",
   font=("Arial", 8),
   fg="#555",
   cursor="hand2"
)
attribution_label.grid(row=4, column=0, columnspan=3, pady=(0, 10))
attribution_label.bind("<Button-1>", lambda e: root.clipboard_clear() or root.clipboard_append("https://www.exchangerate-api.com"))

root.grid_columnconfigure(1, weight=1)
root.mainloop()
