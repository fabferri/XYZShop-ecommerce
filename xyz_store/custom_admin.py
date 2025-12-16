from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html

class CustomAdminSite(AdminSite):
    site_header = 'XYZShop Administration'
    site_title = 'XYZShop Admin'
    index_title = 'Store Management Dashboard'
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Import models here to avoid circular imports
        from products.models import Product, Category
        from orders.models import Order, OrderItem
        from django.contrib.auth.models import User
        from decimal import Decimal
        
        # Gather statistics
        stats = {
            'total_products': Product.objects.count(),
            'available_products': Product.objects.filter(available=True).count(),
            'out_of_stock': Product.objects.filter(stock=0).count(),
            'low_stock': Product.objects.filter(stock__lte=10, stock__gt=0).count(),
            'total_categories': Category.objects.count(),
            'total_users': User.objects.count(),
            'registered_customers': User.objects.filter(is_staff=False).count(),
            'total_orders': Order.objects.count(),
            'paid_orders': Order.objects.filter(paid=True).count(),
            'pending_orders': Order.objects.filter(paid=False).count(),
            'total_revenue': sum(order.get_total_cost() for order in Order.objects.filter(paid=True)),
            'total_items_sold': sum(item.quantity for item in OrderItem.objects.filter(order__paid=True)),
        }
        
        extra_context['statistics'] = stats
        
        return super().index(request, extra_context=extra_context)

# Create an instance of the custom admin site
admin_site = CustomAdminSite(name='custom_admin')
