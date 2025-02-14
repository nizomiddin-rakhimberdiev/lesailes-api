from rest_framework import serializers
from .models import CustomUser, Product, CartItem, Cart, Orders, OrderItem
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        return {"user": user}

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Cart
        fields = ['id', 'user', 'cart_items', 'total_price']

class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    
    class Meta:
        model = Orders
        fields = ['id', 'user', 'order_items', 'total_price', 'status', 'created_at', 'total_items']