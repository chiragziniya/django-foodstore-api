from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Store, MenuItem, Inventory

class MenuAPITestCase(APITestCase):
    def setUp(self):
        self.store = Store.objects.create(name="Test Store")
        self.menu_item_active = MenuItem.objects.create(
            store=self.store, name="Active Item", price=10.00, is_active=True
        )
        self.menu_item_inactive = MenuItem.objects.create(
            store=self.store, name="Inactive Item", price=10.00, is_active=False
        )
        self.inventory_zero = Inventory.objects.create(menu_item=self.menu_item_active, quantity=0)
        self.inventory_threshold = Inventory.objects.create(menu_item=self.menu_item_inactive, quantity=3)

    def test_item_with_zero_quantity(self):
        url = reverse('store-menu', kwargs={'store_id': self.store.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = response.data
        active_item = next(item for item in items if item['id'] == self.menu_item_active.id)
        self.assertFalse(active_item['is_available'])
        self.assertFalse(active_item['almost_gone'])

    def test_item_with_quantity_within_threshold(self):
        # Change to active
        self.menu_item_inactive.is_active = True
        self.menu_item_inactive.save()
        url = reverse('store-menu', kwargs={'store_id': self.store.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = response.data
        threshold_item = next(item for item in items if item['id'] == self.menu_item_inactive.id)
        self.assertTrue(threshold_item['is_available'])
        self.assertTrue(threshold_item['almost_gone'])

    def test_inactive_item(self):
        url = reverse('store-menu', kwargs={'store_id': self.store.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = response.data
        inactive_item = next(item for item in items if item['id'] == self.menu_item_inactive.id)
        self.assertFalse(inactive_item['is_available'])
        self.assertTrue(inactive_item['almost_gone'])  # quantity=3 is within threshold

    def test_query_optimization(self):
        # Ensure select_related is used, check queries
        from django.test.utils import override_settings
        from django.db import connection
        url = reverse('store-menu', kwargs={'store_id': self.store.id})
        with self.assertNumQueries(1):  # Should be 1 query with select_related
            response = self.client.get(url)

class InventoryAPITestCase(APITestCase):
    def setUp(self):
        self.store = Store.objects.create(name="Test Store")
        self.menu_item = MenuItem.objects.create(
            store=self.store, name="Test Item", price=10.00, is_active=True
        )

    def test_negative_quantity_fails(self):
        url = reverse('inventory-update', kwargs={'menu_item_id': self.menu_item.id})
        response = self.client.patch(url, {'quantity': -1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inventory_creation_if_missing(self):
        url = reverse('inventory-update', kwargs={'menu_item_id': self.menu_item.id})
        response = self.client.patch(url, {'quantity': 10}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        inventory = Inventory.objects.get(menu_item=self.menu_item)
        self.assertEqual(inventory.quantity, 10)
        self.assertTrue(response.data['is_available'])
        self.assertFalse(response.data['almost_gone'])

    def test_correct_flag_calculation(self):
        # Create inventory
        inventory = Inventory.objects.create(menu_item=self.menu_item, quantity=3)
        url = reverse('inventory-update', kwargs={'menu_item_id': self.menu_item.id})
        response = self.client.patch(url, {'quantity': 3}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_available'])
        self.assertTrue(response.data['almost_gone'])

class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.store = Store.objects.create(name="Test Store")
        self.menu_item1 = MenuItem.objects.create(
            store=self.store, name="Item 1", price=10.00, is_active=True
        )
        self.menu_item2 = MenuItem.objects.create(
            store=self.store, name="Item 2", price=10.00, is_active=True
        )
        self.inventory1 = Inventory.objects.create(menu_item=self.menu_item1, quantity=10)
        self.inventory2 = Inventory.objects.create(menu_item=self.menu_item2, quantity=5)

    def test_successful_order_reduces_quantity(self):
        url = reverse('place-order')
        data = {
            'store_id': self.store.id,
            'items': [
                {'menu_item_id': self.menu_item1.id, 'quantity': 2},
                {'menu_item_id': self.menu_item2.id, 'quantity': 1}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.inventory1.refresh_from_db()
        self.inventory2.refresh_from_db()
        self.assertEqual(self.inventory1.quantity, 8)
        self.assertEqual(self.inventory2.quantity, 4)

    def test_insufficient_quantity_returns_400(self):
        url = reverse('place-order')
        data = {
            'store_id': self.store.id,
            'items': [
                {'menu_item_id': self.menu_item1.id, 'quantity': 20}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_item_fails(self):
        self.menu_item1.is_active = False
        self.menu_item1.save()
        url = reverse('place-order')
        data = {
            'store_id': self.store.id,
            'items': [
                {'menu_item_id': self.menu_item1.id, 'quantity': 1}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_entire_order_rolls_back_if_one_item_invalid(self):
        url = reverse('place-order')
        data = {
            'store_id': self.store.id,
            'items': [
                {'menu_item_id': self.menu_item1.id, 'quantity': 2},
                {'menu_item_id': self.menu_item2.id, 'quantity': 10}  # Insufficient
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.inventory1.refresh_from_db()
        self.inventory2.refresh_from_db()
        self.assertEqual(self.inventory1.quantity, 10)  # Unchanged
        self.assertEqual(self.inventory2.quantity, 5)  # Unchanged
