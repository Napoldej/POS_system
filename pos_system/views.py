from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from .models import *
from .forms import CategoryForm, ProductForm, InventoryForm, \
    CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, Avg, Count, Value, DecimalField
from django.db.models.functions import TruncMonth, Coalesce, TruncDate, Cast
from django.contrib import messages
from decimal import Decimal
from datetime import datetime, timedelta


@login_required
def home(request):
    """
    Displays the homepage with comprehensive statistics and insights.

    Parameters:
        request: HttpRequest object representing the current request.

    Returns:
        HttpResponse: Rendered homepage with context data.
    """
    # Time-based calculations
    today = timezone.now().date()
    week_ago = today - timezone.timedelta(days=7)
    month_ago = today - timezone.timedelta(days=30)

    # Basic Counts
    number_category = Categories.objects.count()
    number_product = Product.objects.count()
    number_orders = Order.objects.count()

    # Sales and Performance Analysis
    # Today's sales
    today_sales = Payment.objects.filter(date_added__date=today).aggregate(
        total_sales=Sum('grand_total', default=0)
    )['total_sales']

    # Weekly sales trend
    weekly_sales = Payment.objects.annotate(
        sale_date=TruncDate('date_added')
    ).values('sale_date').annotate(
        daily_sales=Sum('grand_total', default=0)
    ).order_by('sale_date')

    # Top Performing Products
    top_products = Product.objects.annotate(
        total_quantity_sold=Sum('order_items__quantity', default=0),
        total_sales=Sum(
            Cast('order_items__quantity', output_field=DecimalField()) * 
            Cast('order_items__price_per_unit', output_field=DecimalField()),
            default=0
        )
    ).order_by('-total_quantity_sold')[:5]

    # Category Performance
    category_performance = Categories.objects.annotate(
        total_products=Count('product'),
        total_sales=Sum(
            Cast('product__order_items__quantity', output_field=DecimalField()) * 
            Cast('product__order_items__price_per_unit', output_field=DecimalField()),
            default=0
        )
    ).order_by('-total_sales')[:3]

    # Inventory Analysis
    low_stock_products = Product.objects.filter(stock_status=False).count()

    # Payment Method Analysis
    payment_method_breakdown = PaymentMethod.objects.annotate(
        total_transactions=Count('payments'),
        total_amount=Sum('payments__grand_total', default=0)
    )

    # Order Status Analysis
    order_status_breakdown = Queue.objects.values('status').annotate(
        total_orders=Count('order')
    )

    context = {
        'number_category': number_category,
        'number_product': number_product,
        'number_orders': number_orders,
        'today_sales': today_sales,
        'weekly_sales': list(weekly_sales),
        'top_products': top_products,
        'category_performance': category_performance,
        'low_stock_products': low_stock_products,
        'payment_method_breakdown': payment_method_breakdown,
        'order_status_breakdown': order_status_breakdown,
    }

    return render(request, 'pos_system/home.html', context)


@login_required
def logout(request):
    """
    Logs out the current user and redirects to the login page.

    Parameters:
        request: HttpRequest object representing the current request.

    Returns:
        HttpResponseRedirect: Redirect to the login page.
    """
    logout(request)
    return redirect('pos-system:login')


def signup(request):
    """
    Handles user registration and logs in the user upon successful signup.

    Parameters:
        request: HttpRequest object representing the current request.

    Returns:
        HttpResponse: Rendered signup page with a form or redirect to the homepage.
    """
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
    """
    A view to list all categories.

    Attributes:
        template_name: Template used to display the list.
        context_object_name: Context variable name for categories in the template.
    """
    template_name = 'pos_system/list_category.html'
    context_object_name = 'category_list'

    def get_queryset(self):
        return Categories.objects.all()


@login_required
def add_category(request):
    """
    Adds a new category to the system.

    Parameters:
        request: HttpRequest object representing the current request.

    Returns:
        HttpResponse: Rendered form or redirect to category list.
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('pos-system:category-list'))
    else:
        form = CategoryForm()
    return render(request, 'pos_system/add_category.html', {'form': form})


@login_required
def edit_category(request, category_id):
    """
    Edits an existing category.

    Parameters:
        request: HttpRequest object representing the current request.
        category_id: ID of the category to edit.

    Returns:
        HttpResponse: Rendered form or redirect to category list.
    """
    category = get_object_or_404(Categories, pk=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('pos-system:category-list')
        else:
            return None
    else:
        form = CategoryForm(instance=category)
    return render(request, 'pos_system/edit_category.html',
                  {'form': form, 'category': category})


@login_required
def delete_category(request, category_id):
    """
    Deletes a category.

    Parameters:
        request: HttpRequest object representing the current request.
        category_id: ID of the category to delete.

    Returns:
        HttpResponseRedirect: Redirect to category list.
    """
    category = get_object_or_404(Categories, id=category_id)
    category.delete()
    return redirect('pos-system:category-list')


class ProductList(generic.ListView):
    """
    A view to list all products.

    Attributes:
        template_name: Template used to display the list.
        context_object_name: Context variable name for products in the template.
    """
    template_name = 'pos_system/product_list.html'
    context_object_name = 'product_list'

    def get_queryset(self):
        return Product.objects.all()


@login_required
def add_product(request):
    """
    Adds a new product to the system.

    Parameters:
        request: HttpRequest object representing the current request.

    Returns:
        HttpResponse: Rendered form or redirect to product list.
    """
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
    """
    Edits an existing product.

    Parameters:
        request: HttpRequest object representing the current request.
        product_id: ID of the product to edit.

    Returns:
        HttpResponse: Rendered form or redirect to product list.
    """
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('pos-system:product-list')
        else:
            print("win")
    else:
        form = ProductForm(instance=product)
    return render(request, 'pos_system/edit_product.html',
                  {'form': form, 'product': product})


@login_required
def delete_product(request, product_id):
    """
    Deletes a product.

    Parameters:
        request: HttpRequest object representing the current request.
        product_id: ID of the product to delete.

    Returns:
        HttpResponseRedirect: Redirect to product list.
    """
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('pos-system:product-list')


@login_required
def add_product_to_order(request):
    """
    This view creates an order if none exists for the user and adds products to the order.
    Upon completion, it redirects to the Payment object for processing payment details.

    Parameters:
    request: HttpRequest object representing the current request.

    Returns:
        HttpResponse: Rendered order details page.
    """
    user = request.user
    # Check if the user already has a pending order
    order = Order.objects.filter(user=user, queue__status='PENDING').first()
    if Order.objects.filter(user=user, queue__status='PENDING').exists():
        order = Order.objects.filter(user=user,
                                     queue__status='PENDING').first()
    else:
        queue = Queue.objects.create(status='PENDING')
        order = Order.objects.create(user=user, queue=queue)

    products = Product.objects.all()
    order_list = OrderItems.objects.filter(order=order)

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity"))
        product = Product.objects.get(id=product_id)
        inventory = Inventory.objects.filter(product=product).first()
        price_per_unit = product.price

        # Check if there is no inventory for the product
        if not inventory:
            messages.error(request, "Sorry, this product is currently out of stock.")
            return render(request, 'pos_system/pos.html', {
                'order': order,
                'products': products,
                'order_item': order_list,
            })

        if quantity > 0:
            # Check if the product already exists in the order
            order_item, created = OrderItems.objects.get_or_create(
                order=order,
                product=product,
                defaults={'quantity': quantity,
                          'price_per_unit': price_per_unit}
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
    tax_rate = float('0.07')  # Example: 10% tax
    tax_amount = float(order.total_amount) * tax_rate
    grand_total = float(order.total_amount) + tax_amount

    return render(request, 'pos_system/pos.html', {
        'order': order,
        'products': products,
        'order_item': order_list,
        'tax_amount': tax_amount,
        'grand_total': grand_total,
    })


def delete_item(request, item_id):
    """
    Deletes a specific item from an order.

    This function retrieves an `OrderItems` instance based on the provided `item_id`,
    deletes it from the database, and redirects the user to the order creation page.

    Args:
        request: The HTTP request object.
        item_id (int): The ID of the `OrderItems` instance to be deleted.

    Returns:
        HttpResponseRedirect: Redirects to the 'create-order' page.

    Raises:
        OrderItems.DoesNotExist: If no `OrderItems` instance is found with the given `item_id`.
    """
    order_item = OrderItems.objects.get(id=item_id)
    order_item.delete()
    return redirect('pos-system:create-order')


def checkout(request, order_id):
    """
    Processes the checkout for a given order, updates inventory, calculates taxes,
    and creates a payment record.

    This function performs the following steps:
    1. Marks the order's queue as "COMPLETE."
    2. Updates the inventory for each product in the order and adjusts stock status
       if the inventory runs out.
    3. Calculates the tax amount and grand total for the order.
    4. Creates a payment record with the specified payment method (default: Cash).
    5. Saves the changes and renders the transaction details.

    Args:
        request: The HTTP request object.
        order_id (int): The ID of the order to be checked out.

    Returns:
        HttpResponse: Renders the 'transaction.html' template with the order details,
                      order items, payment details, and product list.

    Raises:
        Order.DoesNotExist: If the order with the specified ID does not exist.
        Inventory.DoesNotExist: If the inventory record for a product is not found.
    """
    order = Order.objects.get(id=order_id)
    queue = order.queue
    queue.status = "COMPLETE"
    queue.save()
    product_list = []
    order_item = OrderItems.objects.filter(order=order)
    for item in order_item:
        product_list.append(item.product)
        inventory = Inventory.objects.get(product=item.product)
        inventory.quantity -= item.quantity
        if inventory.quantity <= 0:
            item.product.stock_status = False
            item.product.save()
        inventory.save()
    tax_rate = Decimal('0.07')
    tax_amount = order.total_amount * tax_rate
    grand_total_value = order.total_amount + tax_amount
    paymnet_method = PaymentMethod.objects.create(method_name='Cash')
    payment = Payment.objects.create(order=order, method=paymnet_method,
                                     queue=order.queue,
                                     tax_amount=tax_amount,
                                     grand_total=grand_total_value,
                                     tax=tax_rate)
    order.save()
    payment.save()
    return render(request, 'pos_system/transaction.html', {'order': order,
                                                           'order_item': order_item,
                                                           'payment': payment,
                                                           'product_list': product_list})


@login_required
def process_checkout(request):
    """
    Processes the checkout for the current order.

    This function:
    - Calculates tax and grand total for the order.
    - Creates a payment record for the order.
    - Updates inventory levels and product sales statistics.
    - Marks the order as completed.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the homepage or a receipt page upon success,
                              or redirects back to the order creation page on failure.
    """
    user = request.user

    # Find the current pending order
    order = Order.objects.filter(user=user, queue__status='PENDING').first()

    if not order:
        messages.error(request, "No active order found.")
        return redirect('pos-system:pos')

    try:
        # Calculate tax (using the same tax rate as in add_product_to_order view)
        tax_rate = Decimal('0.1')  # 10% tax
        tax_amount = order.total_amount * tax_rate
        grand_total = order.total_amount + tax_amount

        # Create a default payment method if not exists
        payment_method, _ = PaymentMethod.objects.get_or_create(
            method_name='CASH')

        # Create Payment record
        payment = Payment.objects.create(
            order=order,
            queue=order.queue,
            method=payment_method,
            grand_total=grand_total,
            tax_amount=tax_amount,
            tax=float(tax_rate * 100)
        )

        # Update product inventory and sales
        for item in order.items.all():
            product = item.product

            # Update product inventory
            inventory = Inventory.objects.filter(product=product).first()
            if inventory:
                inventory.quantity -= item.quantity
                inventory.save()

            # Update product sales statistics
            product.quantity_sold += item.quantity
            product.sales_total += Decimal(item.total_amount)
            product.save()

        # Mark the order as completed
        order.queue.status = 'COMPLETED'
        order.queue.save()

        # Redirect to payment detail or receipt
        return redirect(
            'pos-system:home')  # You can change this to a receipt page

    except Exception as e:
        messages.error(request, f"Checkout failed: {str(e)}")
        return redirect('pos-system:create-order')


@login_required
def remove_order_item(request, item_id):
    """
    Removes a specific item from the current order.

    Parameters:
        request (HttpRequest): The HTTP request object.
        item_id (int): The ID of the order item to be removed.

    Returns:
        HttpResponseRedirect: Redirects to the POS page or the order creation page upon failure.
    """
    try:
        order_item = get_object_or_404(OrderItems, id=item_id)
        order = order_item.order

        # Remove the item
        order_item.delete()

        # Recalculate order total
        order.total_amount = sum(
            item.quantity * item.price_per_unit for item in order.items.all()
        )
        order.save()

        return redirect('pos-system:pos')

    except Exception as e:
        messages.error(request, f"Failed to remove item: {str(e)}")
        return redirect('pos-system:create-order')

    # @login_required


# def payment_detail(request, payment_id):
#     """
#     Displays the payment details for a specific Payment object.
#     """
#     payment = get_object_or_404(Payment, id=payment_id)

#     return render(request, 'pos_system/payment_detail.html', {'payment': payment})


class InventoryList(generic.ListView):
    """
    A view to list all inventory records.

    Attributes:
        template_name (str): The template to render.
        context_object_name (str): The name of the context variable for inventory items.
    """
    template_name = 'pos_system/inventory_list.html'
    context_object_name = 'inventory_list'

    def get_queryset(self):
        return Inventory.objects.all()


@login_required
def add_inventory(request):
    """
    Adds a new inventory record.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered form for adding inventory or a redirect to the inventory list.
    """
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            product_id = request.POST.get('product_name')
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                form.add_error('product_name',
                               'Selected product does not exist.')
                return render(request, 'pos_system/add_inventory.html',
                              {'form': form,
                               'products': Product.objects.all()})
            product.stock_status = True
            product.save()
            inventory = form.save(commit=False)
            inventory.product = product

            # Check if inventory already exists for the product
            existing_inventory = Inventory.objects.filter(product=product)
            if existing_inventory.exists():
                # Add the new quantity to the existing inventory
                existing_inventory = existing_inventory.first()
                existing_inventory.quantity += inventory.quantity
                existing_inventory.save()
            else:
                # Save the new inventory
                inventory.save()

            return redirect('pos-system:inventory-list')
    else:
        form = InventoryForm()

    products = Product.objects.all()
    return render(request, 'pos_system/add_inventory.html',
                  {'form': form, 'products': products})


@login_required
def edit_inventory(request, inventory_id):
    """
    Edits an existing inventory record.

    Parameters:
        request (HttpRequest): The HTTP request object.
        inventory_id (int): The ID of the inventory record to edit.

    Returns:
        HttpResponse: Rendered form for editing inventory or a redirect to the inventory list.
    """
    inventory = get_object_or_404(Inventory, id=inventory_id)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            return redirect('pos-system:inventory-list')
    else:
        form = InventoryForm(instance=inventory)
    return render(request, 'pos_system/edit_inventory.html',
                  {'form': form, 'inventory': inventory})


@login_required
def delete_inventory(request, inventory_id):
    """
    Deletes an inventory record.

    Parameters:
        request (HttpRequest): The HTTP request object.
        inventory_id (int): The ID of the inventory record to delete.

    Returns:
        HttpResponseRedirect: Redirects to the inventory list.
    """
    inventory = get_object_or_404(Inventory, id=inventory_id)
    inventory.delete()
    return redirect('pos-system:inventory-list')


@login_required
def sales_insights(request):
    """
    Displays a comprehensive sales insights dashboard.

    Includes:
    - Average order value.
    - Most recent orders.
    - Sales by category.
    - Top-selling products.
    - Products never sold.
    - Monthly sales trends.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered dashboard with sales insights data.
    """
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
            F('product__order_items__quantity') * F(
                'product__order_items__price_per_unit')
        ),
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
    """
    Provides customer spending and order analytics.

    Includes:
    - Customer lifetime value.
    - Order count by payment method.
    - Recent customer orders.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered dashboard with customer insights data.
    """
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
    recent_customer_orders = Order.objects.select_related('user').order_by(
        '-timestamp')[:20]

    context = {
        'customer_lifetime_value': customer_lifetime_value,
        'payment_method_orders': payment_method_orders,
        'recent_customer_orders': recent_customer_orders
    }

    return render(request, 'pos_system/customer_insights.html', context)


@login_required
def inventory_performance(request):
    """
    Displays inventory performance and stock insights.

    Includes:
    - Low stock products.
    - Product stock versus sales performance.
    - Restock recommendations.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered dashboard with inventory performance data.
    """
    # Low Stock Products
    low_stock_products = Inventory.objects.filter(quantity__lt=10)

    # Product Stock vs Sales
    product_stock_performance = Product.objects.annotate(
        total_sales=Sum('order_items__quantity'),
        current_stock=F('inventory__quantity')
    )

    # Handle null values for current_stock
    product_stock_performance = product_stock_performance.annotate(
        current_stock=Coalesce('current_stock', Value(0))
    )

    # Restock Recommendations
    products_needing_restock = [
        product for product in product_stock_performance
        if product.current_stock < 10
    ]

    context = {
        'low_stock_products': low_stock_products,
        'product_stock_performance': product_stock_performance,
        'restock_recommendations': products_needing_restock
    }

    return render(request, 'pos_system/inventory_insights.html', context)
