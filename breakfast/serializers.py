from rest_framework import serializers
from .models import Dish, AddOn, Order

class AddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddOn
        fields = '__all__'

class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    dish_name = serializers.CharField(source='dish.name', read_only=True)
    addon_details = AddOnSerializer(source='addons', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'dish', 'dish_name', 'addons', 'addon_details', 'address', 'total_price', 'status', 'created_at']