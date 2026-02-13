from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Store, MenuItem, Inventory
from .serializers import MenuItemSerializer, InventorySerializer, PlaceOrderSerializer

class StoreMenuView(generics.ListAPIView):
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        store_id = self.kwargs['store_id']
        return MenuItem.objects.filter(store_id=store_id).select_related('inventory')

class InventoryUpdateView(APIView):
    def patch(self, request, menu_item_id):
        menu_item = get_object_or_404(MenuItem, id=menu_item_id)
        quantity = request.data.get('quantity')
        if quantity is None or quantity < 0:
            return Response({'error': 'Quantity must be >= 0'}, status=status.HTTP_400_BAD_REQUEST)
        
        inventory, created = Inventory.objects.get_or_create(menu_item=menu_item, defaults={'quantity': quantity})
        if not created:
            inventory.quantity = quantity
            inventory.save()
        
        serializer = InventorySerializer(inventory)
        return Response(serializer.data)

class PlaceOrderView(APIView):
    def post(self, request):
        serializer = PlaceOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        store_id = serializer.validated_data['store_id']
        items = serializer.validated_data['items']
        
        store = get_object_or_404(Store, id=store_id)
        
        # Validate all items first
        for item in items:
            menu_item_id = item['menu_item_id']
            order_quantity = item['quantity']
            
            menu_item = get_object_or_404(MenuItem, id=menu_item_id, store=store)
            
            if not menu_item.is_active:
                return Response({'error': f'Menu item {menu_item.name} is inactive'}, status=status.HTTP_400_BAD_REQUEST)
            
            inventory = Inventory.objects.filter(menu_item=menu_item).first()
            if not inventory or inventory.quantity < order_quantity:
                return Response({'error': f'Insufficient quantity for {menu_item.name}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # All valid, now deduct
        with transaction.atomic():
            for item in items:
                menu_item_id = item['menu_item_id']
                order_quantity = item['quantity']
                
                menu_item = MenuItem.objects.get(id=menu_item_id, store=store)
                inventory = Inventory.objects.get(menu_item=menu_item)
                
                inventory.quantity -= order_quantity
                inventory.save()
        
        return Response({'message': 'Order placed successfully'}, status=status.HTTP_201_CREATED)
