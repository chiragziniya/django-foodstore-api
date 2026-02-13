from django.core.management.base import BaseCommand
from api.models import Store, MenuItem, Inventory


class Command(BaseCommand):
    help = 'Seeds the database with sample data for testing'

    def handle(self, *args, **kwargs):
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Inventory.objects.all().delete()
        MenuItem.objects.all().delete()
        Store.objects.all().delete()

        # Create Stores
        self.stdout.write('Creating stores...')
        store1 = Store.objects.create(name='Downtown Food Court')
        store2 = Store.objects.create(name='Campus Cafeteria')
        
        # Create Menu Items for Store 1 (Downtown Food Court)
        self.stdout.write('Creating menu items for Downtown Food Court...')
        
        # Items with different inventory states
        burger = MenuItem.objects.create(
            store=store1,
            name='Veg Burger',
            price=129.00,
            is_active=True
        )
        Inventory.objects.create(menu_item=burger, quantity=3)  # almost_gone=True
        
        pizza = MenuItem.objects.create(
            store=store1,
            name='Margherita Pizza',
            price=199.00,
            is_active=True
        )
        Inventory.objects.create(menu_item=pizza, quantity=15)  # Normal stock
        
        pasta = MenuItem.objects.create(
            store=store1,
            name='Penne Pasta',
            price=149.00,
            is_active=True
        )
        Inventory.objects.create(menu_item=pasta, quantity=5)  # almost_gone=True (threshold)
        
        sandwich = MenuItem.objects.create(
            store=store1,
            name='Grilled Sandwich',
            price=89.00,
            is_active=True
        )
        Inventory.objects.create(menu_item=sandwich, quantity=0)  # Out of stock
        
        fries = MenuItem.objects.create(
            store=store1,
            name='French Fries',
            price=79.00,
            is_active=False  # Inactive item
        )
        Inventory.objects.create(menu_item=fries, quantity=10)  # Not available (inactive)
        
        salad = MenuItem.objects.create(
            store=store1,
            name='Caesar Salad',
            price=119.00,
            is_active=True
        )
        # No inventory created - will default to quantity=0
        
        # Create Menu Items for Store 2 (Campus Cafeteria)
        self.stdout.write('Creating menu items for Campus Cafeteria...')
        
        coffee = MenuItem.objects.create(
            store=store2,
            name='Cappuccino',
            price=59.00,
            is_active=True
        )
        Inventory.objects.create(menu_item=coffee, quantity=50)
        
        samosa = MenuItem.objects.create(
            store=store2,
            name='Samosa',
            price=25.00,
            is_active=True
        )
        Inventory.objects.create(menu_item=samosa, quantity=2)  # almost_gone=True
        
        dosa = MenuItem.objects.create(
            store=store2,
            name='Masala Dosa',
            price=89.00,
            is_active=True
        )
        Inventory.objects.create(menu_item=dosa, quantity=8)
        
        juice = MenuItem.objects.create(
            store=store2,
            name='Orange Juice',
            price=49.00,
            is_active=True
        )
        Inventory.objects.create(menu_item=juice, quantity=1)  # almost_gone=True
        
        milkshake = MenuItem.objects.create(
            store=store2,
            name='Chocolate Milkshake',
            price=99.00,
            is_active=False  # Inactive
        )
        Inventory.objects.create(menu_item=milkshake, quantity=3)  # almost_gone but inactive
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== Data Seeding Complete ==='))
        self.stdout.write(self.style.SUCCESS(f'Created {Store.objects.count()} stores'))
        self.stdout.write(self.style.SUCCESS(f'Created {MenuItem.objects.count()} menu items'))
        self.stdout.write(self.style.SUCCESS(f'Created {Inventory.objects.count()} inventory records'))
        
        self.stdout.write('\n--- Store Details ---')
        for store in Store.objects.all():
            self.stdout.write(f'\nStore ID: {store.id} - {store.name}')
            items = MenuItem.objects.filter(store=store).select_related('inventory')
            for item in items:
                try:
                    qty = item.inventory.quantity
                except:
                    qty = 0
                status = '✓ Active' if item.is_active else '✗ Inactive'
                self.stdout.write(f'  - ID:{item.id} {item.name} (₹{item.price}) | Qty: {qty} | {status}')
        
        self.stdout.write('\n--- Testing Scenarios ---')
        self.stdout.write('1. Almost Gone Items (quantity <= 5 and > 0):')
        self.stdout.write(f'   - Store {store1.id}: Veg Burger (qty=3), Penne Pasta (qty=5)')
        self.stdout.write(f'   - Store {store2.id}: Samosa (qty=2), Orange Juice (qty=1)')
        
        self.stdout.write('\n2. Out of Stock (quantity = 0):')
        self.stdout.write(f'   - Store {store1.id}: Grilled Sandwich (qty=0), Caesar Salad (no inventory)')
        
        self.stdout.write('\n3. Inactive Items:')
        self.stdout.write(f'   - Store {store1.id}: French Fries (qty=10, inactive)')
        self.stdout.write(f'   - Store {store2.id}: Chocolate Milkshake (qty=3, inactive)')
        
        self.stdout.write('\n4. Normal Stock:')
        self.stdout.write(f'   - Store {store1.id}: Margherita Pizza (qty=15)')
        self.stdout.write(f'   - Store {store2.id}: Cappuccino (qty=50), Masala Dosa (qty=8)')
        
        self.stdout.write('\n--- API Testing Commands ---')
        self.stdout.write(f'\nList menu for store {store1.id}:')
        self.stdout.write(f'curl -X GET http://127.0.0.1:8000/stores/{store1.id}/menu/')
        
        self.stdout.write(f'\nUpdate inventory for item {burger.id}:')
        self.stdout.write(f'curl -X PATCH http://127.0.0.1:8000/inventory/{burger.id}/ -H "Content-Type: application/json" -d "{{\\"quantity\\": 10}}"')
        
        self.stdout.write(f'\nPlace order for store {store1.id}:')
        self.stdout.write(f'curl -X POST http://127.0.0.1:8000/orders/ -H "Content-Type: application/json" -d "{{\\"store_id\\": {store1.id}, \\"items\\": [{{\\"menu_item_id\\": {pizza.id}, \\"quantity\\": 2}}]}}"')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Database seeded successfully!\n'))
