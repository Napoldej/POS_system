from django.urls import path
from . import views

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
    path('create-order/', views.add_product_to_order, name='create-order'),
    path('inventory-list/', views.InventoryList.as_view(), name='inventory-list'),
    path('add/inventory/', views.add_inventory, name='add_inventory'),
    path('edit-inventory/<int:inventory_id>', views.edit_inventory, name='edit_inventory'),
    path('delete/inventory/<int:inventory_id>', views.delete_inventory, name='delete_inventory'),
    path('sales-insights/', views.sales_insights, name='sales-insights'),
    path('transaction/<int:order_id>', views.checkout, name='checkout'),
    path('item/delete/<int:item_id>', views.delete_item, name='delete_item'),
    path('customer-insights/', views.customer_insights, name='customer-insights'),
    # path("checkout/", views.checkout.as_view(), name="checkout"),
    path('inventory-insights/', views.inventory_performance, name='inventory-insights'),
    path('remove-order-item/<int:item_id>/', views.remove_order_item, name='remove-order-item'),
    path('process-checkout/', views.process_checkout, name='process-checkout'),
]
