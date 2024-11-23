from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, View
from django.http import JsonResponse
from .models import Product, Categories, Order, OrderItems, Customer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

class HomePageView(ListView):
    model = Product
    template_name = 'shop/home.html'
    context_object_name = 'products'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categories.objects.all()
        return context
    
    def get_queryset(self):
        queryset = Product.objects.filter(stock_status=True)
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(categories__category_name=category)
            
        # Filter by search query
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(product_name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            
        # Filter by price range
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=float(max_price))
            
        return queryset

class CartView(LoginRequiredMixin, View):
    template_name = 'shop/cart.html'
    
    def get(self, request):
        # Get or create cart order
        cart_order, created = Order.objects.get_or_create(
            employee=request.user,
            customer=Customer.objects.first(),  # You might want to handle this differently
            defaults={'total_amount': 0}
        )
        
        # Get cart items
        cart_items = OrderItems.objects.filter(order=cart_order)
        
        context = {
            'cart_items': cart_items,
            'total': cart_order.total_amount,
        }
        return render(request, self.template_name, context)

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        
        # Get or create cart order
        cart_order, created = Order.objects.get_or_create(
            employee=request.user,
            customer=Customer.objects.first(),  # You might want to handle this differently
            defaults={'total_amount': 0}
        )
        
        # Get or create order item
        order_item, created = OrderItems.objects.get_or_create(
            order=cart_order,
            product=product,
            defaults={
                'quantity': 0,
                'price_per_unit': product.price
            }
        )
        
        # Update quantity
        order_item.quantity += 1
        order_item.save()
        
        # Update order total
        cart_order.total_amount += product.price
        cart_order.save()
        
        return JsonResponse({
            'success': True,
            'cart_total': cart_order.total_amount,
            'item_count': OrderItems.objects.filter(order=cart_order).count()
        })

class UpdateCartView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        order_item = get_object_or_404(OrderItems, id=item_id)
        action = request.POST.get('action')
        
        if action == 'remove':
            # Update order total
            order_item.order.total_amount -= (order_item.price_per_unit * order_item.quantity)
            order_item.order.save()
            order_item.delete()
        else:
            quantity = int(request.POST.get('quantity', 1))
            old_quantity = order_item.quantity
            order_item.quantity = quantity
            order_item.save()
            
            # Update order total
            quantity_difference = quantity - old_quantity
            order_item.order.total_amount += (order_item.price_per_unit * quantity_difference)
            order_item.order.save()
        
        return JsonResponse({
            'success': True,
            'cart_total': order_item.order.total_amount
        })