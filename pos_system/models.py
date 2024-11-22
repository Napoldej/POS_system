from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

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
    
class Employees(AbstractUser):
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(unique= True , null = False, blank = False)
    hired_data = models.DateField("Hired date",auto_now_add=True)
    groups = models.ManyToManyField(
        Group,
        related_name="employees_groups",  # Avoid conflict with default user_set
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="employees_permissions",  # Avoid conflict with default user_set
        blank=True
    )
    
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    
class Customer(models.Model):
    customer_name  = models.CharField(max_length= 100, choices= PRODUCT_CATEGORY,null = True , blank = True)
    
    def __str__(self):
        return f"Customer : {self.customer_name}"
        
    
class Order(models.Model):
    employee = models.ForeignKey(Employees, on_delete= models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete= models.CASCADE)
    total_amount = models.DecimalField(max_digits= 6, decimal_places= 2, default= 0.00)
    timestamp = models.DateTimeField("Order At", auto_now_add= True)
    
    def __str__(self):
        return (f"Order : {self.id},Employee : {self.employee}, Customer : {self.customer}," 
                f"total_amount : {self.total_amount}", 
                f"timestamp: {self.timestamp}")
    
class Categories(models.Model):
    category_name = models.CharField(max_length= 100, null = False, blank = False)
    
class Product(models.Model):
    product_name = models.CharField(max_length= 100, null = False, blank = False)
    description = models.CharField(max_length= 100, null = False, blank = False)
    price = models.DecimalField(max_digits= 6, decimal_places= 2, default= 0.00)
    categories = models.ForeignKey(Categories, on_delete= models.CASCADE)
    stock_status = models.BooleanField(default= False)
    
    def __str__(self):
        return f"Product: {self.product_name}, Price : {self.price}, Status : {self.stock_status}"

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

    def __str__(self):
        return f"Order: {self.order.id}, Product: {self.product.product_name}, Quantity: {self.quantity}, Price per unit: {self.price_per_unit}"
    
    
class PaymentMethod(models.Model):
    method_name = models.CharField(max_length= 100, choices= PAYMENT_METHOD ,null = False, blank = False)
    
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete= models.CASCADE, related_name='payments')
    customer = models.ForeignKey(Customer, on_delete= models.CASCADE, related_name='payments')
    method = models.ForeignKey(PaymentMethod, on_delete= models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits= 6, decimal_places= 2, default= 0.00)
    
    def __str__(self):
        return f"Order: {self.order.id}, Customer: {self.customer.customer_name}, Method: {self.method.method_name}, Amount: {self.amount}"
    
class Receipt(models.Model):
    order = models.ForeignKey(Order, on_delete= models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete= models.CASCADE)
    
    @property
    def order_detail(self):
        # Retrieve all related order items
        items = OrderItems.objects.filter(order=self)
        detail_list = [f"{item.quantity} {item.product.product_name}" for item in items]
        return ", ".join(detail_list)
    
    def __str__(self):
        return f"Receipt: Order ID {self.order.id}, Customer: {self.customer.customer_name}, Order Details: {self.order_detail}"
    