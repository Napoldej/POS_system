from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from .models import *
from .forms import CategoryForm, ProductForm, InventoryForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
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

@login_required
def signup(request):
    """Register a new user."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # get named fields from the form data
            username = form.cleaned_data.get("username")
            # password input field is named 'password1'
            raw_passwd = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_passwd)
            login(request, user)
            return redirect('pos-system:home')
    else:
        # create a user form and display it the signup page
        form = UserCreationForm()
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
            return redirect('pos-system:category-list')
    else:
        form = CategoryForm()
    return render(request, 'pos_system/add_category.html', {'form': form})

@login_required

def edit_category(request,category_id):
    category=  get_object_or_404(Categories, pk=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('pos-system:category-list')
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
    
    
class InventoryList(generic.ListView):
    template_name = 'pos_system/inventory_list.html'
    context_object_name = 'inventory_list'
    
    def get_queryset(self):
        return Inventory.objects.all()
    
def add_inventory(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pos-system:inventory-list')
    else:
        form = InventoryForm()
    return render(request, 'pos_system/add_inventory.html')


def edit_inventory(request, inventory_id):
    inventory =  get_object_or_404(Inventory, id = inventory_id)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            return redirect('pos-system:inventory-list')
    else:
        form = InventoryForm(instance=inventory)
    return render(request, 'pos_system/edit_inventory.html', {'form': form, 'inventory': inventory})


def delete_inventory(request, inventory_id):
    inventory = get_object_or_404(Inventory, id=inventory_id)
    inventory.delete()
    return redirect('pos-system:inventory-list')
    