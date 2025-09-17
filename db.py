"""
Модуль для работы с базой данных SQLite.
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import Client, Product, Order, OrderItem


class Database:
    """Класс для работы с базой данных."""

    def __init__(self, db_name: str = "database.db"):
        """
        Инициализирует соединение с базой данных.

        Parameters
        ----------
        db_name : str, optional
            Имя файла базы данных
        """
        self.db_name = db_name
        self.init_db()

    def init_db(self) -> None:
        """Инициализирует таблицы базы данных."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Таблица клиентов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT NOT NULL,
                    address TEXT NOT NULL,
                    registration_date TEXT NOT NULL
                )
            ''')

            # Таблица товаров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT
                )
            ''')

            # Таблица заказов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    order_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            ''')

            # Таблица элементов заказа
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')

            conn.commit()

    def add_client(self, client: Client) -> int:
        """
        Добавляет клиента в базу данных.

        Parameters
        ----------
        client : Client
            Объект клиента

        Returns
        -------
        int
            ID добавленного клиента
        """
        if not client.validate():
            raise ValueError("Невалидные данные клиента")

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clients (name, email, phone, address, registration_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (client.name, client.email, client.phone, client.address,
                  client.registration_date.isoformat()))
            conn.commit()
            return cursor.lastrowid

    def add_product(self, product: Product) -> int:
        """
        Добавляет товар в базу данных.

        Parameters
        ----------
        product : Product
            Объект товара

        Returns
        -------
        int
            ID добавленного товара
        """
        if not product.validate():
            raise ValueError("Невалидные данные товара")

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, price, category, description)
                VALUES (?, ?, ?, ?)
            ''', (product.name, product.price, product.category,
                  product.description))
            conn.commit()
            return cursor.lastrowid

    def add_order(self, order: Order) -> int:
        """
        Добавляет заказ в базу данных.

        Parameters
        ----------
        order : Order
            Объект заказа

        Returns
        -------
        int
            ID добавленного заказа
        """
        if not order.validate():
            raise ValueError("Невалидные данные заказа")

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (client_id, order_date, status)
                VALUES (?, ?, ?)
            ''', (order.client_id, order.order_date.isoformat(), order.status))
            order_id = cursor.lastrowid

            for item in order.items:
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                ''', (order_id, item.product_id, item.quantity, item.price))

            conn.commit()
            return order_id

    def get_clients(self) -> List[Client]:
        """Возвращает список всех клиентов."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients')
            rows = cursor.fetchall()

            clients = []
            for row in rows:
                clients.append(Client(
                    id=row[0],
                    name=row[1],
                    email=row[2],
                    phone=row[3],
                    address=row[4],
                    registration_date=datetime.fromisoformat(row[5])
                ))
            return clients

    def get_products(self) -> List[Product]:
        """Возвращает список всех товаров."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products')
            rows = cursor.fetchall()

            products = []
            for row in rows:
                products.append(Product(
                    id=row[0],
                    name=row[1],
                    price=row[2],
                    category=row[3],
                    description=row[4] or ""
                ))
            return products

    def get_orders(self) -> List[Order]:
        """Возвращает список всех заказов."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM orders')
            orders = []

            for row in cursor.fetchall():
                order = Order(
                    id=row[0],
                    client_id=row[1],
                    order_date=datetime.fromisoformat(row[2]),
                    status=row[3]
                )

                # Получаем элементы заказа
                cursor.execute('''
                    SELECT product_id, quantity, price 
                    FROM order_items 
                    WHERE order_id = ?
                ''', (order.id,))

                for item_row in cursor.fetchall():
                    order.add_item(item_row[0], item_row[1], item_row[2])

                orders.append(order)

            return orders

    def export_to_json(self, filename: str) -> None:
        """
        Экспортирует все данные в JSON файл.

        Parameters
        ----------
        filename : str
            Имя файла для экспорта
        """
        data = {
            'clients': [client.to_dict() for client in self.get_clients()],
            'products': [product.to_dict() for product in self.get_products()],
            'orders': [order.to_dict() for order in self.get_orders()]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_from_json(self, filename: str) -> None:
        """
        Импортирует данные из JSON файла.

        Parameters
        ----------
        filename : str
            Имя файла для импорта
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Очищаем таблицы
            cursor.execute('DELETE FROM order_items')
            cursor.execute('DELETE FROM orders')
            cursor.execute('DELETE FROM products')
            cursor.execute('DELETE FROM clients')

            # Импортируем клиентов
            for client_data in data.get('clients', []):
                cursor.execute('''
                    INSERT INTO clients (name, email, phone, address, registration_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    client_data['name'],
                    client_data['email'],
                    client_data['phone'],
                    client_data['address'],
                    client_data['registration_date']
                ))

            # Импортируем товары
            for product_data in data.get('products', []):
                cursor.execute('''
                    INSERT INTO products (name, price, category, description)
                    VALUES (?, ?, ?, ?)
                ''', (
                    product_data['name'],
                    product_data['price'],
                    product_data['category'],
                    product_data.get('description', '')
                ))

            # Импортируем заказы
            for order_data in data.get('orders', []):
                cursor.execute('''
                    INSERT INTO orders (client_id, order_date, status)
                    VALUES (?, ?, ?)
                ''', (
                    order_data['client_id'],
                    order_data['order_date'],
                    order_data['status']
                ))
                order_id = cursor.lastrowid

                # Импортируем элементы заказа
                for item_data in order_data.get('items', []):
                    cursor.execute('''
                        INSERT INTO order_items (order_id, product_id, quantity, price)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        order_id,
                        item_data['product_id'],
                        item_data['quantity'],
                        item_data['price']
                    ))

            conn.commit()

    def export_to_csv(self, entity_type: str, filename: str) -> None:
        """
        Экспортирует данные в CSV файл.

        Parameters
        ----------
        entity_type : str
            Тип сущности ('clients', 'products', 'orders')
        filename : str
            Имя файла для экспорта
        """
        import csv

        if entity_type == 'clients':
            data = self.get_clients()
            fieldnames = ['id', 'name', 'email', 'phone', 'address',
                          'registration_date']
        elif entity_type == 'products':
            data = self.get_products()
            fieldnames = ['id', 'name', 'price', 'category', 'description']
        elif entity_type == 'orders':
            data = self.get_orders()
            fieldnames = ['id', 'client_id', 'order_date', 'status',
                          'total_amount']
        else:
            raise ValueError("Неизвестный тип сущности")

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for item in data:
                row_data = item.to_dict()
                if entity_type == 'orders':
                    row_data['total_amount'] = item.total_amount
                writer.writerow(row_data)