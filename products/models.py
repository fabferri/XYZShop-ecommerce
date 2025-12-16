from django.db import models
from django.urls import reverse
from django.conf import settings

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:product_list_by_category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='products/', blank=True)
    description = models.TextField(blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text='Cost price paid for this item')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Selling price to customers')
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False, help_text='Product is visible to customers on the website')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.id, self.slug])
    
    def get_margin_percentage(self):
        """Calculate profit margin percentage"""
        if self.cost_price > 0:
            margin = ((self.price - self.cost_price) / self.cost_price) * 100
            return round(margin, 2)
        return 0.00
    
    def get_profit(self):
        """Calculate profit amount"""
        return self.price - self.cost_price
    
    def get_average_rating(self):
        """Calculate average rating from all reviews"""
        reviews = self.reviews.all()
        if reviews.exists():
            total = sum(review.rating for review in reviews)
            return round(total / reviews.count(), 1)
        return 0.0
    
    def get_rating_count(self):
        """Get total number of ratings"""
        return self.reviews.count()
    
    def get_rating_distribution(self):
        """Get distribution of ratings (5 stars to 1 star)"""
        distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for review in self.reviews.all():
            distribution[review.rating] += 1
        return distribution


class ProductReview(models.Model):
    """
    Customer reviews and ratings for products
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.PositiveSmallIntegerField(
        choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')],
        help_text='Rate this product from 1 to 5 stars'
    )
    title = models.CharField(max_length=200, blank=True, help_text='Short title for your review')
    comment = models.TextField(help_text='Your review of this product')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    verified_purchase = models.BooleanField(default=False, help_text='Customer has purchased this product')
    
    class Meta:
        ordering = ('-created',)
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'
        # Ensure a user can only review a product once
        unique_together = ('product', 'user')
        indexes = [
            models.Index(fields=['product', '-created']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating} stars)"
    
    def get_star_display(self):
        """Return star rating as visual representation"""
        return '★' * self.rating + '☆' * (5 - self.rating)


class Sale(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='sales', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    sold_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ('-date',)
        verbose_name = 'sale'
        verbose_name_plural = 'sales'
    
    def __str__(self):
        return f"{self.item.name} x{self.quantity} - £{self.sold_price} ({self.date.strftime('%Y-%m-%d')})"
    
    def get_total_amount(self):
        """Calculate total amount for this sale"""
        return self.sold_price * self.quantity


class ProductPriceHistory(models.Model):
    """
    Track price changes for products over time
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Cost price at this point in time')
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Selling price at this point in time')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text='User who made the price change')
    changed_at = models.DateTimeField(auto_now_add=True, help_text='When the price was changed')
    reason = models.TextField(blank=True, help_text='Optional reason for the price change')
    
    class Meta:
        ordering = ('-changed_at',)
        verbose_name = 'Product Price History'
        verbose_name_plural = 'Product Price Histories'
        indexes = [
            models.Index(fields=['product', '-changed_at']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - £{self.selling_price} (Cost: £{self.cost_price}) - {self.changed_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_margin_percentage(self):
        """Calculate profit margin percentage at this point in time"""
        if self.cost_price > 0:
            margin = ((self.selling_price - self.cost_price) / self.cost_price) * 100
            return round(margin, 2)
        return 0.00
    
    def get_profit(self):
        """Calculate profit amount at this point in time"""
        return self.selling_price - self.cost_price
