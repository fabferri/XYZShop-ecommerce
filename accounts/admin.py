from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from orders.models import Order

# Register your models here.

class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    readonly_fields = ['created', 'get_total_cost', 'paid']
    fields = ['id', 'created', 'first_name', 'last_name', 'city', 'get_total_cost', 'paid']
    can_delete = False
    max_num = 0  # Don't allow adding orders from user admin
    
    def get_total_cost(self, obj):
        return f"£{obj.get_total_cost()}"
    get_total_cost.short_description = 'Total Cost'


class CustomUserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 
                    'date_joined', 'get_order_count', 'get_total_spent']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    list_per_page = 25
    
    inlines = [OrderInline]
    
    def get_order_count(self, obj):
        count = obj.orders.count()
        return count
    get_order_count.short_description = 'Total Orders'
    
    def get_total_spent(self, obj):
        total = sum(order.get_total_cost() for order in obj.orders.all())
        return f"£{total:.2f}"
    get_total_spent.short_description = 'Total Spent'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
