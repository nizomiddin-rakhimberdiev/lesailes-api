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
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.FloatField(source='product.price', read_only=True)
    total_price = serializers.FloatField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'user', 'product', 'product_name', 'product_price', 'quantity', 'total_price']
        read_only_fields = ['user']  # Foydalanuvchi avtomatik o‘rnatiladi

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Miqdor kamida 1 bo‘lishi kerak.")
        return value

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'product_name', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )

    class Meta:
        model = Orders
        fields = ['id', 'user', 'created_at', 'updated_at', 'status', 'total_price', 'address', 'items']
        read_only_fields = ['user', 'total_price', 'items', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')  # `items` ni ajratib olish
        order = Orders.objects.create(**validated_data)  # Avval orderni yaratish

        total_price = 0  # Umumiy narxni hisoblash uchun

        # OrderItem larni yaratish
        for item in items_data:
            product_id = item.get('product')
            quantity = item.get('quantity')

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError({"product": f"Mahsulot ID {product_id} topilmadi."})

            item_price = product.price * quantity  # Narxni hisoblash
            total_price += item_price  # Jami narxga qo'shish

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=item_price  # Set the price
            )

        order.total_price = total_price  # Jami narxni yangilash
        order.save()  # Orderni saqlash

        return order


# class OrderSerializer(serializers.ModelSerializer):
#     items = serializers.ListField(
#         child=serializers.DictField(), write_only=True
#     )
#     address = serializers.CharField(required=False, allow_blank=True)
#     class Meta:
#         model = Orders
#         fields = [
#             'id', 'user', 'created_at', 'updated_at', 'status', 'total_price', 'address', 'items'
#         ]
#
#     def create(self, validated_data):
#         items_data = validated_data.pop('items')  # `items`ni ajratib olish
#         order = Orders.objects.create(**validated_data)  # Buyurtmani yaratish
#
#         # `items`ni qayta ishlash va `OrderItem`larni yaratish
#         for item in items_data:
#             product_id = item.get('product')
#             quantity = item.get('quantity')
#
#             # `Product` obyektini olish
#             try:
#                 product = Product.objects.get(id=product_id)
#             except Product.DoesNotExist:
#                 raise serializers.ValidationError({"product": f"Product with id {product_id} does not exist."})
#
#             # `price` qiymatini hisoblash va `OrderItem`ni yaratish
#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 quantity=quantity,
#                 price=product.price * quantity  # Mahsulot narxini qo'shish
#             )
#
#         # Buyurtmaning umumiy narxini hisoblash
#         total_price = sum(item['quantity'] * Product.objects.get(id=item['product']).price for item in items_data)
#         order.total_price = total_price
#         order.save()
#
#         return order


# class CartItemSerializer(serializers.ModelSerializer):
#     total_price = serializers.ReadOnlyField()
#     class Meta:
#         model = CartItem
#         fields = ['id', 'product', 'quantity', 'total_price']

# class CartSerializer(serializers.ModelSerializer):
#     cart_items = CartItemSerializer(many=True, read_only=True)
#     total_price = serializers.ReadOnlyField()
#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())
#
#     class Meta:
#         model = Cart
#         fields = ['id', 'user', 'cart_items', 'total_price']
#
# class OrderItemSerializer(serializers.ModelSerializer):
#     total_price = serializers.ReadOnlyField()
#     class Meta:
#         model = OrderItem
#         fields = ['id', 'product', 'quantity', 'price', 'total_price']
#
# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True, read_only=True)
#     total_items = serializers.ReadOnlyField()
#
#     class Meta:
#         model = Orders
#         fields = ['id', 'user', 'order_items', 'total_price', 'status', 'created_at', 'total_items']