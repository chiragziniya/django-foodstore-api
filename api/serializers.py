from rest_framework import serializers
from .models import Store, MenuItem, Inventory, ALMOST_GONE_THRESHOLD

class MenuItemSerializer(serializers.ModelSerializer):
    quantity = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    almost_gone = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'quantity', 'is_available', 'almost_gone']

    def get_quantity(self, obj):
        return obj.inventory.quantity if hasattr(obj, 'inventory') else 0

    def get_is_available(self, obj):
        quantity = self.get_quantity(obj)
        return obj.is_active and quantity > 0

    def get_almost_gone(self, obj):
        quantity = self.get_quantity(obj)
        return quantity > 0 and quantity <= ALMOST_GONE_THRESHOLD

class InventorySerializer(serializers.ModelSerializer):
    is_available = serializers.SerializerMethodField()
    almost_gone = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = ['quantity', 'is_available', 'almost_gone']
        read_only_fields = ['is_available', 'almost_gone']

    def get_is_available(self, obj):
        return obj.menu_item.is_active and obj.quantity > 0

    def get_almost_gone(self, obj):
        return obj.quantity > 0 and obj.quantity <= ALMOST_GONE_THRESHOLD

class OrderItemSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class PlaceOrderSerializer(serializers.Serializer):
    store_id = serializers.IntegerField()
    items = OrderItemSerializer(many=True)