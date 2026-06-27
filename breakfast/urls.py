from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DishViewSet, AddOnViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'dishes', DishViewSet)
router.register(r'addons', AddOnViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]