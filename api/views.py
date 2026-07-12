"""
API Views
DRF views for categories, products, reviews, session-based cart,
orders, and token authentication (register, login, profile).
"""
from decimal import Decimal

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, F, Q
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from products.models import Category, Product, ProductReview
from orders.models import Order, OrderItem
from cart.cart import Cart

from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ReviewSerializer,
    CartSerializer,
    CartItemSerializer,
    CartAddSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
)


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.annotate(
            product_count=Count(
                'products',
                filter=Q(products__available=True, products__is_online=True),
            )
        ).order_by('name')


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category__slug', 'available']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created']
    ordering = ['name']

    def get_queryset(self):
        return Product.objects.filter(
            available=True, is_online=True
        ).select_related('category')


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Product.objects.filter(
            available=True, is_online=True
        ).select_related('category').prefetch_related('reviews__user')


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

class ProductReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return ProductReview.objects.filter(
            product_id=self.kwargs['product_id']
        ).select_related('user')


class ProductReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        product = generics.get_object_or_404(
            Product, id=self.kwargs['product_id'],
            available=True, is_online=True,
        )
        if ProductReview.objects.filter(product=product, user=self.request.user).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'You have already reviewed this product.'})
        serializer.save(user=self.request.user, product=product)


# ---------------------------------------------------------------------------
# Cart  (session-based, function views)
# ---------------------------------------------------------------------------

@api_view(['GET'])
def cart_detail(request):
    cart = Cart(request)
    items = []
    for item in cart:
        items.append({
            'product_id': item['product'].id,
            'product_name': item['product'].name,
            'price': item['price'],
            'quantity': item['quantity'],
            'total_price': item['total_price'],
        })
    data = {
        'items': items,
        'total_items': len(cart),
        'total_price': cart.get_total_price(),
    }
    return Response(CartSerializer(data).data)


@api_view(['POST'])
def cart_add(request):
    serializer = CartAddSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    product_id = serializer.validated_data['product_id']
    quantity = serializer.validated_data['quantity']
    update = serializer.validated_data['update_quantity']
    try:
        product = Product.objects.get(
            id=product_id, available=True, is_online=True
        )
    except Product.DoesNotExist:
        return Response(
            {'detail': 'Product not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )
    cart = Cart(request)
    cart.add(product=product, quantity=quantity, update_quantity=update)
    return Response({'detail': 'Product added to cart.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def cart_remove(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {'detail': 'Product not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )
    cart = Cart(request)
    cart.remove(product)
    return Response({'detail': 'Product removed from cart.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return Response({'detail': 'Cart cleared.'}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

class _InsufficientStock(Exception):
    """Raised when a cart item's quantity exceeds available product stock."""

    def __init__(self, product_name):
        self.product_name = product_name
        super().__init__(product_name)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items__product')


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart = Cart(request)
        if len(cart) == 0:
            return Response(
                {'detail': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                # Lock the product rows to prevent overselling under concurrency.
                product_ids = [item['product'].id for item in cart]
                locked = {
                    p.id: p for p in
                    Product.objects.select_for_update().filter(id__in=product_ids)
                }
                # Validate stock before creating the order.
                for item in cart:
                    product = locked.get(item['product'].id)
                    if product is None or product.stock < item['quantity']:
                        raise _InsufficientStock(item['product'].name)

                order = serializer.save(user=request.user)
                for item in cart:
                    product = locked[item['product'].id]
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=item['price'],
                        quantity=item['quantity'],
                    )
                    # Atomic decrement at the database level.
                    Product.objects.filter(id=product.id).update(
                        stock=F('stock') - item['quantity']
                    )
        except _InsufficientStock as exc:
            return Response(
                {'detail': f'Insufficient stock for "{exc.product_name}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart.clear()
        return Response(
            OrderDetailSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@api_view(['POST'])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {'token': token.key, 'user': UserProfileSerializer(user).data},
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response(
            {'detail': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {'detail': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user': UserProfileSerializer(user).data})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    return Response(UserProfileSerializer(request.user).data)
