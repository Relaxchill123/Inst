"""
Модуль unit-тестов для analysis.py.
"""

import unittest
from datetime import datetime
from models import Client, Product, Order, OrderItem
from db import Database
from analysis import DataAnalyzer


class TestAnalysis(unittest.TestCase):
    """Тесты для анализа данных."""

    def setUp(self):
        """Настройка тестовых данных."""
        # Создаем временную базу данных в памяти
        self.db = Database(':memory:')
        self.analyzer = DataAnalyzer(self.db)

        # Добавляем тестовых клиентов
        clients = [
            Client(1, "Иван Иванов", "ivan@example.com", "+79123456789",
                   "Москва"),
            Client(2, "Петр Петров", "petr@example.com", "+79234567890",
                   "СПб"),
            Client(3, "Сидор Сидоров", "sidor@example.com", "+79345678901",
                   "Казань")
        ]

        for client in clients:
            self.db.add_client(client)

        # Добавляем тестовые товары
        products = [
            Product(1, "Телефон", 10000.0, "Электроника"),
            Product(2, "Ноутбук", 50000.0, "Электроника"),
            Product(3, "Книга", 500.0, "Книги")
        ]

        for product in products:
            self.db.add_product(product)

        # Добавляем тестовые заказы
        orders = [
            Order(1, 1, datetime(2023, 1, 1), "выполнен"),
            Order(2, 1, datetime(2023, 1, 2), "выполнен"),
            Order(3, 2, datetime(2023, 1, 3), "новый"),
            Order(4, 3, datetime(2023, 1, 4), "в обработке")
        ]

        # Добавляем товары в заказы
        orders[0].add_item(1, 2, 10000.0)  # 20000
        orders[0].add_item(3, 1, 500.0)  # 500

        orders[1].add_item(2, 1, 50000.0)  # 50000

        orders[2].add_item(1, 1, 10000.0)  # 10000
        orders[2].add_item(3, 2, 500.0)  # 1000

        orders[3].add_item(2, 1, 50000.0)  # 50000

        for order in orders:
            self.db.add_order(order)

    def test_top_clients_by_orders(self):
        """Тест получения топ клиентов по заказам."""
        top_clients = self.analyzer.get_top_clients_by_orders(2)

        self.assertEqual(len(top_clients), 2)
        self.assertEqual(top_clients[0]['client'].name, "Иван Иванов")
        self.assertEqual(top_clients[0]['order_count'], 2)
        self.assertEqual(top_clients[1]['client'].name, "Петр Петров")

    def test_sales_statistics(self):
        """Тест получения статистики продаж."""
        stats = self.analyzer.get_sales_statistics()

        self.assertEqual(stats['total_orders'], 4)
        self.assertEqual(stats['total_clients'], 3)
        self.assertEqual(stats['total_products'], 3)
        self.assertAlmostEqual(stats['total_revenue'],
                               20000 + 500 + 50000 + 10000 + 1000 + 50000)

    def test_clients_network(self):
        """Тест создания графа клиентов."""
        G = self.analyzer.create_clients_network()

        # Должны быть 3 узла (клиента)
        self.assertEqual(len(G.nodes()), 3)

        # Должны быть связи между клиентами
        self.assertTrue(len(G.edges()) > 0)


if __name__ == '__main__':
    unittest.main()