from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ['get_cost']
    fields = ['product', 'price', 'quantity', 'get_cost']
    
    def get_cost(self, obj):
        return f"£{obj.get_cost()}"
    get_cost.short_description = 'Total Cost'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_user_info', 'first_name', 'last_name', 'email', 
                    'city', 'get_total_cost', 'payment_method', 'status', 'paid', 'created']
    list_filter = ['paid', 'status', 'payment_method', 'created', 'updated', 'user']
    search_fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'payment_id']
    inlines = [OrderItemInline]
    readonly_fields = ['created', 'updated', 'get_total_cost', 'payment_id']
    list_per_page = 25
    date_hierarchy = 'created'
    list_editable = ['status']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'first_name', 'last_name', 'email')
        }),
        ('Delivery Address', {
            'fields': ('address', 'postal_code', 'city')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_id', 'paid', 'get_total_cost')
        }),
        ('Order Status', {
            'fields': ('status', 'created', 'updated')
        }),
    )
    
    def get_user_info(self, obj):
        if obj.user:
            return f"{obj.user.username} (Registered)"
        return "Guest"
    get_user_info.short_description = 'User Account'
    get_user_info.admin_order_field = 'user'
    
    def get_total_cost(self, obj):
        return f"£{obj.get_total_cost()}"
    get_total_cost.short_description = 'Total Cost'
    
    def get_queryset(self, request):
        """
        Administrators see all orders.
        This method ensures staff and superusers have access to all orders.
        """
        qs = super().get_queryset(request)
        # Staff and superusers can see all orders
        if request.user.is_staff or request.user.is_superuser:
            return qs
        # Regular users shouldn't access admin panel, but if they do, show nothing
        return qs.none()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'price', 'quantity', 'get_cost']
    list_filter = ['order__created', 'product__category']
    search_fields = ['product__name', 'order__email', 'order__first_name', 'order__last_name']
    raw_id_fields = ['order', 'product']
    list_per_page = 50
    
    def get_cost(self, obj):
        return f"£{obj.get_cost()}"
    get_cost.short_description = 'Total Cost'
