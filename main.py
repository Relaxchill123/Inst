"""
Главный модуль приложения для управления заказами.
Точка входа в программу.
"""

import tkinter as tk
from gui import OrderManagementApp

def main():
    """
    Главная функция приложения.
    Инициализирует и запускает графический интерфейс.
    """
    try:
        root = tk.Tk()
        app = OrderManagementApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        raise

if __name__ == "__main__":
    main()