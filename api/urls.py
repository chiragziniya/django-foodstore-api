from django.urls import path
from . import views

urlpatterns = [
    path('stores/<int:store_id>/menu/', views.StoreMenuView.as_view(), name='store-menu'),
    path('inventory/<int:menu_item_id>/', views.InventoryUpdateView.as_view(), name='inventory-update'),
    path('orders/', views.PlaceOrderView.as_view(), name='place-order'),
]