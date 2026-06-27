# File: backend/core/urls.py
from django.contrib import admin
from django.urls import path
import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core Catalogs & Orders Endpoints
    path('api/dishes/', views.handle_dishes),
    path('api/addons/', views.handle_addons),
    path('api/orders/', views.handle_orders),
    path('api/materials/', views.handle_materials),
    path('api/admin/metrics/', views.get_admin_metrics),
    
    # ADD THESE MISSING AUTHENTICATION ROUTES NOW
    path('api/auth/register/', views.register_user),
    path('api/auth/login/', views.login_gateway),
    path('api/auth/addresses/', views.manage_address_book),
    path('api/restaurants/', views.handle_restaurants),
]