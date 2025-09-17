"""
Модуль графического интерфейса на tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import Client, Product, Order, OrderItem, DataProcessor
from db import Database
from analysis import DataAnalyzer

class OrderManagementApp:
    """Главное приложение для управления заказами."""

    def __init__(self, root):
        """
        Инициализирует главное окно приложения.

        Parameters
        ----------
        root : tk.Tk
            Корневое окно tkinter
        """
        self.root = root
        self.root.title("Система управления заказами")
        self.root.geometry("1200x800")

        self.db = Database()
        self.analyzer = DataAnalyzer(self.db)
        self.processor = DataProcessor()

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Настраивает пользовательский интерфейс."""
        # Создаем Notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка клиентов
        self.clients_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.clients_frame, text="Клиенты")
        self.setup_clients_tab()

        # Вкладка товаров
        self.products_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.products_frame, text="Товары")
        self.setup_products_tab()

        # Вкладка заказов
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="Заказы")
        self.setup_orders_tab()

        # Вкладка анализа
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="Аналитика")
        self.setup_analysis_tab()

        # Меню
        self.setup_menu()

    def setup_menu(self) -> None:
        """Настраивает главное меню."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню файла
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Экспорт в JSON", command=self.export_to_json)
        file_menu.add_command(label="Импорт из JSON", command=self.import_from_json)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Меню экспорта
        export_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Экспорт", menu=export_menu)
        export_menu.add_command(label="Клиенты в CSV",
                               command=lambda: self.export_to_csv('clients'))
        export_menu.add_command(label="Товары в CSV",
                               command=lambda: self.export_to_csv('products'))
        export_menu.add_command(label="Заказы в CSV",
                               command=lambda: self.export_to_csv('orders'))

    def setup_clients_tab(self) -> None:
        """Настраивает вкладку клиентов."""
        # Форма добавления клиента
        form_frame = ttk.LabelFrame(self.clients_frame, text="Добавить клиента")
        form_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(form_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.client_name = ttk.Entry(form_frame)
        self.client_name.grid(row=0, column=1, padx=5, pady=5, sticky='we')

        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.client_email = ttk.Entry(form_frame)
        self.client_email.grid(row=1, column=1, padx=5, pady=5, sticky='we')

        ttk.Label(form_frame, text="Телефон:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.client_phone = ttk.Entry(form_frame)
        self.client_phone.grid(row=2, column=1, padx=5, pady=5, sticky='we')

        ttk.Label(form_frame, text="Адрес:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.client_address = ttk.Entry(form_frame)
        self.client_address.grid(row=3, column=1, padx=5, pady=5, sticky='we')

        ttk.Button(form_frame, text="Добавить", command=self.add_client).grid(
            row=4, column=0, columnspan=2, pady=10)

        # Таблица клиентов
        table_frame = ttk.Frame(self.clients_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('id', 'name', 'email', 'phone', 'address', 'reg_date')
        self.clients_tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        for col in columns:
            self.clients_tree.heading(col, text=col.capitalize().replace('_', ' '))
            self.clients_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)

        self.clients_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def setup_products_tab(self) -> None:
        """Настраивает вкладку товаров."""
        # Форма добавления товара
        form_frame = ttk.LabelFrame(self.products_frame, text="Добавить товар")
        form_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.product_name = ttk.Entry(form_frame)
        self.product_name.grid(row=0, column=1, padx=5, pady=5, sticky='we')

        ttk.Label(form_frame, text="Цена:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.product_price = ttk.Entry(form_frame)
        self.product_price.grid(row=1, column=1, padx=5, pady=5, sticky='we')

        ttk.Label(form_frame, text="Категория:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.product_category = ttk.Entry(form_frame)
        self.product_category.grid(row=2, column=1, padx=5, pady=5, sticky='we')

        ttk.Label(form_frame, text="Описание:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.product_description = ttk.Entry(form_frame)
        self.product_description.grid(row=3, column=1, padx=5, pady=5, sticky='we')

        ttk.Button(form_frame, text="Добавить", command=self.add_product).grid(
            row=4, column=0, columnspan=2, pady=10)

        # Таблица товаров
        table_frame = ttk.Frame(self.products_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('id', 'name', 'price', 'category', 'description')
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        for col in columns:
            self.products_tree.heading(col, text=col.capitalize().replace('_', ' '))
            self.products_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)

        self.products_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def setup_orders_tab(self) -> None:
        """Настраивает вкладку заказов."""
        # Форма добавления заказа
        form_frame = ttk.LabelFrame(self.orders_frame, text="Создать заказ")
        form_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(form_frame, text="Клиент:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.order_client = ttk.Combobox(form_frame)
        self.order_client.grid(row=0, column=1, padx=5, pady=5, sticky='we')

        ttk.Label(form_frame, text="Товар:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.order_product = ttk.Combobox(form_frame)
        self.order_product.grid(row=1, column=1, padx=5, pady=5, sticky='we')

        ttk.Label(form_frame, text="Количество:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.order_quantity = ttk.Entry(form_frame)
        self.order_quantity.grid(row=2, column=1, padx=5, pady=5, sticky='we')

        ttk.Label(form_frame, text="Статус:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.order_status = ttk.Combobox(form_frame, values=['новый', 'в обработке', 'выполнен', 'отменен'])
        self.order_status.grid(row=3, column=1, padx=5, pady=5, sticky='we')
        self.order_status.set('новый')

        ttk.Button(form_frame, text="Добавить товар", command=self.add_order_item).grid(
            row=4, column=0, padx=5, pady=5)
        ttk.Button(form_frame, text="Создать заказ", command=self.create_order).grid(
            row=4, column=1, padx=5, pady=5)

        # Список товаров в заказе
        items_frame = ttk.LabelFrame(self.orders_frame, text="Товары в заказе")
        items_frame.pack(fill='x', padx=10, pady=5)

        columns = ('product', 'quantity', 'price', 'total')
        self.order_items_tree = ttk.Treeview(items_frame, columns=columns, show='headings')

        for col in columns:
            self.order_items_tree.heading(col, text=col.capitalize())
            self.order_items_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(items_frame, orient='vertical', command=self.order_items_tree.yview)
        self.order_items_tree.configure(yscrollcommand=scrollbar.set)

        self.order_items_tree.pack(side='left', fill='x', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Таблица заказов
        table_frame = ttk.Frame(self.orders_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('id', 'client', 'date', 'status', 'amount')
        self.orders_tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        for col in columns:
            self.orders_tree.heading(col, text=col.capitalize())
            self.orders_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)

        self.orders_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Фильтры заказов
        filter_frame = ttk.Frame(self.orders_frame)
        filter_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(filter_frame, text="Сортировка:").pack(side='left', padx=5)
        self.sort_var = tk.StringVar(value='date')
        ttk.Combobox(filter_frame, textvariable=self.sort_var,
                    values=['date', 'amount', 'status']).pack(side='left', padx=5)

        ttk.Label(filter_frame, text="Статус:").pack(side='left', padx=5)
        self.filter_status = ttk.Combobox(filter_frame, values=['все', 'новый', 'в обработке', 'выполнен', 'отменен'])
        self.filter_status.pack(side='left', padx=5)
        self.filter_status.set('все')

        ttk.Button(filter_frame, text="Применить", command=self.apply_filters).pack(side='left', padx=5)

    def setup_analysis_tab(self) -> None:
        """Настраивает вкладку анализа."""
        # Статистика
        stats_frame = ttk.LabelFrame(self.analysis_frame, text="Общая статистика")
        stats_frame.pack(fill='x', padx=10, pady=5)

        stats = self.analyzer.get_sales_statistics()
        ttk.Label(stats_frame, text=f"Всего заказов: {stats['total_orders']}").pack(anchor='w', padx=5, pady=2)
        ttk.Label(stats_frame, text=f"Общая выручка: {stats['total_revenue']:.2f} руб.").pack(anchor='w', padx=5, pady=2)
        ttk.Label(stats_frame, text=f"Средний чек: {stats['avg_order_value']:.2f} руб.").pack(anchor='w', padx=5, pady=2)
        ttk.Label(stats_frame, text=f"Всего клиентов: {stats['total_clients']}").pack(anchor='w', padx=5, pady=2)
        ttk.Label(stats_frame, text=f"Всего товаров: {stats['total_products']}").pack(anchor='w', padx=5, pady=2)

        # Кнопки анализа
        buttons_frame = ttk.Frame(self.analysis_frame)
        buttons_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(buttons_frame, text="Топ клиенты",
                  command=lambda: self.show_top_clients()).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Динамика продаж",
                  command=lambda: self.analyzer.plot_orders_dynamics()).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Топ товары",
                  command=lambda: self.analyzer.plot_top_products()).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Граф клиентов",
                  command=lambda: self.analyzer.plot_clients_network()).pack(side='left', padx=5)

    def load_data(self) -> None:
        """Загружает данные в интерфейс."""
        self.load_clients()
        self.load_products()
        self.load_orders()

        # Заполняем комбобоксы
        clients = self.db.get_clients()
        products = self.db.get_products()

        self.order_client['values'] = [f"{c.id}: {c.name}" for c in clients]
        self.order_product['values'] = [f"{p.id}: {p.name}" for p in products]

    def load_clients(self) -> None:
        """Загружает клиентов в таблицу."""
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)

        clients = self.db.get_clients()
        for client in clients:
            self.clients_tree.insert('', 'end', values=(
                client.id, client.name, client.email,
                client.phone, client.address,
                client.registration_date.strftime('%Y-%m-%d')
            ))

    def load_products(self) -> None:
        """Загружает товары в таблицу."""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        products = self.db.get_products()
        for product in products:
            self.products_tree.insert('', 'end', values=(
                product.id, product.name, product.price,
                product.category, product.description
            ))

    def load_orders(self) -> None:
        """Загружает заказы в таблицу."""
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        orders = self.db.get_orders()
        clients = self.db.get_clients()

        for order in orders:
            client = next((c for c in clients if c.id == order.client_id), None)
            client_name = client.name if client else "Неизвестный"

            self.orders_tree.insert('', 'end', values=(
                order.id, client_name,
                order.order_date.strftime('%Y-%m-%d'),
                order.status, f"{order.total_amount:.2f}"
            ))

    def add_client(self) -> None:
        """Добавляет нового клиента."""
        try:
            client = Client(
                id=0,  # Будет автоматически сгенерирован
                name=self.client_name.get(),
                email=self.client_email.get(),
                phone=self.client_phone.get(),
                address=self.client_address.get()
            )

            if not client.validate():
                messagebox.showerror("Ошибка", "Невалидные данные клиента")
                return

            self.db.add_client(client)
            self.load_clients()

            # Очищаем форму
            self.client_name.delete(0, tk.END)
            self.client_email.delete(0, tk.END)
            self.client_phone.delete(0, tk.END)
            self.client_address.delete(0, tk.END)

            messagebox.showinfo("Успех", "Клиент добавлен")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении клиента: {str(e)}")

    def add_product(self) -> None:
        """Добавляет новый товар."""
        try:
            price = float(self.product_price.get())
            product = Product(
                id=0,
                name=self.product_name.get(),
                price=price,
                category=self.product_category.get(),
                description=self.product_description.get()
            )

            if not product.validate():
                messagebox.showerror("Ошибка", "Невалидные данные товара")
                return

            self.db.add_product(product)
            self.load_products()

            # Очищаем форму
            self.product_name.delete(0, tk.END)
            self.product_price.delete(0, tk.END)
            self.product_category.delete(0, tk.END)
            self.product_description.delete(0, tk.END)

            messagebox.showinfo("Успех", "Товар добавлен")

        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении товара: {str(e)}")

    def add_order_item(self) -> None:
        """Добавляет товар в текущий заказ."""
        try:
            product_str = self.order_product.get()
            if not product_str:
                messagebox.showerror("Ошибка", "Выберите товар")
                return

            product_id = int(product_str.split(':')[0])
            quantity = int(self.order_quantity.get())

            products = self.db.get_products()
            product = next((p for p in products if p.id == product_id), None)

            if not product:
                messagebox.showerror("Ошибка", "Товар не найден")
                return

            self.order_items_tree.insert('', 'end', values=(
                product.name, quantity, product.price, quantity * product.price
            ))

            self.order_quantity.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть целым числом")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении товара: {str(e)}")

    def create_order(self) -> None:
        """Создает новый заказ."""
        try:
            client_str = self.order_client.get()
            if not client_str:
                messagebox.showerror("Ошибка", "Выберите клиента")
                return

            client_id = int(client_str.split(':')[0])
            status = self.order_status.get()

            order = Order(id=0, client_id=client_id, status=status)

            # Добавляем товары из дерева
            for item in self.order_items_tree.get_children():
                values = self.order_items_tree.item(item)['values']
                product_name = values[0]
                quantity = values[1]
                price = values[2]

                # Находим ID товара по имени
                products = self.db.get_products()
                product = next((p for p in products if p.name == product_name), None)

                if product:
                    order.add_item(product.id, quantity, price)

            if not order.items:
                messagebox.showerror("Ошибка", "Добавьте хотя бы один товар")
                return

            self.db.add_order(order)
            self.load_orders()

            # Очищаем форму
            self.order_items_tree.delete(*self.order_items_tree.get_children())

            messagebox.showinfo("Успех", "Заказ создан")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании заказа: {str(e)}")

    def apply_filters(self) -> None:
        """Применяет фильтры к заказам."""
        try:
            orders = self.db.get_orders()
            clients = self.db.get_clients()

            # Применяем фильтр по статусу
            status_filter = self.filter_status.get()
            if status_filter != 'все':
                orders = [o for o in orders if o.status == status_filter]

            # Сортируем
            sort_key = self.sort_var.get()
            orders = self.processor.sort_orders(orders, sort_key)

            # Обновляем таблицу
            for item in self.orders_tree.get_children():
                self.orders_tree.delete(item)

            for order in orders:
                client = next((c for c in clients if c.id == order.client_id), None)
                client_name = client.name if client else "Неизвестный"

                self.orders_tree.insert('', 'end', values=(
                    order.id, client_name,
                    order.order_date.strftime('%Y-%m-%d'),
                    order.status, f"{order.total_amount:.2f}"
                ))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при применении фильтров: {str(e)}")

    def show_top_clients(self) -> None:
        """Показывает топ клиентов."""
        top_clients = self.analyzer.get_top_clients_by_orders()

        top_window = tk.Toplevel(self.root)
        top_window.title("Топ клиенты")
        top_window.geometry("600x400")

        tree = ttk.Treeview(top_window, columns=('name', 'orders', 'total'), show='headings')
        tree.heading('name', text='Клиент')
        tree.heading('orders', text='Заказов')
        tree.heading('total', text='Общая сумма')

        for client in top_clients:
            tree.insert('', 'end', values=(
                client['client'].name,
                client['order_count'],
                f"{client['total_spent']:.2f} руб."
            ))

        tree.pack(fill='both', expand=True, padx=10, pady=10)

    def export_to_json(self) -> None:
        """Экспортирует данные в JSON файл."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )
            if filename:
                self.db.export_to_json(filename)
                messagebox.showinfo("Успех", "Данные экспортированы в JSON")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")

    def import_from_json(self) -> None:
        """Импортирует данные из JSON файла."""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")]
            )
            if filename:
                self.db.import_from_json(filename)
                self.load_data()
                messagebox.showinfo("Успех", "Данные импортированы из JSON")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при импорте: {str(e)}")

    def export_to_csv(self, entity_type: str) -> None:
        """Экспортирует данные в CSV файл."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )
            if filename:
                self.db.export_to_csv(entity_type, filename)
                messagebox.showinfo("Успех", f"{entity_type.capitalize()} экспортированы в CSV")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")