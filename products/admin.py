from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Sale, ProductPriceHistory, ProductReview

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/products/category/change_list.html'
    list_display = ['name', 'slug', 'product_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Number of Products'
    
    def changelist_view(self, request, extra_context=None):
        """Add total product count to the context"""
        extra_context = extra_context or {}
        extra_context['total_products'] = Product.objects.count()
        return super().changelist_view(request, extra_context=extra_context)


class ProductPriceHistoryInline(admin.TabularInline):
    """Inline admin for displaying price history within product admin"""
    model = ProductPriceHistory
    extra = 0
    readonly_fields = ['cost_price', 'selling_price', 'changed_by', 'changed_at', 'reason', 'margin_display']
    can_delete = False
    ordering = ['-changed_at']
    
    def margin_display(self, obj):
        """Display margin percentage"""
        margin = obj.get_margin_percentage()
        if margin > 50:
            color = '#28a745'  # Green
        elif margin > 25:
            color = '#ffc107'  # Amber
        elif margin > 0:
            color = '#fd7e14'  # Orange
        else:
            color = '#dc3545'  # Red
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, f'{margin:.1f}'
        )
    margin_display.short_description = 'Margin %'
    
    def has_add_permission(self, request, obj=None):
        """Prevent manual addition of price history records"""
        return False


class ProductReviewInline(admin.TabularInline):
    """Inline admin for displaying product reviews within product admin"""
    model = ProductReview
    extra = 0
    readonly_fields = ['user', 'rating', 'star_display', 'title', 'comment', 'created', 'verified_purchase']
    can_delete = True
    ordering = ['-created']
    
    def star_display(self, obj):
        """Display star rating visually"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        color = '#ffa500' if obj.rating >= 4 else '#ff6347' if obj.rating <= 2 else '#ffd700'
        return format_html(
            '<span style="color: {}; font-size: 1.2em;">{}</span>',
            color, stars
        )
    star_display.short_description = 'Rating'
    
    def has_add_permission(self, request, obj=None):
        """Reviews should be added by customers, not admin"""
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    change_list_template = 'admin/products/product/change_list.html'
    list_display = ['image_preview', 'name', 'category', 'cost_price', 'price', 'profit_display', 'margin_display', 'rating_display', 'stock', 'available', 'is_online', 'created']
    list_filter = ['is_online', 'available', 'created', 'updated', 'category']
    list_editable = ['name', 'category', 'cost_price', 'price', 'stock']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_per_page = 20
    date_hierarchy = 'created'
    ordering = ['-created']
    actions = ['make_online', 'make_warehouse']
    inlines = [ProductPriceHistoryInline, ProductReviewInline]
    
    class Media:
        css = {
            'all': ('admin/css/product_admin.css',)
        }
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('cost_price', 'price', 'stock', 'available'),
            'description': 'Cost price is what you paid, Price is what customers pay'
        }),
        ('Warehouse & Online Status', {
            'fields': ('is_online',),
            'description': 'Control whether this product is visible to customers online or stored in warehouse'
        }),
        ('Image', {
            'fields': ('image',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return format_html('<span style="color: #999;">No Image</span>')
    image_preview.short_description = 'Image'
    
    def selling_price_display(self, obj):
        """Display selling price"""
        return f'£{obj.price:.2f}'
    selling_price_display.short_description = 'Selling Price'
    selling_price_display.admin_order_field = 'price'
    
    def profit_display(self, obj):
        """Display profit amount"""
        profit = obj.get_profit()
        color = 'green' if profit > 0 else 'red' if profit < 0 else 'gray'
        profit_formatted = f'£{profit:.2f}'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, profit_formatted
        )
    profit_display.short_description = 'Profit'
    profit_display.admin_order_field = 'price'
    
    def margin_display(self, obj):
        """Display margin percentage"""
        margin = obj.get_margin_percentage()
        if margin > 50:
            color = '#28a745'  # Green
        elif margin > 25:
            color = '#ffc107'  # Amber
        elif margin > 0:
            color = '#fd7e14'  # Orange
        else:
            color = '#dc3545'  # Red
        
        margin_formatted = f'{margin:.1f}%'
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 1.1em;">{}</span>',
            color, margin_formatted
        )
    margin_display.short_description = 'Margin %'
    margin_display.admin_order_field = 'price'
    
    def rating_display(self, obj):
        """Display average rating with stars"""
        avg_rating = obj.get_average_rating()
        count = obj.get_rating_count()
        
        if count == 0:
            return format_html('<span style="color: #999;">No reviews</span>')
        
        # Calculate full stars and half star
        full_stars = int(avg_rating)
        has_half = (avg_rating - full_stars) >= 0.5
        empty_stars = 5 - full_stars - (1 if has_half else 0)
        
        stars = '★' * full_stars
        if has_half:
            stars += '⯨'
        stars += '☆' * empty_stars
        
        color = '#ffa500' if avg_rating >= 4 else '#ff6347' if avg_rating <= 2 else '#ffd700'
        
        return format_html(
            '<span style="color: {}; font-size: 1.1em;">{}</span> <span style="color: #666;">({} / 5 - {} reviews)</span>',
            color, stars, f'{avg_rating:.1f}', count
        )
    rating_display.short_description = 'Rating'
    
    def make_online(self, request, queryset):
        """Move selected products from warehouse to online store"""
        updated = queryset.update(is_online=True)
        self.message_user(request, f'{updated} product(s) successfully moved to online store.')
    make_online.short_description = '✓ Move selected products ONLINE (visible to customers)'
    
    def make_warehouse(self, request, queryset):
        """Move selected products from online store to warehouse"""
        updated = queryset.update(is_online=False)
        self.message_user(request, f'{updated} product(s) successfully moved to warehouse (hidden from customers).')
    make_warehouse.short_description = '📦 Move selected products to WAREHOUSE (not visible)'
    
    def save_model(self, request, obj, form, change):
        """Custom save to add any additional logic"""
        super().save_model(request, obj, form, change)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['date', 'order', 'category', 'item', 'quantity', 'sold_price_display', 'total_amount_display']
    list_filter = ['date', 'category']
    search_fields = ['item__name', 'order__id']
    date_hierarchy = 'date'
    ordering = ['-date']
    readonly_fields = ['date', 'order']
    
    def sold_price_display(self, obj):
        """Display sold price"""
        return f'£{obj.sold_price:.2f}'
    sold_price_display.short_description = 'Unit Price'
    sold_price_display.admin_order_field = 'sold_price'
    
    def total_amount_display(self, obj):
        """Display total amount"""
        return f'£{obj.get_total_amount():.2f}'
    total_amount_display.short_description = 'Total Amount'
    
    def changelist_view(self, request, extra_context=None):
        """Add sales statistics to the changelist view"""
        from django.db.models import Sum, Count
        from django.utils import timezone
        from datetime import timedelta
        
        extra_context = extra_context or {}
        
        # Get current date
        now = timezone.now()
        today = now.date()
        
        # Calculate date ranges
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        year_ago = now - timedelta(days=365)
        
        # Today's sales
        today_sales = Sale.objects.filter(date__date=today).aggregate(
            total=Sum('sold_price'),
            count=Count('id')
        )
        
        # This week's sales
        week_sales = Sale.objects.filter(date__gte=week_ago).aggregate(
            total=Sum('sold_price'),
            count=Count('id')
        )
        
        # This month's sales
        month_sales = Sale.objects.filter(date__gte=month_ago).aggregate(
            total=Sum('sold_price'),
            count=Count('id')
        )
        
        # This year's sales
        year_sales = Sale.objects.filter(date__gte=year_ago).aggregate(
            total=Sum('sold_price'),
            count=Count('id')
        )
        
        extra_context['today_sales'] = today_sales['total'] or 0
        extra_context['today_count'] = today_sales['count'] or 0
        extra_context['week_sales'] = week_sales['total'] or 0
        extra_context['week_count'] = week_sales['count'] or 0
        extra_context['month_sales'] = month_sales['total'] or 0
        extra_context['month_count'] = month_sales['count'] or 0
        extra_context['year_sales'] = year_sales['total'] or 0
        extra_context['year_count'] = year_sales['count'] or 0
        
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ProductPriceHistory)
class ProductPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'cost_price', 'selling_price', 'margin_display', 'profit_display', 'changed_by', 'changed_at', 'reason']
    list_filter = ['changed_at', 'product__category']
    search_fields = ['product__name', 'reason', 'changed_by__username']
    date_hierarchy = 'changed_at'
    ordering = ['-changed_at']
    readonly_fields = ['product', 'cost_price', 'selling_price', 'changed_by', 'changed_at', 'reason', 'margin_display', 'profit_display']
    
    def has_add_permission(self, request):
        """Prevent manual addition - price history is auto-created via signals"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion for data cleanup if needed"""
        return True
    
    def margin_display(self, obj):
        """Display margin percentage"""
        margin = obj.get_margin_percentage()
        if margin > 50:
            color = '#28a745'  # Green
        elif margin > 25:
            color = '#ffc107'  # Amber
        elif margin > 0:
            color = '#fd7e14'  # Orange
        else:
            color = '#dc3545'  # Red
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, f'{margin:.1f}'
        )
    margin_display.short_description = 'Margin %'
    
    def profit_display(self, obj):
        """Display profit amount"""
        profit = obj.get_profit()
        color = 'green' if profit > 0 else 'red' if profit < 0 else 'gray'
        return format_html(
            '<span style="color: {}; font-weight: bold;">£{}</span>',
            color, f'{profit:.2f}'
        )
    profit_display.short_description = 'Profit'


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product_link', 'user', 'star_display', 'title_display', 'verified_purchase', 'created']
    list_filter = ['rating', 'verified_purchase', 'created']
    search_fields = ['product__name', 'user__username', 'title', 'comment']
    date_hierarchy = 'created'
    ordering = ['-created']
    readonly_fields = ['product', 'user', 'star_display', 'created', 'updated']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'user', 'star_display', 'rating', 'verified_purchase')
        }),
        ('Review Content', {
            'fields': ('title', 'comment')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Reviews should be added by customers through the website"""
        return False
    
    def product_link(self, obj):
        """Display product name as clickable link to product admin page"""
        from django.urls import reverse
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    product_link.admin_order_field = 'product'
    
    def star_display(self, obj):
        """Display star rating visually"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        color = '#ffa500' if obj.rating >= 4 else '#ff6347' if obj.rating <= 2 else '#ffd700'
        return format_html(
            '<span style="color: {}; font-size: 1.5em; font-weight: bold;">{} ({})</span>',
            color, stars, obj.rating
        )
    star_display.short_description = 'Rating'
    
    def title_display(self, obj):
        """Display review title with truncation"""
        if obj.title:
            return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
        return '(No title)'
    title_display.short_description = 'Review Title'
