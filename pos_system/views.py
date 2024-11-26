from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.http import HttpResponse
from .models import *
from .forms import CategoryForm

def home(request):
    number_category = len(Categories.objects.all())
    number_product = len(Product.objects.all())
    number_order = len(Receipt.objects.all())
    context=  {
        'number_category': number_category,
        'number_product' : number_product,
        'number_order' : number_order,
    }
    return  render(request,'pos_system/home.html', context= context)


class CategoryList(generic.ListView):
    template_name = 'pos_system/list_category.html'
    context_object_name = 'category_list'
    
    def get_queryset(self):
        return Categories.objects.all()
    

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pos-system:category-list')
    else:
        form = CategoryForm()
    return render(request, 'pos_system/add_category.html', {'form': form})

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


def delete_category(request, category_id):
    category = get_object_or_404(Categories, id=category_id)
    category.delete()
    return redirect('pos-system:category-list')


    
        
    