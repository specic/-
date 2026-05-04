import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # API конфигурация
        self.api_key = "YOUR_API_KEY"  # Замените на ваш ключ
        self.base_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/"

        # Доступные валюты
        self.currencies = ["USD", "EUR", "UAH", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "PLN"]

        # История конвертаций
        self.history_file = "history.json"
        self.history = self.load_history()

        # Интерфейс
        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        # Фрейм для ввода
        input_frame = ttk.LabelFrame(self.root, text="Конвертация", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = ttk.Entry(input_frame, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Из валюты
        ttk.Label(input_frame, text="Из валюты:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.from_currency = ttk.Combobox(input_frame, values=self.currencies, width=17)
        self.from_currency.grid(row=1, column=1, padx=5, pady=5)
        self.from_currency.set("USD")

        # В валюту
        ttk.Label(input_frame, text="В валюту:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.to_currency = ttk.Combobox(input_frame, values=self.currencies, width=17)
        self.to_currency.grid(row=2, column=1, padx=5, pady=5)
        self.to_currency.set("UAH")

        # Кнопка конвертации
        self.convert_btn = ttk.Button(input_frame, text="Конвертировать", command=self.convert)
        self.convert_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # Результат
        self.result_label = ttk.Label(input_frame, text="", font=("Arial", 12))
        self.result_label.grid(row=4, column=0, columnspan=2)

        # История
        history_frame = ttk.LabelFrame(self.root, text="История конвертаций", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Таблица истории
        columns = ("Дата", "Сумма", "Из", "В", "Результат", "Курс")
        self.history_table = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.history_table.heading(col, text=col)
            self.history_table.column(col, width=100)

        # Скроллбар
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_table.yview)
        self.history_table.configure(yscrollcommand=scrollbar.set)

        self.history_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления историей
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Обновить курсы", command=self.update_rates).pack(side="left", padx=5)

    def get_exchange_rate(self, from_currency, to_currency):
        """Получение курса валюты через API"""
        try:
            url = self.base_url + from_currency
            response = requests.get(url, timeout=10)
            data = response.json()

            if data["result"] == "success":
                rate = data["conversion_rates"].get(to_currency)
                if rate:
                    return rate
                else:
                    messagebox.showerror("Ошибка", f"Валюта {to_currency} не найдена")
                    return None
            else:
                messagebox.showerror("Ошибка API", data.get("error-type", "Неизвестная ошибка"))
                return None
        except Exception as e:
            messagebox.showerror("Ошибка соединения", f"Не удалось получить курсы: {str(e)}")
            return None

    def convert(self):
        """Конвертация валюты"""
        amount_str = self.amount_entry.get().strip()

        # Проверка ввода
        if not amount_str:
            messagebox.showwarning("Ошибка", "Введите сумму")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("Ошибка", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showwarning("Ошибка", "Сумма должна быть числом")
            return

        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()

        if not from_curr or not to_curr:
            messagebox.showwarning("Ошибка", "Выберите валюты")
            return

        # Получение курса
        rate = self.get_exchange_rate(from_curr, to_curr)
        if rate is None:
            return

        converted = amount * rate
        result_text = f"{amount:.2f} {from_curr} = {converted:.2f} {to_curr} (Курс: {rate:.4f})"
        self.result_label.config(text=result_text)

        # Сохранение в историю
        history_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "from": from_curr,
            "to": to_curr,
            "result": round(converted, 2),
            "rate": rate
        }
        self.history.append(history_entry)
        self.save_history()
        self.update_history_table()

    def update_history_table(self):
        """Обновление таблицы истории"""
        # Очистка таблицы
        for item in self.history_table.get_children():
            self.history_table.delete(item)

        # Заполнение данными
        for entry in self.history:
            self.history_table.insert("", "end", values=(
                entry["date"],
                f"{entry['amount']:.2f}",
                entry["from"],
                entry["to"],
                f"{entry['result']:.2f}",
                f"{entry['rate']:.4f}"
            ))

    def save_history(self):
        """Сохранение истории в JSON"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {str(e)}")

    def load_history(self):
        """Загрузка истории из JSON"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_table()
            self.result_label.config(text="История очищена")

    def update_rates(self):
        """Тестовое обновление курсов (просто информационное сообщение)"""
        messagebox.showinfo("Информация", "Курсы обновляются при каждой конвертации через API")

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
