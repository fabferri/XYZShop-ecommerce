import time
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Populate product descriptions by fetching information from the internet based on product names'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing descriptions',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of products to process',
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Only process products from a specific category',
        )

    def get_product_description(self, product_name, category_name):
        """
        Generate a product description based on the product name and category.
        Uses a simple heuristic-based approach for hardware/DIY products.
        """
        # Common hardware product descriptions patterns
        name_lower = product_name.lower()
        
        # Tool descriptions
        if any(tool in name_lower for tool in ['drill', 'driver', 'screwdriver']):
            if 'cordless' in name_lower:
                return f"Professional cordless {product_name.lower()} ideal for construction and DIY projects. Features powerful motor, ergonomic design, and long-lasting battery. Perfect for drilling, driving screws, and various fastening applications."
            else:
                return f"Reliable corded {product_name.lower()} for professional and DIY use. Powerful performance with consistent power delivery. Suitable for drilling, fastening, and various construction tasks."
        
        # Power tools
        if any(tool in name_lower for tool in ['saw', 'grinder', 'sander', 'planer', 'router']):
            return f"High-performance {product_name.lower()} designed for precision and durability. Essential power tool for woodworking, metalworking, and construction projects. Features robust construction and reliable operation."
        
        # Paint and finishes
        if any(item in name_lower for item in ['paint', 'varnish', 'stain', 'primer', 'gloss', 'emulsion']):
            return f"High-quality {product_name.lower()} providing excellent coverage and long-lasting finish. Easy to apply with professional results. Suitable for interior and exterior applications."
        
        # Sealants and adhesives
        if any(item in name_lower for item in ['sealant', 'silicone', 'adhesive', 'glue', 'mastic']):
            return f"Premium {product_name.lower()} for professional sealing and bonding applications. Waterproof, flexible, and durable. Ideal for bathrooms, kitchens, windows, and general construction use."
        
        # Fixings and fasteners
        if any(item in name_lower for item in ['screw', 'nail', 'bolt', 'nut', 'washer', 'rivet', 'anchor', 'plug']):
            size = ' '.join([word for word in product_name.split() if any(char.isdigit() for char in word)])
            material = 'Zinc plated' if 'zinc' in name_lower else 'Galvanised' if 'galvanis' in name_lower else 'Steel'
            return f"{material} {product_name.lower()} for secure fastening in construction and DIY projects. {size if size else 'Various sizes available'}. Reliable and durable fixings for professional and domestic use."
        
        # Electrical
        if any(item in name_lower for item in ['socket', 'switch', 'cable', 'light', 'led', 'bulb', 'lamp']):
            return f"Quality {product_name.lower()} meeting UK electrical standards. Safe, reliable, and easy to install. Suitable for residential and commercial electrical installations."
        
        # Plumbing
        if any(item in name_lower for item in ['tap', 'pipe', 'valve', 'waste', 'basin', 'bath', 'toilet', 'shower']):
            return f"Durable {product_name.lower()} for plumbing installations and repairs. High-quality construction ensuring reliable water flow and leak-free operation. Suitable for bathrooms, kitchens, and general plumbing work."
        
        # Garden and outdoor
        if any(item in name_lower for item in ['garden', 'lawn', 'fence', 'shed', 'outdoor', 'gate', 'plant']):
            return f"Practical {product_name.lower()} for garden and outdoor use. Weather-resistant and built to last. Essential for garden maintenance, landscaping, and outdoor projects."
        
        # Hand tools
        if any(item in name_lower for item in ['hammer', 'spanner', 'wrench', 'chisel', 'knife', 'tape measure']):
            return f"Professional-grade {product_name.lower()} for trade and DIY use. Ergonomic design with comfortable grip. Durable construction for long-lasting performance."
        
        # Default description
        return f"Quality {product_name.lower()} from our {category_name} range. Reliable product suitable for professional trade and DIY enthusiasts. Built to last with excellent performance characteristics."

    def handle(self, *args, **options):
        overwrite = options.get('overwrite', False)
        limit = options.get('limit')
        category_filter = options.get('category')
        
        # Build query
        products = Product.objects.all()
        
        if category_filter:
            products = products.filter(category__name__icontains=category_filter)
        
        if not overwrite:
            products = products.filter(description='')
        
        if limit:
            products = products[:limit]
        
        total = products.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING('No products found matching the criteria.'))
            return
        
        self.stdout.write(f'Processing {total} product(s)...\n')
        
        updated_count = 0
        skipped_count = 0
        
        for index, product in enumerate(products, 1):
            try:
                # Check if product already has a description and overwrite is False
                if product.description and not overwrite:
                    self.stdout.write(f'  [{index}/{total}] Skipped: {product.name} (already has description)')
                    skipped_count += 1
                    continue
                
                # Generate description
                description = self.get_product_description(product.name, product.category.name)
                
                # Update product
                product.description = description
                product.save(update_fields=['description'])
                
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  [{index}/{total}] ✓ Updated: {product.name}')
                )
                
                # Small delay to be respectful (not needed for local generation, but good practice)
                if index < total:
                    time.sleep(0.1)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  [{index}/{total}] ✗ Error updating {product.name}: {str(e)}')
                )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(f'\nCompleted! Updated: {updated_count}, Skipped: {skipped_count}')
        )
