from django.urls import path
from . import views

app_name = 'pos-system'

urlpatterns = [
    path('', views.home, name='home'),
    path('add/category/', views.add_category, name='add_category'),
    path('category-list/', views.CategoryList.as_view(), name='category-list'),
    path('edit-category/<int:category_id>', views.edit_category, name='edit_category'),
    path('delete/category/<int:category_id>', views.delete_category, name='delete_category'),
    # path('cart/update/<int:item_id>/', UpdateCartView.as_view(), name='update_cart'),
]