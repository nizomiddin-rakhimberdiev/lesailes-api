from django.contrib import admin
from .models import CustomUser, Cart, CartItem, Category, OrderItem, Orders, Product

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Category)
admin.site.register(OrderItem)
admin.site.register(Orders)
admin.site.register(Product)