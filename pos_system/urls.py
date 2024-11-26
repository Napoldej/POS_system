from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'pos-system'

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    path('add/category/', views.add_category, name='add_category'),
    path('category-list/', views.CategoryList.as_view(), name='category-list'),
    path('edit-category/<int:category_id>', views.edit_category, name='edit_category'),
    path('delete/category/<int:category_id>', views.delete_category, name='delete_category'),
    path('product-list/', views.ProductList.as_view(), name='product-list'),
    path('add/product/', views.add_product, name='add_product'),
    path('edit-product/<int:product_id>', views.edit_product, name='edit_product'),
    path('delete/product/<int:product_id>', views.delete_product, name='delete_product'),
    path('inventory-list/', views.InventoryList.as_view(), name='inventory-list'),
    path('add/inventory/', views.add_inventory, name='add_inventory'),
    path('edit-inventory/<int:inventory_id>', views.edit_inventory, name='edit_inventory'),
    path('delete/inventory/<int:inventory_id>', views.delete_inventory, name='delete_inventory'),
]