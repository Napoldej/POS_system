from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.


PAYMENT_METHOD = (
    ("CASH", "Cash"),
    ("PROMPTPAY", "Promptpay"),
    ("CREDIT CARD", "credit card"),
    ("DEBIT CARD", "debit card"),
    )

PRODUCT_CATEGORY = [
    ("BEVERAGES", "beverages"),
    ("DESSERTS", "desserts"),
    ("SNACKS", "snacks"),
    ("BREAKFAST_ITEMS", "breakfast items"),
]
    
STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('PROCESSING', 'Processing'),
    ('COMPLETED', 'Completed'),
    ('CANCELED', 'Canceled'),
]    
    
class Queue(models.Model):
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(default=timezone.now)
  
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    queue = models.ForeignKey(Queue, on_delete= models.CASCADE)
    total_amount = models.DecimalField(max_digits= 6, decimal_places= 2, default= 0.00)
    timestamp = models.DateTimeField("Order At", auto_now_add= True)
    
    @classmethod
    def get_orders_by_date_range(cls, start_date, end_date):
        return cls.objects.filter(timestamp__range=[start_date, end_date])
    
    
    def __str__(self):
        return f"Order : {self.id}"
    
class Categories(models.Model):
    category_name = models.CharField(max_length= 100, null = False, blank = False)
    description = models.TextField(null = False, blank = False, max_length= 1000, default= "")
    
    def __str__(self):
        return f"{self.category_name}"
    
class Product(models.Model):
    product_name = models.CharField(max_length= 100, null = False, blank = False)
    description = models.CharField(max_length= 100, null = False, blank = False)
    price = models.DecimalField(max_digits= 6, decimal_places= 2, default= 0.00)
    categories = models.ForeignKey(Categories, on_delete= models.CASCADE)
    stock_status = models.BooleanField(default= False)
    quantity_sold = models.PositiveIntegerField(default=0)
    sales_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def never_sold(cls):
        return cls.objects.filter(quantity_sold=0)
    
    def __str__(self):
        return f"Product: {self.product_name}"

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    quantity = models.IntegerField(default= 0)
    cost = models.DecimalField(max_digits= 6, decimal_places= 2, default= 0.00)
    last_restocked = models.DateField(auto_now_add= True)
    
    def __str__(self):
        return f"Product : {self.product}, Quantity: {self.quantity}, Cost : {self.cost}"
    
    
class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=0)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.price_per_unit = self.product.price  # Ensure the price is up-to-date
        super().save(*args, **kwargs)
        
    @property
    def total_amount(self):
        total = self.quantity * float(self.price_per_unit)
        return str(total)

    def __str__(self):
        return f"Order: {self.order.id}, Product: {self.product.product_name}, Quantity: {self.quantity}, Price per unit: {self.price_per_unit}"
    
    
class PaymentMethod(models.Model):
    method_name = models.CharField(max_length= 100, choices= PAYMENT_METHOD ,null = False, blank = False)


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete= models.CASCADE, related_name='payments')
    queue = models.ForeignKey(Queue, on_delete= models.CASCADE)
    method = models.ForeignKey(PaymentMethod, on_delete= models.CASCADE, related_name='payments')
    grand_total = models.FloatField(default=0)
    tax_amount = models.FloatField(default=0)
    tax = models.FloatField(default=0)
    tendered_amount = models.FloatField(default=0)
    amount_change = models.FloatField(default=0)
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True)

    def calculate_total(self):
        total = sum(item.price_per_unit * item.quantity for item in self.order.items.all())
        self.grand_total = total + self.tax_amount
        self.save()

    def __str__(self):
        return f"Order: {self.order.id},  ,Method: {self.method.method_name}, Amount: {self.amount}"
    
    

