"""
Populate Fresh Database Script
This script adds all products to a fresh XYZShop database.
Run this after creating a new database with: python manage.py migrate
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from products.models import Product, Category
from django.utils.text import slugify

def create_categories():
    """Create all product categories"""
    categories_data = [
        ('Power Tools', 'power-tools'),
        ('Hand Tools', 'hand-tools'),
        ('Electrical', 'electrical'),
        ('Screws & Fixings', 'screws-fixings'),
        ('Paint & Decorating', 'paint-decorating'),
        ('Plumbing', 'plumbing'),
        ('Garden', 'garden'),
        ('Outdoor', 'outdoor'),
        ('Sealants', 'sealants'),
    ]
    
    print("Creating categories...")
    categories = {}
    for name, slug in categories_data:
        category, created = Category.objects.get_or_create(
            slug=slug,
            defaults={'name': name}
        )
        categories[slug] = category
        if created:
            print(f"   [+] Created: {name}")
        else:
            print(f"   [=] Exists: {name}")
    
    return categories


def add_power_tools(category):
    """Add 35 Power Tools products"""
    print("\nAdding Power Tools...")
    
    products = [
        # Cordless Drills & Drivers
        {
            'name': 'Cordless Drill Driver 18V 2.0Ah Li-Ion',
            'description': 'Powerful 18V cordless drill driver with 2-speed gearbox, LED work light, and 2.0Ah lithium-ion battery. Perfect for drilling and driving in wood, metal, and masonry. Includes charger and carry case.',
            'price': 79.99,
            'stock': 45,
        },
        {
            'name': 'Combi Drill 18V 4.0Ah Brushless',
            'description': 'High-performance brushless combi drill with hammer action for masonry. 18V system with 4.0Ah battery for extended runtime. Variable speed trigger and 24-position clutch for precise control.',
            'price': 129.99,
            'stock': 32,
        },
        {
            'name': 'Impact Driver 18V Compact Body Only',
            'description': 'Compact impact driver delivering 180Nm of torque. Body only - battery sold separately. Ideal for driving long screws and bolts. Hex chuck accepts all standard driver bits.',
            'price': 64.99,
            'stock': 38,
        },
        {
            'name': 'SDS Plus Drill 800W Corded',
            'description': 'Powerful 800W SDS plus rotary hammer drill. Three modes: drilling, hammer drilling, and chiseling. Includes depth stop, side handle, and carry case. Perfect for masonry work.',
            'price': 89.99,
            'stock': 28,
        },
        {
            'name': 'Drill Driver Set 12V with 100pc Accessories',
            'description': 'Complete 12V drill driver kit with 100-piece accessory set including drill bits, driver bits, and storage case. Compact design perfect for light-duty tasks and tight spaces.',
            'price': 54.99,
            'stock': 52,
        },
        {
            'name': 'Hammer Drill 1050W Keyed Chuck',
            'description': '1050W corded hammer drill with variable speed and reversible action. Keyed chuck accepts bits up to 13mm. Auxiliary handle and depth gauge included. Ideal for heavy-duty drilling.',
            'price': 69.99,
            'stock': 35,
        },
        {
            'name': 'Right Angle Drill 18V Body Only',
            'description': 'Compact right-angle drill for working in confined spaces. 18V system, body only. All-metal gearbox and 10mm keyless chuck. LED work light and belt clip included.',
            'price': 94.99,
            'stock': 18,
        },
        {
            'name': 'Magnetic Drill Press 1200W',
            'description': 'Industrial magnetic drill press with 1200W motor. Electromagnetic base for drilling on steel structures. Variable speed, reversible, and includes arbor and pilot pin.',
            'price': 329.99,
            'stock': 8,
        },
        
        # Saws
        {
            'name': 'Circular Saw 1400W 190mm Blade',
            'description': '1400W circular saw with 190mm blade for cutting wood, MDF, and plywood. Adjustable cutting depth up to 65mm. Laser guide for accurate cutting. Includes TCT blade.',
            'price': 74.99,
            'stock': 42,
        },
        {
            'name': 'Jigsaw 650W Variable Speed',
            'description': '650W jigsaw with variable speed control and 4-stage pendulum action. Tool-free blade change system. Cuts wood up to 80mm and steel up to 8mm. Includes dust extraction port.',
            'price': 59.99,
            'stock': 48,
        },
        {
            'name': 'Reciprocating Saw 1200W',
            'description': 'Powerful 1200W reciprocating saw for demolition and construction work. Variable speed trigger and tool-free blade change. Cuts wood, metal, and plastic. Includes 3 blades.',
            'price': 84.99,
            'stock': 36,
        },
        {
            'name': 'Mitre Saw 1800W 254mm Compound',
            'description': '1800W compound mitre saw with 254mm blade. Mitre cuts from -45° to +45° and bevel cuts up to 45°. Laser guide and LED work light. Includes TCT blade and dust bag.',
            'price': 189.99,
            'stock': 22,
        },
        {
            'name': 'Table Saw 2000W 254mm',
            'description': 'Heavy-duty 2000W table saw with 254mm blade. Large table with extension and parallel fence. Adjustable blade height and angle. Safety push stick included.',
            'price': 249.99,
            'stock': 15,
        },
        {
            'name': 'Tile Cutter Electric 800W Wet',
            'description': '800W electric wet tile cutter with 200mm diamond blade. Water cooling system for clean cuts. Adjustable fence and mitre guide. Cuts tiles up to 45mm thick.',
            'price': 159.99,
            'stock': 19,
        },
        {
            'name': 'Band Saw 350W Portable',
            'description': 'Compact 350W band saw for cutting metal and wood. Adjustable blade guide and workpiece clamp. Variable speed control. Includes blade and carry handle.',
            'price': 129.99,
            'stock': 14,
        },
        {
            'name': 'Cordless Circular Saw 18V 165mm',
            'description': '18V cordless circular saw with 165mm blade. Cutting depth 57mm at 90° and 42mm at 45°. LED work light and dust blower. Body only - battery sold separately.',
            'price': 99.99,
            'stock': 27,
        },
        
        # Sanders & Grinders
        {
            'name': 'Angle Grinder 2200W 230mm Professional',
            'description': 'Professional-grade 2200W angle grinder with 230mm disc. Anti-vibration side handle and spindle lock for easy disc changes. Includes cutting disc and grinding disc.',
            'price': 119.99,
            'stock': 31,
        },
        {
            'name': 'Orbital Sander 300W Random',
            'description': '300W random orbital sander with 125mm sanding pad. Dust extraction with micro-filter. Variable speed control. Ergonomic grip for comfortable use. Includes sanding discs.',
            'price': 49.99,
            'stock': 55,
        },
        {
            'name': 'Belt Sander 1200W 100mm Heavy Duty',
            'description': 'Heavy-duty 1200W belt sander with 100mm wide belt. Powerful motor for rapid stock removal. Dust bag included. Ideal for large flat surfaces and edge work.',
            'price': 109.99,
            'stock': 24,
        },
        {
            'name': 'Detail Sander 200W Multi-Tool',
            'description': '200W detail sander with triangular pad for corners and edges. Hook-and-loop sanding sheets. Dust extraction port. Perfect for furniture restoration and detailed work.',
            'price': 39.99,
            'stock': 46,
        },
        {
            'name': 'Bench Grinder 500W Twin Wheel',
            'description': '500W bench grinder with twin 200mm grinding wheels - one coarse, one fine. Adjustable tool rests and eye shields. Sturdy cast iron base. Ideal for sharpening and shaping.',
            'price': 89.99,
            'stock': 20,
        },
        {
            'name': 'Disc Sander 450W Benchtop',
            'description': '450W benchtop disc sander with 300mm sanding disc. Tilting table for angle work. Cast iron construction. Dust extraction port included. Great for woodworking.',
            'price': 139.99,
            'stock': 12,
        },
        {
            'name': 'Wall Sander 750W Drywall',
            'description': '750W wall sander with telescopic handle for ceilings and walls. 225mm sanding head with vacuum connection. LED work light. Perfect for drywall finishing.',
            'price': 179.99,
            'stock': 16,
        },
        
        # Planers & Routers
        {
            'name': 'Planer 900W Electric 82mm',
            'description': '900W electric planer with 82mm wide cutting blade. Adjustable cutting depth up to 3mm. Parallel fence and rebating facility. Dust extraction outlet and shavings bag.',
            'price': 79.99,
            'stock': 29,
        },
        {
            'name': 'Router 1200W Variable Speed',
            'description': '1200W plunge router with variable speed control. Soft start and constant speed under load. Includes parallel fence, template guide, and 6mm collet. Ideal for edge work.',
            'price': 94.99,
            'stock': 33,
        },
        {
            'name': 'Biscuit Jointer 900W',
            'description': '900W biscuit jointer for making strong wood joints. Adjustable fence for precise positioning. Includes 4-tooth tungsten carbide blade and dust bag. Complete with biscuits.',
            'price': 119.99,
            'stock': 18,
        },
        {
            'name': 'Laminate Trimmer 600W Compact',
            'description': 'Compact 600W laminate trimmer for edge work. Variable speed with soft start. LED work light and transparent base for clear visibility. Includes 6mm and 8mm collets.',
            'price': 69.99,
            'stock': 25,
        },
        {
            'name': 'Thickness Planer 1500W 318mm Benchtop',
            'description': '1500W benchtop thickness planer with 318mm capacity. Two-blade cutter head and adjustable depth stop. Includes dust extraction port and return rollers for smooth feeding.',
            'price': 299.99,
            'stock': 9,
        },
        {
            'name': 'Spindle Moulder 1500W',
            'description': 'Professional 1500W spindle moulder with tilting fence. Variable speed 3000-10000 RPM. Cast iron table and precision depth adjustment. Includes guards and push sticks.',
            'price': 449.99,
            'stock': 6,
        },
        
        # Nailers & Other
        {
            'name': 'Nail Gun 18V Cordless Brad',
            'description': '18V cordless brad nailer for finish work. Fires 18-gauge nails from 15-50mm. Tool-free depth adjustment. Magazine holds 100 nails. Body only - battery sold separately.',
            'price': 149.99,
            'stock': 21,
        },
        {
            'name': 'Framing Nailer Pneumatic',
            'description': 'Pneumatic framing nailer for heavy construction. Fires 50-90mm nails. Adjustable depth and contact/sequential firing modes. Includes carry case and safety glasses.',
            'price': 169.99,
            'stock': 13,
        },
        {
            'name': 'Staple Gun Electric Heavy Duty',
            'description': 'Electric heavy-duty staple gun for upholstery and carpentry. Fires staples 6-14mm and nails up to 15mm. Adjustable power and safety lock. Includes 1000 staples.',
            'price': 44.99,
            'stock': 37,
        },
        {
            'name': 'Heat Gun 2000W Two Temperature',
            'description': '2000W heat gun with two temperature settings (350°C and 550°C). Ideal for paint stripping, shrink wrapping, and thawing pipes. Includes scraper and carry case.',
            'price': 39.99,
            'stock': 42,
        },
        {
            'name': 'Multi-Tool Oscillating 300W',
            'description': '300W oscillating multi-tool with variable speed. Quick-change accessory system. Includes cutting, sanding, and scraping attachments. LED work light and carry case.',
            'price': 64.99,
            'stock': 40,
        },
    ]
    
    count = 0
    for product_data in products:
        slug = slugify(product_data['name'])
        Product.objects.create(
            category=category,
            name=product_data['name'],
            slug=slug,
            description=product_data['description'],
            price=product_data['price'],
            cost_price=product_data['price'] * 0.60,  # 40% margin
            stock=product_data['stock'],
            available=True,
            is_online=False,  # Products start in warehouse
            image=f'products/{slug}.jpg'
        )
        count += 1
    
    print(f"   [+] Added {count} Power Tools products")
    return count


def add_screws_fixings(category):
    """Add 101 Screws & Fixings products"""
    print("\nAdding Screws & Fixings...")
    
    products = [
        # Chipboard Screws
        {'name': 'Chipboard Screws Pozi 3x30mm Yellow Zinc Pack 200', 'price': 4.99, 'stock': 250},
        {'name': 'Chipboard Screws Pozi 4x40mm Yellow Zinc Pack 200', 'price': 5.99, 'stock': 220},
        {'name': 'Chipboard Screws Pozi 4x50mm Yellow Zinc Pack 100', 'price': 4.49, 'stock': 180},
        {'name': 'Chipboard Screws Countersunk 3x25mm Pack 200', 'price': 3.99, 'stock': 300},
        {'name': 'Chipboard Screws Bugle Head 4x45mm Pack 100', 'price': 5.49, 'stock': 150},
        
        # Drywall Screws
        {'name': 'Drywall Screws Coarse Thread 3.5x25mm Pack 500', 'price': 5.99, 'stock': 280},
        {'name': 'Drywall Screws Coarse Thread 3.5x32mm Pack 500', 'price': 6.49, 'stock': 260},
        {'name': 'Drywall Screws Coarse Thread 3.5x38mm Pack 500', 'price': 6.99, 'stock': 240},
        {'name': 'Drywall Screws Fine Thread 3.5x25mm Pack 500', 'price': 5.99, 'stock': 290},
        {'name': 'Drywall Screws Bugle Head 3.9x45mm Pack 200', 'price': 5.49, 'stock': 200},
        
        # Wood Screws
        {'name': 'Wood Screws Countersunk Brass 4x30mm Pack 100', 'price': 6.99, 'stock': 160},
        {'name': 'Wood Screws Countersunk Brass 6x40mm Pack 50', 'price': 5.49, 'stock': 140},
        {'name': 'Wood Screws Round Head 4x25mm Pack 100', 'price': 4.99, 'stock': 180},
        {'name': 'Wood Screws Raised Head 5x50mm Pack 50', 'price': 5.99, 'stock': 120},
        {'name': 'Wood Screws Slotted 6x50mm Steel Pack 50', 'price': 4.49, 'stock': 150},
        
        # Machine Screws
        {'name': 'Machine Screws M4x10mm Steel Pack 100', 'price': 3.99, 'stock': 350},
        {'name': 'Machine Screws M4x16mm Steel Pack 100', 'price': 4.49, 'stock': 320},
        {'name': 'Machine Screws M5x20mm Steel Pack 50', 'price': 4.99, 'stock': 280},
        {'name': 'Machine Screws M6x25mm Steel Pack 50', 'price': 5.49, 'stock': 260},
        {'name': 'Machine Screws M8x30mm Steel Pack 25', 'price': 5.99, 'stock': 200},
        
        # Masonry Screws
        {'name': 'Masonry Screws Hex Head 7.5x60mm Pack 50', 'price': 8.99, 'stock': 140},
        {'name': 'Masonry Screws Countersunk 7.5x80mm Pack 50', 'price': 9.99, 'stock': 120},
        {'name': 'Masonry Screws Hex Head 7.5x100mm Pack 25', 'price': 7.99, 'stock': 100},
        
        # Frame Fixings
        {'name': 'Frame Fixings 8x80mm Torx Drive Pack 50', 'price': 9.99, 'stock': 160},
        {'name': 'Frame Fixings 10x100mm Torx Drive Pack 25', 'price': 8.99, 'stock': 130},
        
        # Self-Tapping Screws
        {'name': 'Self-Tapping Screws 4.2x13mm Pan Head Pack 200', 'price': 4.99, 'stock': 240},
        {'name': 'Self-Tapping Screws 4.8x19mm Pan Head Pack 100', 'price': 4.49, 'stock': 220},
        {'name': 'Self-Tapping Screws 6.3x25mm Hex Head Pack 50', 'price': 5.99, 'stock': 180},
        
        # Nails
        {'name': 'Lost Head Nails 50mm Galvanised Pack 500g', 'price': 4.99, 'stock': 200},
        {'name': 'Round Wire Nails 75mm Bright Steel Pack 1kg', 'price': 5.99, 'stock': 180},
        {'name': 'Oval Wire Nails 40mm Bright Steel Pack 500g', 'price': 4.49, 'stock': 190},
        {'name': 'Hardboard Pins 20mm Copper Plated Pack 500g', 'price': 3.99, 'stock': 220},
        {'name': 'Clout Nails 40mm Galvanised Pack 1kg', 'price': 6.99, 'stock': 150},
        {'name': 'Masonry Nails 50mm Hardened Steel Pack 100', 'price': 5.49, 'stock': 160},
        {'name': 'Panel Pins 25mm Veneer Pack 500g', 'price': 3.49, 'stock': 240},
        
        # Wall Plugs & Anchors
        {'name': 'Wall Plugs Brown 7mm Pack 100', 'price': 2.99, 'stock': 400},
        {'name': 'Wall Plugs Red 6mm Pack 100', 'price': 2.49, 'stock': 450},
        {'name': 'Frame Fixing Plugs 10x80mm Pack 50', 'price': 7.99, 'stock': 140},
        {'name': 'Hollow Wall Anchors Metal 4mm Pack 50', 'price': 6.99, 'stock': 160},
        {'name': 'Hollow Wall Anchors Metal 6mm Pack 25', 'price': 5.99, 'stock': 130},
        {'name': 'Cavity Wall Anchors Spring Toggle M6 Pack 10', 'price': 7.49, 'stock': 120},
        {'name': 'Cavity Wall Anchors Spring Toggle M8 Pack 10', 'price': 8.49, 'stock': 100},
        
        # Bolts
        {'name': 'Hex Bolts M6x30mm Zinc Plated Pack 25', 'price': 4.99, 'stock': 200},
        {'name': 'Hex Bolts M8x40mm Zinc Plated Pack 20', 'price': 5.99, 'stock': 180},
        {'name': 'Hex Bolts M10x50mm Zinc Plated Pack 15', 'price': 6.99, 'stock': 150},
        {'name': 'Coach Bolts M8x60mm Zinc Plated Pack 20', 'price': 6.49, 'stock': 140},
        {'name': 'Coach Bolts M10x80mm Zinc Plated Pack 15', 'price': 7.99, 'stock': 120},
        {'name': 'Roofing Bolts M6x50mm Square Neck Pack 20', 'price': 5.49, 'stock': 130},
        
        # Nuts
        {'name': 'Hex Nuts M6 Zinc Plated Pack 100', 'price': 3.99, 'stock': 300},
        {'name': 'Hex Nuts M8 Zinc Plated Pack 50', 'price': 4.49, 'stock': 280},
        {'name': 'Hex Nuts M10 Zinc Plated Pack 50', 'price': 4.99, 'stock': 250},
        {'name': 'Wing Nuts M6 Zinc Plated Pack 50', 'price': 4.99, 'stock': 200},
        {'name': 'Wing Nuts M8 Zinc Plated Pack 25', 'price': 4.49, 'stock': 180},
        {'name': 'Lock Nuts M8 Nylon Insert Pack 50', 'price': 5.99, 'stock': 160},
        
        # Washers
        {'name': 'Flat Washers M6 Zinc Plated Pack 100', 'price': 2.99, 'stock': 350},
        {'name': 'Flat Washers M8 Zinc Plated Pack 100', 'price': 3.49, 'stock': 320},
        {'name': 'Spring Washers M6 Zinc Plated Pack 100', 'price': 3.49, 'stock': 300},
        {'name': 'Spring Washers M8 Zinc Plated Pack 50', 'price': 3.99, 'stock': 280},
        {'name': 'Penny Washers M8 Large Zinc Plated Pack 50', 'price': 4.49, 'stock': 240},
        {'name': 'Rubber Washers 1/2 inch Mixed Pack 50', 'price': 3.99, 'stock': 200},
        {'name': 'Fibre Washers 1/2 inch Red Pack 50', 'price': 3.49, 'stock': 220},
        {'name': 'Coupling Nuts M8 Zinc Plated Pack 10', 'price': 4.99, 'stock': 140},
        
        # Threaded Rod & Studding
        {'name': 'Threaded Rod M8 x 1m Zinc Plated', 'price': 4.99, 'stock': 100},
        {'name': 'Threaded Rod M10 x 1m Zinc Plated', 'price': 5.99, 'stock': 90},
        {'name': 'Studding Connector M8 Zinc Plated Pack 10', 'price': 4.49, 'stock': 120},
        {'name': 'Studding Connector M10 Zinc Plated Pack 10', 'price': 5.49, 'stock': 100},
        
        # Specialty Fasteners
        {'name': 'Tek Screws Self-Drilling 4.8x19mm Pack 100', 'price': 6.99, 'stock': 160},
        {'name': 'Brad Nails 18 Gauge 25mm Pack 1000', 'price': 7.99, 'stock': 140},
        {'name': 'Brad Nails 18 Gauge 32mm Pack 1000', 'price': 8.99, 'stock': 130},
        {'name': 'Staples 10mm Heavy Duty Pack 1000', 'price': 4.99, 'stock': 200},
        {'name': 'Cable Clips Round White 6mm Pack 100', 'price': 3.99, 'stock': 240},
        {'name': 'Nail-In Cable Clips 8mm Black Pack 100', 'price': 4.49, 'stock': 220},
        {'name': 'Screw Eyes Steel 25mm Pack 20', 'price': 3.49, 'stock': 180},
        {'name': 'Screw Hooks Steel 38mm Pack 20', 'price': 3.99, 'stock': 170},
        {'name': 'Gate Hooks and Eyes 150mm Black Pack 2', 'price': 7.99, 'stock': 100},
        {'name': 'Mirror Screws Chrome 25mm Pack 4', 'price': 5.99, 'stock': 120},
        
        # Decking & Outdoor
        {'name': 'Decking Screws 4x50mm Green Pack 200', 'price': 8.99, 'stock': 140},
        {'name': 'Decking Screws 5x70mm Green Pack 100', 'price': 7.99, 'stock': 120},
        {'name': 'Fence Panel Brackets Galvanised Pack 4', 'price': 6.99, 'stock': 110},
        {'name': 'Joist Hangers 50mm Galvanised Pack 10', 'price': 9.99, 'stock': 90},
        
        # Brackets & Plates
        {'name': 'Angle Brackets 50mm Zinc Plated Pack 10', 'price': 4.99, 'stock': 180},
        {'name': 'L Brackets 75mm Heavy Duty Pack 4', 'price': 6.99, 'stock': 130},
        {'name': 'T Plates 100mm Zinc Plated Pack 10', 'price': 5.99, 'stock': 150},
        {'name': 'Mending Plates 100mm Zinc Plated Pack 10', 'price': 4.49, 'stock': 160},
        {'name': 'Corner Braces 50mm Zinc Plated Pack 10', 'price': 5.49, 'stock': 140},
        {'name': 'Shelf Brackets White 200mm Pair', 'price': 7.99, 'stock': 100},
        
        # Rivets
        {'name': 'Blind Rivets Aluminium 4mm Pack 100', 'price': 5.99, 'stock': 180},
        {'name': 'Blind Rivets Multigrip 4.8mm Pack 50', 'price': 6.49, 'stock': 160},
        {'name': 'Rivet Nuts M6 Zinc Plated Pack 20', 'price': 7.99, 'stock': 120},
        
        # Hinge & Door Hardware
        {'name': 'Butt Hinges 75mm Brass Pair', 'price': 5.99, 'stock': 140},
        {'name': 'Tee Hinges 300mm Black Pack 2', 'price': 8.99, 'stock': 100},
        {'name': 'Tower Bolts 150mm Brass', 'price': 6.99, 'stock': 110},
        {'name': 'Barrel Bolts 100mm Chrome', 'price': 5.49, 'stock': 130},
        {'name': 'Padlock Eyes 75mm Galvanised Pair', 'price': 4.99, 'stock': 120},
        {'name': 'Hasp and Staple 100mm Heavy Duty', 'price': 7.99, 'stock': 90},
    ]
    
    count = 0
    for product_data in products:
        slug = slugify(product_data['name'])
        Product.objects.create(
            category=category,
            name=product_data['name'],
            slug=slug,
            description=f"High-quality {product_data['name'].lower()}. Suitable for various construction and DIY projects. Durable and reliable fastening solution.",
            price=product_data['price'],
            cost_price=product_data['price'] * 0.55,  # 45% margin
            stock=product_data['stock'],
            available=True,
            is_online=False,  # Products start in warehouse
            image=f'products/{slug}.jpg'
        )
        count += 1
    
    print(f"   [+] Added {count} Screws & Fixings products")
    return count


def add_paint_decorating(category):
    """Add 72 Paint & Decorating products"""
    print("\nAdding Paint & Decorating...")
    
    products = [
        # Emulsion Paint
        {'name': 'Emulsion Paint Brilliant White Matt 10L', 'price': 24.99, 'stock': 85},
        {'name': 'Emulsion Paint Brilliant White Silk 10L', 'price': 26.99, 'stock': 78},
        {'name': 'Emulsion Paint Magnolia Matt 5L', 'price': 14.99, 'stock': 120},
        {'name': 'Emulsion Paint Magnolia Silk 5L', 'price': 15.99, 'stock': 110},
        {'name': 'Emulsion Paint Ivory Matt 2.5L', 'price': 9.99, 'stock': 95},
        {'name': 'Emulsion Paint Ivory Silk 2.5L', 'price': 10.99, 'stock': 88},
        {'name': 'Emulsion Paint Soft Cream Matt 2.5L', 'price': 9.99, 'stock': 92},
        {'name': 'Emulsion Paint Soft Cream Silk 2.5L', 'price': 10.99, 'stock': 85},
        {'name': 'Emulsion Paint Duck Egg Matt 2.5L', 'price': 12.99, 'stock': 76},
        {'name': 'Emulsion Paint Duck Egg Silk 2.5L', 'price': 13.99, 'stock': 70},
        
        # Gloss Paint
        {'name': 'Gloss Paint Brilliant White 2.5L', 'price': 16.99, 'stock': 95},
        {'name': 'Gloss Paint Brilliant White 750ml', 'price': 8.99, 'stock': 125},
        {'name': 'Gloss Paint Black 750ml', 'price': 9.99, 'stock': 88},
        {'name': 'Gloss Paint Racing Green 750ml', 'price': 10.99, 'stock': 65},
        {'name': 'Gloss Paint Oxford Blue 750ml', 'price': 10.99, 'stock': 68},
        
        # Satinwood Paint
        {'name': 'Satinwood Paint Brilliant White 2.5L', 'price': 18.99, 'stock': 82},
        {'name': 'Satinwood Paint Brilliant White 750ml', 'price': 9.99, 'stock': 110},
        {'name': 'Satinwood Paint Magnolia 750ml', 'price': 10.99, 'stock': 95},
        
        # Undercoat & Primer
        {'name': 'Undercoat White 2.5L', 'price': 14.99, 'stock': 90},
        {'name': 'Undercoat White 750ml', 'price': 7.99, 'stock': 115},
        {'name': 'Multi-Surface Primer White 2.5L', 'price': 16.99, 'stock': 78},
        {'name': 'Metal Primer Red Oxide 750ml', 'price': 9.99, 'stock': 88},
        {'name': 'Wood Primer Pink 2.5L', 'price': 15.99, 'stock': 72},
        
        # Masonry Paint
        {'name': 'Masonry Paint Brilliant White Smooth 10L', 'price': 34.99, 'stock': 65},
        {'name': 'Masonry Paint Brilliant White Textured 10L', 'price': 36.99, 'stock': 58},
        {'name': 'Masonry Paint Magnolia Smooth 5L', 'price': 19.99, 'stock': 75},
        {'name': 'Masonry Paint Sandstone Smooth 5L', 'price': 21.99, 'stock': 68},
        
        # Fence & Shed Paint
        {'name': 'Fence Paint Dark Oak 5L', 'price': 18.99, 'stock': 82},
        {'name': 'Fence Paint Forest Green 5L', 'price': 18.99, 'stock': 78},
        {'name': 'Fence Paint Charcoal Grey 5L', 'price': 19.99, 'stock': 72},
        {'name': 'Shed & Fence Protector Golden Brown 9L', 'price': 24.99, 'stock': 64},
        {'name': 'Shed & Fence Protector Medium Oak 9L', 'price': 24.99, 'stock': 68},
        
        # Wood Stain & Varnish
        {'name': 'Wood Stain Walnut Satin 750ml', 'price': 10.99, 'stock': 85},
        {'name': 'Wood Stain Pine Satin 750ml', 'price': 10.99, 'stock': 88},
        {'name': 'Wood Stain Dark Oak Satin 750ml', 'price': 10.99, 'stock': 82},
        {'name': 'Interior Varnish Clear Satin 750ml', 'price': 11.99, 'stock': 92},
        {'name': 'Interior Varnish Clear Gloss 750ml', 'price': 11.99, 'stock': 88},
        {'name': 'Yacht Varnish Clear Gloss 1L', 'price': 15.99, 'stock': 68},
        {'name': 'Floor Varnish Clear Satin 2.5L', 'price': 24.99, 'stock': 58},
        
        # Spray Paint
        {'name': 'Spray Paint Brilliant White Gloss 400ml', 'price': 6.99, 'stock': 140},
        {'name': 'Spray Paint Black Matt 400ml', 'price': 6.99, 'stock': 135},
        {'name': 'Spray Paint Chrome Effect 400ml', 'price': 8.99, 'stock': 95},
        {'name': 'Spray Paint Hammered Metal Grey 400ml', 'price': 8.99, 'stock': 88},
        {'name': 'Spray Paint Red Gloss 400ml', 'price': 7.99, 'stock': 98},
        
        # Brushes
        {'name': 'Paint Brush Pure Bristle 2 inch', 'price': 7.99, 'stock': 110},
        {'name': 'Paint Brush Pure Bristle 1 inch', 'price': 5.99, 'stock': 125},
        {'name': 'Paint Brush Set Synthetic 5 Piece', 'price': 12.99, 'stock': 85},
        {'name': 'Radiator Brush Long Handle', 'price': 6.99, 'stock': 92},
        
        # Rollers
        {'name': 'Paint Roller Set 9 inch with Tray', 'price': 8.99, 'stock': 105},
        {'name': 'Paint Roller Sleeve Medium Pile 9 inch Pack 2', 'price': 5.99, 'stock': 130},
        {'name': 'Mini Roller Kit 4 inch', 'price': 6.99, 'stock': 98},
        {'name': 'Roller Extension Pole Telescopic 1-2m', 'price': 9.99, 'stock': 75},
        
        # Masking & Protection
        {'name': 'Masking Tape 25mm x 50m', 'price': 2.99, 'stock': 200},
        {'name': 'Masking Tape Professional 38mm x 50m', 'price': 4.99, 'stock': 150},
        {'name': 'Dust Sheet Plastic 12ft x 9ft', 'price': 3.99, 'stock': 180},
        {'name': 'Dust Sheet Cotton Twill 12ft x 9ft', 'price': 14.99, 'stock': 68},
        {'name': 'Low-Tack Masking Film with Tape 1.8m x 33m', 'price': 12.99, 'stock': 55},
        
        # Preparation & Fillers
        {'name': 'Decorators Caulk White 310ml', 'price': 3.99, 'stock': 165},
        {'name': 'All-Purpose Filler Ready Mixed 1kg', 'price': 5.99, 'stock': 145},
        {'name': 'All-Purpose Filler Powder 2kg', 'price': 6.99, 'stock': 128},
        {'name': 'Fine Surface Filler 330ml Tube', 'price': 4.99, 'stock': 155},
        {'name': 'Wood Filler Light Oak 250g', 'price': 5.49, 'stock': 118},
        {'name': 'Wood Filler Dark Oak 250g', 'price': 5.49, 'stock': 112},
        
        # Cleaning & Maintenance
        {'name': 'White Spirit 750ml', 'price': 4.99, 'stock': 142},
        {'name': 'Brush Cleaner 500ml', 'price': 5.99, 'stock': 98},
        {'name': 'Sugar Soap Liquid 500ml', 'price': 4.49, 'stock': 125},
        {'name': 'Paint Kettle 2.5L Plastic', 'price': 3.99, 'stock': 88},
        
        # Specialty Products
        {'name': 'Rust Converter and Primer 250ml', 'price': 9.99, 'stock': 75},
        {'name': 'Damp Seal White 1L', 'price': 14.99, 'stock': 62},
        {'name': 'Mould Resistant Paint White 2.5L', 'price': 19.99, 'stock': 58},
    ]
    
    count = 0
    for product_data in products:
        slug = slugify(product_data['name'])
        Product.objects.create(
            category=category,
            name=product_data['name'],
            slug=slug,
            description=f"Professional quality {product_data['name'].lower()}. Ideal for interior and exterior decoration projects. Easy to apply with excellent coverage and finish.",
            price=product_data['price'],
            cost_price=product_data['price'] * 0.60,  # 40% margin
            stock=product_data['stock'],
            available=True,
            is_online=False,  # Products start in warehouse
            image=f'products/{slug}.jpg'
        )
        count += 1
    
    print(f"   [+] Added {count} Paint & Decorating products")
    return count


def add_sealants(category):
    """Add 15 Sealants products"""
    print("\nAdding Sealants...")
    
    products = [
        {
            'name': 'Silicone Sealant Clear 310ml',
            'description': 'General purpose silicone sealant suitable for kitchens and bathrooms. Waterproof seal for sanitary ware, tiles, and glass. Mould resistant formulation.',
            'price': 4.99,
            'stock': 200,
        },
        {
            'name': 'Silicone Sealant White 310ml',
            'description': 'White silicone sealant for kitchen and bathroom applications. Creates watertight seals around sinks, baths, and showers. Resists mould and mildew.',
            'price': 4.99,
            'stock': 180,
        },
        {
            'name': 'Frame Sealant Brown 310ml',
            'description': 'Acrylic-based frame sealant in brown. Paintable and overpaintable. Perfect for sealing gaps around door and window frames. Low odour formula.',
            'price': 5.49,
            'stock': 150,
        },
        {
            'name': 'Frame Sealant White 310ml',
            'description': 'White acrylic frame sealant for interior and exterior use. Flexible and paintable. Ideal for filling gaps between frames and walls. Easy to apply.',
            'price': 5.49,
            'stock': 160,
        },
        {
            'name': 'Bathroom Sealant Clear 310ml',
            'description': 'Specialist bathroom sealant with anti-fungal properties. Clear finish suitable for all bathroom fixtures. Waterproof and long-lasting seal.',
            'price': 6.99,
            'stock': 140,
        },
        {
            'name': 'Sanitary Silicone Translucent 310ml',
            'description': 'Premium sanitary silicone in translucent finish. Enhanced mould resistance for wet areas. Suitable for all bathroom and kitchen sealing.',
            'price': 6.49,
            'stock': 130,
        },
        {
            'name': 'Roof and Gutter Sealant Grey 310ml',
            'description': 'Heavy-duty weatherproof sealant for roofs and gutters. Flexible in all weather conditions. Bonds to metal, plastic, and masonry. UV resistant.',
            'price': 7.99,
            'stock': 100,
        },
        {
            'name': 'Multi-Purpose Sealant Black 290ml',
            'description': 'Versatile multi-purpose sealant in black. Suitable for indoor and outdoor use. Adheres to most building materials. Paintable when cured.',
            'price': 8.49,
            'stock': 90,
        },
        {
            'name': 'Fire Rated Sealant Grey 310ml',
            'description': 'Intumescent fire-rated sealant for sealing service penetrations. Expands when exposed to heat to maintain fire resistance. Grey finish.',
            'price': 12.99,
            'stock': 70,
        },
        {
            'name': 'Grab Adhesive White 350ml',
            'description': 'High-strength grab adhesive and sealant. Instant grab with no support needed. Bonds wood, metal, plastic, and more. Interior and exterior use.',
            'price': 9.99,
            'stock': 120,
        },
        {
            'name': 'Neutral Cure Silicone Clear 310ml',
            'description': 'Neutral cure silicone suitable for sensitive surfaces. Non-corrosive formula safe for metals, mirrors, and natural stone. Professional grade.',
            'price': 8.99,
            'stock': 110,
        },
        {
            'name': 'Exterior Frame Sealant Brown 380ml',
            'description': 'Heavy-duty exterior frame sealant in brown. Weather resistant and flexible. Ideal for external window and door frames. Long-lasting performance.',
            'price': 6.99,
            'stock': 95,
        },
        {
            'name': 'Kitchen and Bath Sealant White 310ml',
            'description': 'Premium kitchen and bathroom sealant in white. Anti-mould formula with enhanced flexibility. Food-safe certification. Easy to clean surface.',
            'price': 5.99,
            'stock': 170,
        },
        {
            'name': 'Gutter Repair Sealant Clear 290ml',
            'description': 'Specialist gutter repair sealant for emergency fixes. Applies to wet surfaces. Flexible and waterproof. Clear finish blends with any gutter.',
            'price': 9.49,
            'stock': 85,
        },
        {
            'name': 'Acoustic Sealant Grey 310ml',
            'description': 'Professional acoustic sealant for soundproofing applications. Maintains flexibility to dampen vibrations. Use with acoustic plasterboard systems.',
            'price': 11.99,
            'stock': 60,
        },
    ]
    
    count = 0
    for product_data in products:
        slug = slugify(product_data['name'])
        Product.objects.create(
            category=category,
            name=product_data['name'],
            slug=slug,
            description=product_data['description'],
            price=product_data['price'],
            cost_price=product_data['price'] * 0.55,  # 45% margin
            stock=product_data['stock'],
            available=True,
            is_online=False,  # Products start in warehouse
            image=f'products/{slug}.jpg'
        )
        count += 1
    
    print(f"   [+] Added {count} Sealants products")
    return count


def main():
    """Main function to populate the database"""
    print("=" * 60)
    print("XYZShop - Fresh Database Population Script")
    print("=" * 60)
    
    # Check if database is empty or has products
    existing_products = Product.objects.count()
    existing_categories = Category.objects.count()
    
    if existing_products > 0 or existing_categories > 0:
        print(f"\n[!] WARNING: Database already has data:")
        print(f"   - {existing_categories} categories")
        print(f"   - {existing_products} products")
        print("\nThis script will DELETE ALL existing data and create fresh records.")
        print("All products will be created with is_online=False (warehouse status).")
        response = input("\nContinue? (yes/no): ")
        if response.lower() != 'yes':
            print("\n[-] Operation cancelled")
            return
        
        # Delete all existing products and categories
        print("\nDeleting existing data...")
        Product.objects.all().delete()
        print(f"   Deleted {existing_products} products")
        Category.objects.all().delete()
        print(f"   Deleted {existing_categories} categories")
    
    print("\nStarting database population...\n")
    
    # Create categories
    categories = create_categories()
    
    # Add products by category
    total_products = 0
    
    total_products += add_power_tools(categories['power-tools'])
    total_products += add_screws_fixings(categories['screws-fixings'])
    total_products += add_paint_decorating(categories['paint-decorating'])
    total_products += add_sealants(categories['sealants'])
    
    # Summary
    print("\n" + "=" * 60)
    print("[SUCCESS] Database Population Complete!")
    print("=" * 60)
    print(f"\nTotal items added: {total_products} products")
    print(f"Total categories: {Category.objects.count()}")
    print(f"Total products in database: {Product.objects.count()}")
    print(f"\nAll products created with is_online=False (warehouse status)")
    print("Use set_existing_products_online.py to move products online")
    print("\nProduct breakdown by category:")
    for category in Category.objects.all():
        count = Product.objects.filter(category=category).count()
        print(f"   - {category.name}: {count} products")
    
    print("\nNext Steps:")
    print("   1. Generate product images:")
    print("      python generate_power_tools_images.py")
    print("      python generate_screws_fixings_images.py")
    print("      python generate_paint_images.py")
    print("      python generate_sealants_images.py")
    print("\n   2. Create superuser:")
    print("      python manage.py createsuperuser")
    print("\n   3. Run server:")
    print("      python manage.py runserver")
    print("\n   4. Access the site:")
    print("      Main site: http://127.0.0.1:8000/")
    print("      Admin: http://127.0.0.1:8000/admin/")
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
