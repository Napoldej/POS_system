from django.urls import path
from .views import HomePageView, CartView, AddToCartView, UpdateCartView

urlpatterns = [
    path('home/', HomePageView.as_view(), name='home'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/<int:item_id>/', UpdateCartView.as_view(), name='update_cart'),
]