from django.contrib import admin
from .models import Store, MenuItem, Inventory


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'store', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'store', 'created_at']
    search_fields = ['name', 'store__name']
    list_editable = ['is_active']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'menu_item', 'get_store', 'quantity', 'updated_at']
    list_filter = ['menu_item__store', 'updated_at']
    search_fields = ['menu_item__name', 'menu_item__store__name']
    
    def get_store(self, obj):
        return obj.menu_item.store.name
    get_store.short_description = 'Store'
    get_store.admin_order_field = 'menu_item__store'
