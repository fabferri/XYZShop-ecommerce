"""
API URL Configuration
Routes for all REST API endpoints under /api/: categories, products,
reviews, cart, orders, and authentication.
"""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Products
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<int:id>/', views.ProductDetailView.as_view(), name='product-detail'),

    # Reviews
    path('products/<int:product_id>/reviews/', views.ProductReviewListView.as_view(), name='product-review-list'),
    path('products/<int:product_id>/reviews/create/', views.ProductReviewCreateView.as_view(), name='product-review-create'),

    # Cart
    path('cart/', views.cart_detail, name='cart-detail'),
    path('cart/add/', views.cart_add, name='cart-add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart-remove'),
    path('cart/clear/', views.cart_clear, name='cart-clear'),

    # Orders
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<int:id>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),

    # Auth
    path('auth/register/', views.register, name='auth-register'),
    path('auth/login/', views.login, name='auth-login'),
    path('auth/profile/', views.profile, name='auth-profile'),
]
