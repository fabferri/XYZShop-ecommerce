from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from products.models import Sale


@receiver(post_save, sender=Order)
def create_sales_from_order(sender, instance, created, **kwargs):
    """
    Automatically create Sale records when an order is marked as paid
    """
    if instance.paid and not created:
        # Check if sales already exist for this order to avoid duplicates
        existing_sales = Sale.objects.filter(order=instance).exists()
        
        if not existing_sales:
            # Create a Sale record for each item in the order
            for item in instance.items.all():
                Sale.objects.create(
                    order=instance,
                    category=item.product.category,
                    item=item.product,
                    sold_price=item.price,
                    quantity=item.quantity
                )
