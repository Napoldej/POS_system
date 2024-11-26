from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from .forms import CategoryForm, ProductForm, InventoryForm, CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required




@login_required
def home(request):
    number_category = len(Categories.objects.all())
    number_product = len(Product.objects.all())
    number_order = len(Payment.objects.all())
    context=  {
        'number_category': number_category,
        'number_product' : number_product,
        'number_order' : number_order,
    }
    return  render(request,'pos_system/home.html', context= context)


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
    queue = Queue.objects.create(status='PENDING')
    order = Order.objects.create(user=user, queue=queue)
    products = Product.objects.all()
    order_item = OrderItems.objects.all()
    tax_rate = 0.1  # Example: 10% tax
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
            item.quantity * item.price_per_unit for item in OrderItems.objects.all()
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
            product = Product.objects.get(id=product_id)
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
    
