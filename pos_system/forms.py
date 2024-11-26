from django import forms
from .models import Categories, Product, Inventory
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = "__all__"
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")

    class Meta:
        model = User  # Use Django's default User model
        fields = ("username", "email", "password1", "password2")  # Include email here

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]  # Assign email field
        if commit:
            user.save()
        return user
    
class InventoryForm(forms.ModelForm):

    class Meta:
        model = Inventory
        fields = "__all__"
        exclude = ['product']
        
