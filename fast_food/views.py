from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import Product, CartItem, Orders, OrderItem
from .serializers import (
    ProductSerializer, OrderSerializer, RegisterSerializer, CartItemSerializer
)
from .permissions import IsAdminOrReadOnly, IsCustomerOrAdmin

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Foydalanuvchining savatini ko‘rish"""
        cart_items = CartItem.objects.filter(user=request.user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Mahsulotni savatga qo‘shish yoki yangilash"""
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = CartItemSerializer(data=data)

        if serializer.is_valid():
            # Agar savatda mahsulot bo‘lsa, miqdorini oshirish
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product_id=serializer.validated_data['product'].id,
                defaults={'quantity': serializer.validated_data['quantity']}
            )
            if not created:
                cart_item.quantity += serializer.validated_data['quantity']
                cart_item.save()

            return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Savatdagi mahsulotni o‘chirish"""
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(user=request.user, product_id=product_id)
            cart_item.delete()
            return Response({"message": "Mahsulot savatdan o‘chirildi."}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"error": "Bunday mahsulot savatda topilmadi."}, status=status.HTTP_404_NOT_FOUND)

class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Foydalanuvchining savatdagi mahsulotlarini ko‘rish"""
        cart_items = CartItem.objects.filter(user=request.user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Total price calculation
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        # Addressni request-dan olish
        address = request.data.get('address')
        if not address:
            return Response({"error": "Address field is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Buyurtmani yaratish (avval orderni bazaga saqlaymiz)
        order = Orders.objects.create(
            user=user,
            total_price=total_price,
            address=address
        )

        # Savatdagi mahsulotlar asosida OrderItem yaratish
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price * cart_item.quantity  # Mahsulot narxi * miqdor
            )

        # Savatni bo‘shatish
        cart_items.delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class OrderViewSet(ModelViewSet):
    """
    - Mijozlar faqat oʻz buyurtmalarini koʻra oladi.
    - Admin esa barcha buyurtmalarni koʻrishi va order statusini oʻzgartirishi mumkin.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsCustomerOrAdmin]

    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return Orders.objects.all()
        return Orders.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Faqat admin buyurtma statusini o'zgartira oladi
        if self.request.user.role == 'ADMIN':
            serializer.save()
        else:
            raise PermissionError("Only admins can change order status")
