from rest_framework.viewsets import ModelViewSet
from .models import Product, Cart, Orders
from .serializers import ProductSerializer, CartSerializer, OrderSerializer, RegisterSerializer
from .permissions import IsAdminOrReadOnly, IsCustomerOrAdmin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

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


class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsCustomerOrAdmin]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsCustomerOrAdmin]

    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return Orders.objects.all()
        return Orders.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if self.request.user.role == 'ADMIN':
            serializer.save()
        else:
            raise PermissionError("Only admins can change order status")