from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Product, ProductPriceHistory


@receiver(pre_save, sender=Product)
def track_price_change(sender, instance, **kwargs):
    """
    Track price changes before saving the product.
    Only creates a history record if the price or cost_price has changed.
    """
    if instance.pk:  # Only for existing products (not new ones)
        try:
            old_product = Product.objects.get(pk=instance.pk)
            # Check if price or cost_price has changed
            if old_product.price != instance.price or old_product.cost_price != instance.cost_price:
                # Store the change in a temporary attribute to be saved in post_save
                instance._price_changed = True
                instance._old_price = old_product.price
                instance._old_cost_price = old_product.cost_price
        except Product.DoesNotExist:
            pass


@receiver(post_save, sender=Product)
def save_price_history(sender, instance, created, **kwargs):
    """
    Save price history after the product is saved.
    Creates a history record for new products or when prices change.
    """
    # For new products, create initial price history
    if created:
        ProductPriceHistory.objects.create(
            product=instance,
            cost_price=instance.cost_price,
            selling_price=instance.price,
            reason="Initial price set"
        )
    # For existing products, create history only if price changed
    elif hasattr(instance, '_price_changed') and instance._price_changed:
        ProductPriceHistory.objects.create(
            product=instance,
            cost_price=instance.cost_price,
            selling_price=instance.price,
            reason="Price updated"
        )
        # Clean up temporary attributes
        delattr(instance, '_price_changed')
        delattr(instance, '_old_price')
        delattr(instance, '_old_cost_price')
