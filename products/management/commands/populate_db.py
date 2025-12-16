from django.core.management.base import BaseCommand
from products.models import Category, Product


class Command(BaseCommand):
    help = 'Populates the database with sample products'

    def handle(self, *args, **kwargs):
        # Create categories
        categories_data = [
            {'name': 'Power Tools', 'slug': 'power-tools'},
            {'name': 'Hand Tools', 'slug': 'hand-tools'},
            {'name': 'Screws & Fixings', 'slug': 'screws-fixings'},
            {'name': 'Paint & Decorating', 'slug': 'paint-decorating'},
            {'name': 'Electrical', 'slug': 'electrical'},
            {'name': 'Plumbing', 'slug': 'plumbing'},
        ]

        self.stdout.write('Creating categories...')
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(**cat_data)
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Create products
        products_data = [
            {
                'category': categories['power-tools'],
                'name': 'Cordless Drill Driver 18V',
                'slug': 'cordless-drill-driver-18v',
                'description': 'Powerful 18V cordless drill with 2-speed gearbox and 13mm keyless chuck. Perfect for drilling and driving applications.',
                'price': '89.99',
                'stock': 25,
            },
            {
                'category': categories['power-tools'],
                'name': 'Circular Saw 185mm',
                'slug': 'circular-saw-185mm',
                'description': '1400W circular saw with 185mm blade. Ideal for cutting wood, MDF, and plywood.',
                'price': '69.99',
                'stock': 15,
            },
            {
                'category': categories['power-tools'],
                'name': 'Angle Grinder 115mm',
                'slug': 'angle-grinder-115mm',
                'description': 'Compact and powerful 115mm angle grinder, 750W motor. Perfect for cutting and grinding metal.',
                'price': '45.99',
                'stock': 30,
            },
            {
                'category': categories['hand-tools'],
                'name': 'Claw Hammer 16oz',
                'slug': 'claw-hammer-16oz',
                'description': 'Professional quality claw hammer with fibreglass handle and anti-vibration grip.',
                'price': '12.99',
                'stock': 50,
            },
            {
                'category': categories['hand-tools'],
                'name': 'Screwdriver Set 8 Piece',
                'slug': 'screwdriver-set-8-piece',
                'description': '8-piece screwdriver set including slotted and Phillips head drivers. Chrome vanadium steel.',
                'price': '18.99',
                'stock': 40,
            },
            {
                'category': categories['hand-tools'],
                'name': 'Spirit Level 600mm',
                'slug': 'spirit-level-600mm',
                'description': 'Heavy-duty 600mm spirit level with 3 vials. Milled base for accuracy.',
                'price': '15.99',
                'stock': 35,
            },
            {
                'category': categories['screws-fixings'],
                'name': 'Woodscrews Pozi 4x40mm 200pk',
                'slug': 'woodscrews-pozi-4x40mm',
                'description': 'Pack of 200 zinc-plated woodscrews, Pozi head, 4mm x 40mm.',
                'price': '5.99',
                'stock': 100,
            },
            {
                'category': categories['screws-fixings'],
                'name': 'Wall Plugs Assorted 150pk',
                'slug': 'wall-plugs-assorted',
                'description': 'Assorted wall plugs pack of 150. Various sizes for different applications.',
                'price': '7.99',
                'stock': 80,
            },
            {
                'category': categories['paint-decorating'],
                'name': 'Emulsion Paint White 10L',
                'slug': 'emulsion-paint-white-10l',
                'description': 'Matt emulsion paint, brilliant white finish. 10 litre coverage approximately 65m².',
                'price': '29.99',
                'stock': 20,
            },
            {
                'category': categories['paint-decorating'],
                'name': 'Paint Roller Set',
                'slug': 'paint-roller-set',
                'description': 'Complete paint roller set including frame, 2 sleeves and tray.',
                'price': '8.99',
                'stock': 45,
            },
            {
                'category': categories['electrical'],
                'name': '13A Socket Twin 2 Gang White',
                'slug': 'socket-twin-2-gang-white',
                'description': 'Twin 13A socket outlet, 2 gang, white finish. Includes mounting box.',
                'price': '6.99',
                'stock': 60,
            },
            {
                'category': categories['electrical'],
                'name': 'LED Bulb GU10 5W Pack of 5',
                'slug': 'led-bulb-gu10-5w',
                'description': 'Energy saving LED bulbs, GU10 fitting, 5W, warm white. Pack of 5.',
                'price': '12.99',
                'stock': 70,
            },
            {
                'category': categories['plumbing'],
                'name': 'Tap Connector 15mm x 3/4"',
                'slug': 'tap-connector-15mm',
                'description': 'Chrome-plated tap connector, 15mm x 3/4" BSP thread.',
                'price': '4.99',
                'stock': 55,
            },
            {
                'category': categories['plumbing'],
                'name': 'Basin Waste & Plug Chrome',
                'slug': 'basin-waste-plug-chrome',
                'description': 'Slotted basin waste with plug, chrome plated brass construction.',
                'price': '9.99',
                'stock': 30,
            },
        ]

        self.stdout.write('Creating products...')
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults=prod_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
