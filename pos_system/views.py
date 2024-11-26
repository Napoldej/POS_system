from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from .forms import CategoryForm, ProductForm, InventoryForm, CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, Avg
from django.db.models.functions import TruncMonth
from decimal import Decimal



@login_required
def home(request):
    number_category = len(Categories.objects.all())
    number_product = len(Product.objects.all())
    number_order = len(Payment.objects.all())
    
    product_performance_data = OrderItems.objects.values('product') \
        .annotate(
            total_sales=Sum(F('quantity') * F('price_per_unit')),
            total_quantity_sold=Sum('quantity')
        ) \
        .order_by('-total_quantity_sold')
    top_performing_products = []
    for entry in product_performance_data:
        product = Product.objects.get(id=entry['product'])
        top_performing_products.append({
            'product_name': product.product_name,
            'total_sales': entry['total_sales'],
            'total_quantity_sold': entry['total_quantity_sold'],
        })

    # Returning the context for rendering
    context = {
        'number_category': number_category,
        'number_product': number_product,
        'number_order': number_order,
        'top_performing_products': top_performing_products
    }

    return render(request, 'pos_system/home.html', context)

@login_required
def logout(request):
    logout(request)
    return redirect('pos-system:login')

def signup(request):
    """Register a new user."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # get named fields from the form data
            username = form.cleaned_data.get("username")
            # password input field is named 'password1'
            raw_passwd = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_passwd)
            login(request, user)  # Log the user in
            return redirect('pos-system:home')
        else:
            print(form.errors)
    else:
        # create a user form and display it the signup page
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


class CategoryList(generic.ListView):
    template_name = 'pos_system/list_category.html'
    context_object_name = 'category_list'
    
    def get_queryset(self):
        return Categories.objects.all()
    
@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('pos-system:category-list')) 
    else:
        form = CategoryForm()
    return render(request, 'pos_system/add_category.html', {'form': form})

@login_required
def edit_category(request,category_id):
    print(f"User Authenticated: {request.user.is_authenticated}, User: {request.user}")
    print(request.method)
    category=  get_object_or_404(Categories, pk=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('pos-system:category-list')
        else:
            return None
    else:
        form = CategoryForm(instance=category)
    return render(request, 'pos_system/edit_category.html', {'form': form, 'category': category})

@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Categories, id=category_id)
    category.delete()
    return redirect('pos-system:category-list')

class ProductList(generic.ListView):
    template_name = 'pos_system/product_list.html'
    context_object_name = 'product_list'
    
    def get_queryset(self):
        return Product.objects.all()
    
@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pos-system:product-list')
    else:
        form = ProductForm()
    return render(request, 'pos_system/add_product.html', {'form': form})
    

@login_required
def edit_product(request, product_id):
    product =  get_object_or_404(Product, id = product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('pos-system:product-list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'pos_system/edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('pos-system:product-list')



@login_required
def add_product_to_order(request):
    """
    This view creates an order if none exists for the user and adds products to the order.
    Upon completion, it redirects to the Payment object for processing payment details.
    """
    user = request.user
    # Check if the user already has a pending order
    existing_order = Order.objects.filter(user=user, queue__status='PENDING').first()
    if existing_order:
        order = existing_order
    else:
        queue = Queue.objects.create(status='PENDING')
        order = Order.objects.create(user=user, queue=queue)

    products = Product.objects.all()
    order_item = OrderItems.objects.all()
    tax_rate = Decimal('0.7') # Example: 10% tax
    tax_amount = order.total_amount * tax_rate
    grand_total = order.total_amount + tax_amount

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity"))
        product = Product.objects.get(id=product_id)
        price_per_unit = product.price
        if quantity > 0:
            # Check if the product already exists in the order
            order_item, created = OrderItems.objects.get_or_create(
                order=order,
                product=product,
                defaults={'quantity': quantity, 'price_per_unit': price_per_unit}
            )
            if not created:
                # Update the quantity if the product already exists in the order
                order_item.quantity += quantity
                order_item.save()

        # Update the total amount of the order
        order.total_amount = sum(
            item.quantity * item.price_per_unit for item in order.items.all()
        )
        order.save()
    
    return render(request, 'pos_system/pos.html', {
        'order': order,
        'products': products,
        'order_item': order_item,
        'tax_amount': tax_amount,
        'grand_total': grand_total,
    })
        


        


# @login_required
# def payment_detail(request, payment_id):
#     """
#     Displays the payment details for a specific Payment object.
#     """
#     payment = get_object_or_404(Payment, id=payment_id)

#     return render(request, 'pos_system/payment_detail.html', {'payment': payment})
    
    
class InventoryList(generic.ListView):
    template_name = 'pos_system/inventory_list.html'
    context_object_name = 'inventory_list'
    
    def get_queryset(self):
        return Inventory.objects.all()

@login_required
def add_inventory(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            product_id = request.POST.get('product_name')
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                form.add_error('product_name', 'Selected product does not exist.')
                return render(request, 'pos_system/add_inventory.html', {'form': form, 'products': Product.objects.all()})
            inventory = form.save(commit=False)
            inventory.product = product
            inventory.save()     
            return redirect('pos-system:inventory-list')
    else:
        form = InventoryForm()

    products = Product.objects.all()
    return render(request, 'pos_system/add_inventory.html', {'form': form, 'products': products})


@login_required
def edit_inventory(request, inventory_id):
    inventory =  get_object_or_404(Inventory, id=inventory_id)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            return redirect('pos-system:inventory-list')
    else:
        form = InventoryForm(instance=inventory)
    return render(request, 'pos_system/edit_inventory.html', {'form': form, 'inventory': inventory})

@login_required
def delete_inventory(request, inventory_id):
    inventory = get_object_or_404(Inventory, id=inventory_id)
    inventory.delete()
    return redirect('pos-system:inventory-list')
    
@login_required
def sales_insights(request):
    """Comprehensive sales insights dashboard"""
    # Average Order Value
    avg_order_value = Order.objects.aggregate(
        avg_value=Avg('total_amount')
    )['avg_value'] or 0

    # Most Recent Orders
    recent_orders = Order.objects.order_by('-timestamp')[:10]

    # Sales by Category
    category_sales = Categories.objects.annotate(
        total_revenue=Sum(
            F('product__order_items__quantity') * F('product__order_items__price_per_unit')
        )
    )
    # Top Selling Products
    top_products = Product.objects.annotate(
    total_sales=Sum('price')  # Sum of sales price for each product
    ).order_by('-total_sales')

    # Products Never Sold
    never_sold_products = Product.objects.filter(quantity_sold=0)

    # Monthly Sales Trend
    monthly_sales = Order.objects.annotate(
        month=TruncMonth('timestamp')
    ).values('month').annotate(
        total_sales=Sum('total_amount')
    ).order_by('month')

    context = {
        'avg_order_value': avg_order_value,
        'recent_orders': recent_orders,
        'category_sales': category_sales,
        'top_products': top_products,
        'never_sold_products': never_sold_products,
        'monthly_sales_trend': monthly_sales
    }

    return render(request, 'pos_system/sales_insights.html/', context)

@login_required
def customer_insights(request):
    """Customer spending and order analytics"""
    # Customer Lifetime Value
    customer_lifetime_value = User.objects.annotate(
        total_spending=Sum('order__total_amount')
    )

    # Order Count by Payment Method
    payment_method_orders = PaymentMethod.objects.annotate(
        order_count=Count('payments'),
        total_revenue=Sum('payments__grand_total')
    )

    # Recent Customer Orders
    recent_customer_orders = Order.objects.select_related('user').order_by('-timestamp')[:20]

    context = {
        'customer_lifetime_value': customer_lifetime_value,
        'payment_method_orders': payment_method_orders,
        'recent_customer_orders': recent_customer_orders
    }

    return render(request, 'pos_system/customer_insights.html', context)

@login_required
def inventory_performance(request):
    """Inventory performance and stock insights"""
    # Low Stock Products
    low_stock_products = Inventory.objects.filter(quantity__lt=10)

    # Product Stock vs Sales
    product_stock_performance = Product.objects.annotate(
        total_sales=Sum('orderitems__quantity'),
        current_stock=F('inventory__quantity')
    )

    # Restock Recommendations
    products_needing_restock = [
        product for product in product_stock_performance 
        if product.current_stock < (product.total_sales * 0.5)
    ]

    context = {
        'low_stock_products': low_stock_products,
        'product_stock_performance': product_stock_performance,
        'restock_recommendations': products_needing_restock
    }

    return render(request, 'pos_system/inventory_performance.html', context)