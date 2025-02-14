from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    ROLE = (
        ('ADMIN', 'Admin'),
        ('CUSTOMER', 'Customer'),
    )
    role = models.CharField(max_length=15, choices=ROLE, default='CUSTOMER')
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.username
    

class Category(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='images/category', null=True, blank=True)

    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=150)
    price = models.IntegerField()
    image = models.ImageField(upload_to='images/product')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def update_total_price(self):
        self.total_price = sum(item.total_price for item in self.cart_items.all())
        self.save()

    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity  # avtomatik narx hisoblash
        super().save(*args, **kwargs)



class Orders(models.Model):
    STATUS = (
        ('NEW', 'New'),
        ('PROCESSING', 'Processing'),
        ('DELIVERED', 'Delivered'),
    )
    status = models.CharField(max_length=10, choices=STATUS, default='NEW')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    cart_items = models.ManyToManyField(CartItem)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.status} ({self.user})"
    
    @property
    def total_items(self):
        return len(self.cart_items.all())
    


class OrderItem(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    
    @property
    def total_price(self):
        return self.quantity * self.price
    