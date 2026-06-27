from rest_framework import viewsets, permissions
from .models import Dish, AddOn, Order
from .serializers import DishSerializer, AddOnSerializer, OrderSerializer

class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    # Admin roles can be defined here later, public can read

class AddOnViewSet(viewsets.ModelViewSet):
    queryset = AddOn.objects.all()
    serializer_class = AddOnSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at') # Newest orders first
    serializer_class = OrderSerializer