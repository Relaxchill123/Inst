"""
Модуль для анализа и визуализации данных.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any
from datetime import datetime
from models import Client, Order, Product
import networkx as nx


class DataAnalyzer:
    """Класс для анализа данных заказов."""

    def __init__(self, db):
        """
        Инициализирует анализатор данных.

        Parameters
        ----------
        db : Database
            Объект базы данных
        """
        self.db = db

    def get_top_clients_by_orders(self, limit: int = 5) -> List[
        Dict[str, Any]]:
        """
        Возвращает топ клиентов по количеству заказов.

        Parameters
        ----------
        limit : int, optional
            Количество клиентов для возврата

        Returns
        -------
        List[Dict[str, Any]]
            Список словарей с информацией о клиентах
        """
        orders = self.db.get_orders()
        clients = self.db.get_clients()

        client_orders = {}
        for order in orders:
            client_orders[order.client_id] = client_orders.get(order.client_id,
                                                               0) + 1

        top_clients = []
        for client_id, order_count in sorted(client_orders.items(),
                                             key=lambda x: x[1], reverse=True)[
                                      :limit]:
            client = next((c for c in clients if c.id == client_id), None)
            if client:
                top_clients.append({
                    'client': client,
                    'order_count': order_count,
                    'total_spent': sum(o.total_amount for o in orders
                                       if o.client_id == client_id)
                })

        return top_clients

    def plot_orders_dynamics(self, period: str = 'month') -> None:
        """
        Строит график динамики заказов.

        Parameters
        ----------
        period : str, optional
            Период группировки ('day', 'week', 'month')
        """
        orders = self.db.get_orders()

        df = pd.DataFrame([{
            'date': order.order_date.date(),
            'amount': order.total_amount
        } for order in orders])

        if df.empty:
            print("Нет данных для построения графика")
            return

        if period == 'day':
            grouped = df.groupby('date')['amount'].sum()
        elif period == 'week':
            df['week'] = df['date'].apply(lambda x: x.isocalendar()[1])
            grouped = df.groupby('week')['amount'].sum()
        elif period == 'month':
            df['month'] = df['date'].apply(lambda x: x.month)
            grouped = df.groupby('month')['amount'].sum()
        else:
            raise ValueError("Неизвестный период")

        plt.figure(figsize=(12, 6))
        grouped.plot(kind='line', marker='o')
        plt.title(f'Динамика продаж по {period}')
        plt.xlabel('Период')
        plt.ylabel('Сумма продаж')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_top_products(self, limit: int = 10) -> None:
        """
        Строит график топ товаров по продажам.

        Parameters
        ----------
        limit : int, optional
            Количество товаров для отображения
        """
        orders = self.db.get_orders()
        products = self.db.get_products()

        product_sales = {}
        for order in orders:
            for item in order.items:
                product_sales[item.product_id] = product_sales.get(
                    item.product_id, 0) + item.quantity

        top_products = sorted(product_sales.items(), key=lambda x: x[1],
                              reverse=True)[:limit]

        product_names = []
        sales_counts = []

        for product_id, count in top_products:
            product = next((p for p in products if p.id == product_id), None)
            if product:
                product_names.append(product.name)
                sales_counts.append(count)

        plt.figure(figsize=(12, 6))
        plt.barh(product_names, sales_counts)
        plt.title(f'Топ {limit} товаров по количеству продаж')
        plt.xlabel('Количество продаж')
        plt.tight_layout()
        plt.show()

    def create_clients_network(self) -> nx.Graph:
        """
        Создает граф связей между клиентами.

        Returns
        -------
        nx.Graph
            Граф связей клиентов
        """
        orders = self.db.get_orders()
        clients = self.db.get_clients()
        products = self.db.get_products()

        G = nx.Graph()

        # Добавляем клиентов как узлы
        for client in clients:
            G.add_node(client.id, label=client.name, type='client')

        # Создаем связи на основе общих товаров
        client_products = {}
        for order in orders:
            for item in order.items:
                if order.client_id not in client_products:
                    client_products[order.client_id] = set()
                client_products[order.client_id].add(item.product_id)

        # Добавляем ребра между клиентами, которые покупали одинаковые товары
        client_ids = list(client_products.keys())
        for i in range(len(client_ids)):
            for j in range(i + 1, len(client_ids)):
                common_products = client_products[client_ids[i]] & \
                                  client_products[client_ids[j]]
                if common_products:
                    weight = len(common_products)
                    G.add_edge(client_ids[i], client_ids[j], weight=weight)

        return G

    def plot_clients_network(self) -> None:
        """Визуализирует граф связей клиентов."""
        G = self.create_clients_network()

        plt.figure(figsize=(14, 10))
        pos = nx.spring_layout(G, k=1, iterations=50)

        # Рисуем узлы
        nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue')

        # Рисуем ребра
        edges = G.edges(data=True)
        weights = [edge[2]['weight'] for edge in edges]
        nx.draw_networkx_edges(G, pos, width=[w * 0.5 for w in weights],
                               alpha=0.6)

        # Добавляем подписи
        labels = {node: G.nodes[node]['label'] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)

        plt.title('Граф связей клиентов по общим товарам')
        plt.axis('off')
        plt.tight_layout()
        plt.show()

    def get_sales_statistics(self) -> Dict[str, Any]:
        """
        Возвращает общую статистику продаж.

        Returns
        -------
        Dict[str, Any]
            Словарь со статистикой
        """
        orders = self.db.get_orders()
        clients = self.db.get_clients()
        products = self.db.get_products()

        total_orders = len(orders)
        total_revenue = sum(order.total_amount for order in orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        total_clients = len(clients)
        total_products = len(products)

        return {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'avg_order_value': avg_order_value,
            'total_clients': total_clients,
            'total_products': total_products
        }