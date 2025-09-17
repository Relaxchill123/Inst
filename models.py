"""
Модуль содержит классы данных для системы учёта заказов.
"""

import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


class BaseModel(ABC):
    """Абстрактный базовый класс для всех моделей данных."""

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Проверяет валидность данных объекта."""
        pass


@dataclass
class Product(BaseModel):
    """
    Класс товара.

    Attributes
    ----------
    id : int
        Уникальный идентификатор товара
    name : str
        Название товара
    price : float
        Цена товара
    category : str
        Категория товара
    description : str, optional
        Описание товара
    """
    id: int
    name: str
    price: float
    category: str
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует товар в словарь."""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'description': self.description
        }

    def validate(self) -> bool:
        """Проверяет валидность данных товара."""
        if not self.name or self.price <= 0:
            return False
        return True


@dataclass
class Client(BaseModel):
    """
    Класс клиента.

    Attributes
    ----------
    id : int
        Уникальный идентификатор клиента
    name : str
        Имя клиента
    email : str
        Email клиента
    phone : str
        Телефон клиента
    address : str
        Адрес клиента
    registration_date : datetime
        Дата регистрации
    """
    id: int
    name: str
    email: str
    phone: str
    address: str
    registration_date: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует клиента в словарь."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'registration_date': self.registration_date.isoformat()
        }

    def validate(self) -> bool:
        """Проверяет валидность данных клиента."""
        # Проверка email с помощью регулярного выражения
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            return False

        # Проверка телефона (российский формат)
        phone_pattern = r'^(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$'
        if not re.match(phone_pattern, self.phone.replace(" ", "")):
            return False

        if not self.name or not self.address:
            return False

        return True


@dataclass
class OrderItem:
    """
    Элемент заказа.

    Attributes
    ----------
    product_id : int
        ID товара
    quantity : int
        Количество
    price : float
        Цена за единицу
    """
    product_id: int
    quantity: int
    price: float

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует элемент заказа в словарь."""
        return {
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price
        }

    @property
    def total_price(self) -> float:
        """Общая стоимость элемента заказа."""
        return self.quantity * self.price


@dataclass
class Order(BaseModel):
    """
    Класс заказа.

    Attributes
    ----------
    id : int
        Уникальный идентификатор заказа
    client_id : int
        ID клиента
    order_date : datetime
        Дата заказа
    status : str
        Статус заказа
    items : List[OrderItem]
        Список товаров в заказе
    """
    id: int
    client_id: int
    order_date: datetime = field(default_factory=datetime.now)
    status: str = "новый"
    items: List[OrderItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует заказ в словарь."""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'order_date': self.order_date.isoformat(),
            'status': self.status,
            'items': [item.to_dict() for item in self.items]
        }

    def validate(self) -> bool:
        """Проверяет валидность данных заказа."""
        if not self.client_id or not self.items:
            return False
        return True

    @property
    def total_amount(self) -> float:
        """Общая стоимость заказа."""
        return sum(item.total_price for item in self.items)

    def add_item(self, product_id: int, quantity: int, price: float) -> None:
        """Добавляет товар в заказ."""
        self.items.append(OrderItem(product_id, quantity, price))

    def remove_item(self, product_id: int) -> None:
        """Удаляет товар из заказа."""
        self.items = [item for item in self.items if
                      item.product_id != product_id]


class DataProcessor:
    """Класс для обработки и сортировки данных."""

    @staticmethod
    def sort_orders(orders: List[Order], key: str, reverse: bool = False) -> \
    List[Order]:
        """
        Сортирует список заказов по указанному ключу.

        Parameters
        ----------
        orders : List[Order]
            Список заказов для сортировки
        key : str
            Ключ сортировки ('date', 'amount', 'status')
        reverse : bool, optional
            Обратный порядок сортировки

        Returns
        -------
        List[Order]
            Отсортированный список заказов
        """
        key_functions = {
            'date': lambda o: o.order_date,
            'amount': lambda o: o.total_amount,
            'status': lambda o: o.status
        }

        if key not in key_functions:
            raise ValueError(f"Неизвестный ключ сортировки: {key}")

        return sorted(orders, key=key_functions[key], reverse=reverse)

    @staticmethod
    def filter_orders(orders: List[Order], **filters) -> List[Order]:
        """
        Фильтрует заказы по заданным критериям.

        Parameters
        ----------
        orders : List[Order]
            Список заказов для фильтрации
        **filters
            Критерии фильтрации (client_id, status, min_amount, etc.)

        Returns
        -------
        List[Order]
            Отфильтрованный список заказов
        """
        filtered = orders

        if 'client_id' in filters:
            filtered = [o for o in filtered if
                        o.client_id == filters['client_id']]

        if 'status' in filters:
            filtered = [o for o in filtered if
                        o.status.lower() == filters['status'].lower()]

        if 'min_amount' in filters:
            filtered = [o for o in filtered if
                        o.total_amount >= filters['min_amount']]

        if 'max_amount' in filters:
            filtered = [o for o in filtered if
                        o.total_amount <= filters['max_amount']]

        if 'start_date' in filters:
            filtered = [o for o in filtered if
                        o.order_date >= filters['start_date']]

        if 'end_date' in filters:
            filtered = [o for o in filtered if
                        o.order_date <= filters['end_date']]

        return filtered

    @staticmethod
    def recursive_factorial(n: int) -> int:
        """
        Вычисляет факториал числа рекурсивно.

        Parameters
        ----------
        n : int
            Число для вычисления факториала

        Returns
        -------
        int
            Факториал числа
        """
        if n <= 1:
            return 1
        return n * DataProcessor.recursive_factorial(n - 1)