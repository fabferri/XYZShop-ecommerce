from django.core.management.base import BaseCommand
from products.models import Product, ProductPriceHistory


class Command(BaseCommand):
    help = 'Create initial price history records for all existing products'

    def handle(self, *args, **options):
        products = Product.objects.all()
        created_count = 0
        
        self.stdout.write('Creating price history records for existing products...')
        
        for product in products:
            # Check if product already has price history
            if not product.price_history.exists():
                ProductPriceHistory.objects.create(
                    product=product,
                    cost_price=product.cost_price,
                    selling_price=product.price,
                    reason='Initial price record (migrated from existing data)'
                )
                created_count += 1
                self.stdout.write(f'  ✓ Created price history for: {product.name}')
            else:
                self.stdout.write(f'  - Skipped {product.name} (already has price history)')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_count} price history record(s)'
            )
        )
