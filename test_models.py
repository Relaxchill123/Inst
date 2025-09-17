"""
Модуль unit-тестов для models.py.
"""

import unittest
from datetime import datetime
from models import Client, Product, Order, OrderItem, DataProcessor


class TestModels(unittest.TestCase):
    """Тесты для моделей данных."""

    def test_client_validation_valid(self):
        """Тест валидации корректного клиента."""
        client = Client(
            id=1,
            name="Иван Иванов",
            email="ivan@example.com",
            phone="+7 (123) 456-78-90",
            address="Москва"
        )
        self.assertTrue(client.validate())

    def test_client_validation_invalid_email(self):
        """Тест валидации клиента с некорректным email."""
        client = Client(
            id=1,
            name="Иван Иванов",
            email="invalid-email",
            phone="+71234567890",
            address="Москва"
        )
        self.assertFalse(client.validate())

    def test_client_validation_invalid_phone(self):
        """Тест валидации клиента с некорректным телефоном."""
        client = Client(
            id=1,
            name="Иван Иванов",
            email="ivan@example.com",
            phone="invalid-phone",
            address="Москва"
        )
        self.assertFalse(client.validate())

    def test_product_validation_valid(self):
        """Тест валидации корректного товара."""
        product = Product(
            id=1,
            name="Телефон",
            price=10000.0,
            category="Электроника"
        )
        self.assertTrue(product.validate())

    def test_product_validation_invalid_price(self):
        """Тест валидации товара с отрицательной ценой."""
        product = Product(
            id=1,
            name="Телефон",
            price=-100.0,
            category="Электроника"
        )
        self.assertFalse(product.validate())

    def test_order_validation_valid(self):
        """Тест валидации корректного заказа."""
        order = Order(
            id=1,
            client_id=1,
            status="новый"
        )
        order.add_item(1, 2, 1000.0)
        self.assertTrue(order.validate())

    def test_order_validation_no_items(self):
        """Тест валидации заказа без товаров."""
        order = Order(
            id=1,
            client_id=1,
            status="новый"
        )
        self.assertFalse(order.validate())

    def test_order_total_amount(self):
        """Тест расчета общей суммы заказа."""
        order = Order(
            id=1,
            client_id=1,
            status="новый"
        )
        order.add_item(1, 2, 1000.0)  # 2000
        order.add_item(2, 1, 500.0)  # 500
        self.assertEqual(order.total_amount, 2500.0)

    def test_data_processor_sort_orders(self):
        """Тест сортировки заказов."""
        orders = [
            Order(1, 1, datetime(2023, 1, 1), "новый"),
            Order(2, 1, datetime(2023, 1, 3), "выполнен"),
            Order(3, 1, datetime(2023, 1, 2), "в обработке")
        ]

        # Добавляем товары для валидации
        for order in orders:
            order.add_item(1, 1, 100.0)

        processor = DataProcessor()
        sorted_orders = processor.sort_orders(orders, 'date')

        self.assertEqual([o.id for o in sorted_orders], [1, 3, 2])

    def test_recursive_factorial(self):
        """Тест рекурсивного вычисления факториала."""
        processor = DataProcessor()
        self.assertEqual(processor.recursive_factorial(5), 120)
        self.assertEqual(processor.recursive_factorial(0), 1)


if __name__ == '__main__':
    unittest.main()