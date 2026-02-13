from django.db import models

ALMOST_GONE_THRESHOLD = 5

class Store(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        return self.is_active and self.inventory.quantity > 0 if hasattr(self, 'inventory') else False

    @property
    def almost_gone(self):
        if hasattr(self, 'inventory'):
            quantity = self.inventory.quantity
            return quantity > 0 and quantity <= ALMOST_GONE_THRESHOLD
        return False

class Inventory(models.Model):
    menu_item = models.OneToOneField(MenuItem, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inventory for {self.menu_item.name}"
