"""
Restore Database from Export
This script recreates the complete database including:
- 505 products from the exported data
- Product descriptions (generated)
- Price history records (505 entries)
- 10 sample customers with reviews
- 22 orders with 110 order items
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xyz_store.settings')
django.setup()

from django.contrib.auth import get_user_model
from products.models import Product, Category, ProductPriceHistory, ProductReview, Sale
from orders.models import Order, OrderItem
from exported_products import CATEGORIES, ALL_PRODUCTS

User = get_user_model()

def restore_database():
    """Restore all products and categories from exported data"""
    print("=" * 60)
    print("XYZShop - Complete Database Restoration Script")
    print("=" * 60)
    print("\nThis script will restore:")
    print("  1. Products and Categories (505 products, 9 categories)")
    print("  2. Product Descriptions (auto-generated)")
    print("  3. Price History Records (505 entries)")
    print("  4. Sample Customers (50 users)")
    print("  5. Product Reviews (varies based on orders)")
    print("  6. Orders (500 orders distributed among 50 customers)")
    print("  7. Sales Records (one per order item)")
    print("\n" + "=" * 60)
    
    # Check if database has existing data
    existing_products = Product.objects.count()
    existing_categories = Category.objects.count()
    existing_users = User.objects.filter(is_superuser=False).count()
    existing_orders = Order.objects.count()
    existing_reviews = ProductReview.objects.count()
    existing_price_history = ProductPriceHistory.objects.count()
    existing_sales = Sale.objects.count()
    
    if any([existing_products, existing_categories, existing_users, existing_orders, existing_reviews, existing_price_history, existing_sales]):
        print(f"\nWARNING: Database already has data:")
        print(f"   - {existing_categories} categories")
        print(f"   - {existing_products} products")
        print(f"   - {existing_users} non-admin users")
        print(f"   - {existing_orders} orders")
        print(f"   - {existing_reviews} reviews")
        print(f"   - {existing_price_history} price history records")
        print(f"   - {existing_sales} sales records")
        print("\nThis script will DELETE ALL existing data and restore from export.")
        print("(Superuser accounts will be preserved)")
        response = input("\nContinue? (yes/no): ")
        if response.lower() != 'yes':
            print("\nOperation cancelled")
            return
        
        # Delete existing data
        print("\nDeleting existing data...")
        Sale.objects.all().delete()
        print(f"   Deleted {existing_sales} sales")
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        print(f"   Deleted {existing_orders} orders")
        ProductReview.objects.all().delete()
        print(f"   Deleted {existing_reviews} reviews")
        ProductPriceHistory.objects.all().delete()
        print(f"   Deleted {existing_price_history} price history records")
        Product.objects.all().delete()
        print(f"   Deleted {existing_products} products")
        Category.objects.all().delete()
        print(f"   Deleted {existing_categories} categories")
        User.objects.filter(is_superuser=False).delete()
        print(f"   Deleted {existing_users} non-admin users")
    
    print("\nRestoring database from export...\n")
    
    # Create categories
    print("Creating categories...")
    categories = {}
    for cat_data in CATEGORIES:
        category = Category.objects.create(
            name=cat_data['name'],
            slug=cat_data['slug']
        )
        categories[cat_data['slug']] = category
        print(f"   [+] Created: {cat_data['name']}")
    
    # Create products by category
    total_created = 0
    
    for slug, products_list in ALL_PRODUCTS.items():
        category = categories[slug]
        print(f"\nAdding {category.name}...")
        
        count = 0
        for product_data in products_list:
            Product.objects.create(
                category=category,
                name=product_data['name'],
                slug=product_data['slug'],
                description=product_data['description'],
                price=product_data['price'],
                cost_price=product_data['cost_price'],
                stock=product_data['stock'],
                available=product_data['available'],
                is_online=product_data['is_online'],
                image=f"products/{product_data['image']}" if product_data['image'] else ''
            )
            count += 1
        
        print(f"   [+] Added {count} products")
        total_created += count
    
    # Summary
    print("\n" + "=" * 60)
    print("SUCCESS: Database Restoration Complete!")
    print("=" * 60)
    print(f"\nTotal products created: {total_created}")
    print(f"Total categories: {Category.objects.count()}")
    
    # Statistics
    online_count = Product.objects.filter(is_online=True).count()
    warehouse_count = Product.objects.filter(is_online=False).count()
    
    print(f"\nProducts online: {online_count}")
    print(f"Products in warehouse: {warehouse_count}")
    
    print("\nProducts by category:")
    for category in Category.objects.all().order_by('name'):
        total = Product.objects.filter(category=category).count()
        online = Product.objects.filter(category=category, is_online=True).count()
        warehouse = Product.objects.filter(category=category, is_online=False).count()
        print(f"   - {category.name}: {total} total ({online} online, {warehouse} warehouse)")
    
    # Step 2: Populate product descriptions
    populate_product_descriptions()
    
    # Step 3: Create price history
    create_price_history()
    
    # Step 4: Create sample customers
    customers = create_sample_customers()
    
    # Step 5: Create reviews and orders
    create_reviews_and_orders(customers)
    
    # Final summary
    print("\n" + "=" * 60)
    print("COMPLETE DATABASE RESTORATION FINISHED!")
    print("=" * 60)
    print("\nFinal Statistics:")
    print(f"  Products: {Product.objects.count()}")
    print(f"  Categories: {Category.objects.count()}")
    print(f"  Price History Records: {ProductPriceHistory.objects.count()}")
    print(f"  Customers: {User.objects.filter(is_superuser=False).count()}")
    print(f"  Reviews: {ProductReview.objects.count()}")
    print(f"  Orders: {Order.objects.count()}")
    print(f"  Order Items: {OrderItem.objects.count()}")
    print(f"  Sales: {Sale.objects.count()}")
    print("\n" + "=" * 60)


def populate_product_descriptions():
    """Generate descriptions for products based on their names"""
    import re
    from decimal import Decimal
    
    print("\n" + "=" * 60)
    print("Populating Product Descriptions...")
    print("=" * 60)
    
    products = Product.objects.all()
    updated_count = 0
    
    for product in products:
        if product.description:
            continue
            
        name_lower = product.name.lower()
        description = ""
        
        # Pattern matching for description generation
        if 'drill' in name_lower:
            if 'cordless' in name_lower:
                description = f"Professional cordless drill with variable speed control and LED work light. Perfect for drilling into wood, metal, and plastic. Includes rechargeable battery and charger."
            elif 'hammer' in name_lower:
                description = f"Heavy-duty hammer drill with powerful motor and adjustable depth stop. Ideal for masonry work and concrete drilling. Features comfortable grip and dust extraction."
            elif 'bit' in name_lower:
                description = f"High-quality drill bit set made from durable materials. Suitable for various drilling applications. Comes with storage case for easy organization."
            else:
                description = f"Reliable electric drill with variable speed settings. Perfect for professional and DIY projects. Ergonomic design for comfortable extended use."
        
        elif 'screwdriver' in name_lower:
            if 'set' in name_lower:
                description = f"Comprehensive screwdriver set with multiple head types and sizes. Chrome vanadium steel construction for durability. Includes Phillips, flathead, and Torx drivers."
            else:
                description = f"Precision screwdriver with comfortable grip handle. Hardened steel tip for long-lasting performance. Essential tool for any toolbox."
        
        elif 'hammer' in name_lower:
            if 'claw' in name_lower:
                description = f"Classic claw hammer with fiberglass handle for reduced vibration. Forged steel head with polished finish. Perfect for general carpentry and construction work."
            elif 'club' in name_lower or 'lump' in name_lower:
                description = f"Heavy-duty lump hammer for demolition and masonry work. Drop-forged steel head with comfortable handle. Ideal for breaking concrete and chiseling."
            else:
                description = f"Professional-grade hammer with balanced design and comfortable grip. Durable construction for years of reliable service."
        
        elif 'saw' in name_lower:
            if 'hand' in name_lower or 'panel' in name_lower:
                description = f"Sharp hand saw with precision-ground teeth for smooth cutting. Comfortable handle with ergonomic design. Perfect for cutting wood, plastic, and laminates."
            elif 'circular' in name_lower:
                description = f"Powerful circular saw with adjustable depth and angle settings. Laser guide for accurate cutting. Ideal for ripping and cross-cutting lumber."
            elif 'jig' in name_lower:
                description = f"Versatile jigsaw with variable speed control and orbital action. Quick blade change system. Perfect for curved and intricate cuts."
            else:
                description = f"Quality saw designed for precision cutting. Sharp blade and comfortable grip for accurate results."
        
        elif 'spanner' in name_lower or 'wrench' in name_lower:
            if 'adjustable' in name_lower:
                description = f"Adjustable wrench with wide jaw opening. Chrome-plated finish resists corrosion. Essential tool for plumbing and mechanical work."
            elif 'set' in name_lower:
                description = f"Complete wrench set with metric and imperial sizes. Chrome vanadium steel construction. Includes storage rack for organization."
            else:
                description = f"Durable wrench with precision machined jaws. Chrome finish for rust resistance. Perfect for tightening and loosening nuts and bolts."
        
        elif 'pliers' in name_lower:
            if 'combination' in name_lower:
                description = f"Multi-purpose combination pliers with wire cutting capability. Cushioned handles for comfort. Ideal for gripping, bending, and cutting."
            elif 'long nose' in name_lower or 'needle' in name_lower:
                description = f"Precision long-nose pliers for detailed work. Perfect for electronics and jewelry making. Spring-loaded handles for easy operation."
            else:
                description = f"Heavy-duty pliers with strong gripping power. Durable construction and comfortable handles. Essential for any workshop."
        
        elif 'tape measure' in name_lower or 'measuring tape' in name_lower:
            description = f"Professional tape measure with clear markings in metric and imperial units. Auto-lock mechanism and belt clip. Durable nylon-coated blade."
        
        elif 'spirit level' in name_lower or 'level' in name_lower:
            description = f"Precision spirit level with multiple vials for horizontal, vertical, and 45-degree measurements. Solid aluminum construction with comfortable handles."
        
        elif 'chisel' in name_lower:
            if 'set' in name_lower:
                description = f"Professional chisel set with various sizes. Hardened and tempered steel blades. Includes protective caps and storage case."
            else:
                description = f"Sharp wood chisel with comfortable handle. Hardened steel blade holds edge well. Perfect for carpentry and woodworking."
        
        elif 'paint' in name_lower or 'emulsion' in name_lower or 'gloss' in name_lower:
            description = f"High-quality paint with excellent coverage and durability. Low VOC formula for indoor use. Easy to apply with brush or roller."
        
        elif 'brush' in name_lower and 'paint' in name_lower:
            description = f"Professional paint brush with synthetic bristles. Smooth application and excellent paint pickup. Easy to clean and maintain."
        
        elif 'roller' in name_lower and 'paint' in name_lower:
            description = f"Paint roller with medium pile sleeve for smooth finishes. Comfortable handle and sturdy frame. Ideal for walls and ceilings."
        
        elif 'screw' in name_lower:
            description = f"High-quality screws made from hardened steel. Corrosion-resistant coating for durability. Available in various sizes for different applications."
        
        elif 'nail' in name_lower:
            description = f"Strong nails suitable for construction and carpentry. Galvanized finish prevents rust. Bulk pack for professional use."
        
        elif 'bolt' in name_lower:
            description = f"Heavy-duty bolts with precise threading. Zinc-plated for corrosion resistance. Includes matching nuts and washers."
        
        elif 'sealant' in name_lower or 'silicone' in name_lower:
            description = f"Flexible sealant with excellent adhesion. Waterproof and weather-resistant. Perfect for bathrooms, kitchens, and outdoor applications."
        
        elif 'pipe' in name_lower:
            description = f"Durable pipe suitable for plumbing and drainage systems. Complies with building regulations. Easy to cut and install."
        
        elif 'tap' in name_lower or 'faucet' in name_lower:
            description = f"Quality tap with ceramic disc cartridge for smooth operation. Chrome finish resists tarnishing. Easy to install and maintain."
        
        elif 'valve' in name_lower:
            description = f"Reliable valve for controlling water flow. Brass construction for durability. Standard size for easy replacement."
        
        elif 'cable' in name_lower or 'wire' in name_lower:
            description = f"Electrical cable meeting safety standards. Suitable for domestic and commercial installations. Available in various lengths."
        
        elif 'socket' in name_lower and ('electrical' in name_lower or 'outlet' in name_lower or 'double' in name_lower or 'single' in name_lower):
            description = f"Safe electrical socket with shuttered design. Easy to install and complies with regulations. White finish to match standard decor."
        
        elif 'switch' in name_lower and ('light' in name_lower or 'electrical' in name_lower):
            description = f"Reliable light switch with smooth action. Modern design and easy installation. Suitable for standard wall boxes."
        
        elif 'bulb' in name_lower or 'lamp' in name_lower:
            description = f"Energy-efficient bulb with long lifespan. Provides bright, consistent illumination. Standard fitting for easy replacement."
        
        elif 'lock' in name_lower:
            description = f"Secure lock with smooth operation. Durable construction and multiple key options. Easy to install and maintain."
        
        elif 'hinge' in name_lower:
            description = f"Strong hinge with smooth operation and long life. Suitable for doors and cabinets. Includes screws for installation."
        
        elif 'handle' in name_lower or 'knob' in name_lower:
            description = f"Stylish handle with comfortable grip. Durable finish resists wear. Easy to fit to doors and drawers."
        
        elif 'sandpaper' in name_lower:
            description = f"Quality sandpaper for smoothing wood, metal, and painted surfaces. Various grit sizes available. Suitable for hand or machine use."
        
        elif 'ladder' in name_lower:
            description = f"Sturdy ladder with non-slip feet and wide steps. Lightweight aluminum construction. Suitable for domestic and professional use."
        
        elif 'tool box' in name_lower or 'toolbox' in name_lower:
            description = f"Spacious tool box with multiple compartments. Durable plastic construction with secure latches. Comfortable carrying handle."
        
        elif 'work bench' in name_lower or 'workbench' in name_lower:
            description = f"Robust workbench with solid work surface. Adjustable height and built-in storage. Perfect for workshops and garages."
        
        elif 'safety' in name_lower:
            if 'goggles' in name_lower or 'glasses' in name_lower:
                description = f"Protective safety goggles with impact-resistant lenses. Comfortable fit with adjustable strap. Essential PPE for workshop use."
            elif 'glove' in name_lower:
                description = f"Durable work gloves with reinforced palms. Comfortable fit and good dexterity. Suitable for various manual tasks."
            else:
                description = f"Important safety equipment for workshop protection. Meets safety standards and regulations."
        
        elif 'garden' in name_lower:
            if 'hose' in name_lower:
                description = f"Flexible garden hose with standard fittings. UV-resistant and kink-free. Perfect for watering plants and washing."
            elif 'fork' in name_lower or 'spade' in name_lower or 'rake' in name_lower or 'trowel' in name_lower:
                description = f"Robust garden tool with comfortable handle. Rust-resistant coating for durability. Essential for gardening and landscaping."
            else:
                description = f"Quality garden equipment for outdoor maintenance. Durable construction for years of service."
        
        elif 'compressor' in name_lower:
            description = f"Powerful air compressor suitable for various pneumatic tools. Oil-free pump for low maintenance. Includes pressure gauge and regulator."
        
        elif 'generator' in name_lower:
            description = f"Reliable generator providing portable power. Quiet operation and fuel-efficient engine. Perfect for remote sites and emergencies."
        
        elif 'adhesive' in name_lower or 'glue' in name_lower:
            description = f"Strong adhesive for bonding various materials. Quick-setting formula with excellent holding power. Suitable for indoor and outdoor use."
        
        elif 'filler' in name_lower:
            description = f"Ready-mixed filler for repairing holes and cracks. Easy to sand when dry. Suitable for walls, ceilings, and woodwork."
        
        elif 'masking tape' in name_lower or 'duct tape' in name_lower or 'insulation tape' in name_lower:
            description = f"Versatile tape with strong adhesion. Easy to apply and remove. Essential for DIY and professional use."
        
        elif 'extension lead' in name_lower or 'extension cable' in name_lower or 'power strip' in name_lower:
            description = f"Heavy-duty extension lead with multiple sockets. Surge protection and safety switch. Ideal for workshop and home use."
        
        elif 'flashlight' in name_lower or 'torch' in name_lower:
            description = f"Bright LED flashlight with long battery life. Durable construction and water-resistant. Perfect for emergencies and outdoor activities."
        
        elif 'battery' in name_lower:
            description = f"High-quality batteries with reliable performance. Long shelf life and consistent power output. Available in various sizes."
        
        elif 'bucket' in name_lower or 'container' in name_lower:
            description = f"Durable bucket suitable for various applications. Strong handle and robust construction. Easy to clean and store."
        
        elif 'trowel' in name_lower and 'garden' not in name_lower:
            description = f"Professional bricklaying trowel with comfortable grip. Hardened steel blade for durability. Essential for masonry work."
        
        elif 'float' in name_lower and ('plastering' in name_lower or 'plaster' in name_lower):
            description = f"Plastering float with smooth surface for finishing. Comfortable handle for extended use. Perfect for creating smooth wall finishes."
        
        elif 'wheelbarrow' in name_lower:
            description = f"Heavy-duty wheelbarrow with pneumatic tire. Large capacity and balanced design. Ideal for moving materials around site."
        
        elif 'shovel' in name_lower or 'spade' in name_lower and 'garden' not in name_lower:
            description = f"Strong shovel with hardened blade. Comfortable grip and durable construction. Perfect for excavation and landscaping."
        
        elif 'brush' in name_lower and 'paint' not in name_lower:
            description = f"Durable brush suitable for various cleaning tasks. Strong bristles and comfortable handle. Long-lasting performance."
        
        elif 'broom' in name_lower:
            description = f"Sturdy broom with angled bristles for efficient sweeping. Comfortable handle and durable construction. Suitable for indoor and outdoor use."
        
        elif 'dustpan' in name_lower:
            description = f"Practical dustpan with rubber edge for better contact. Comfortable handle and hanging hole. Works perfectly with any broom."
        
        elif 'bin' in name_lower or 'waste' in name_lower:
            description = f"Durable waste bin with secure lid. Easy to clean and odor-resistant. Available in various sizes for different needs."
        
        elif 'marker' in name_lower or 'pencil' in name_lower and 'carpenter' in name_lower:
            description = f"Professional marking tool for accurate measurements. Easy to use and long-lasting. Essential for carpentry and construction work."
        
        elif 'knife' in name_lower and ('utility' in name_lower or 'stanley' in name_lower or 'craft' in name_lower):
            description = f"Sharp utility knife with retractable blade. Comfortable grip and blade storage. Perfect for cutting various materials."
        
        elif 'blade' in name_lower and 'knife' not in name_lower:
            description = f"Replacement blades made from high-quality steel. Sharp edge for clean cuts. Compatible with standard utility knives."
        
        elif 'file' in name_lower:
            description = f"Hardened steel file for shaping and smoothing metal, wood, and plastic. Comfortable handle. Available in various cuts."
        
        elif 'rasp' in name_lower:
            description = f"Heavy-duty rasp for rapid material removal. Durable construction with comfortable grip. Ideal for woodworking and metalwork."
        
        elif 'clamp' in name_lower or 'vice' in name_lower or 'vise' in name_lower:
            description = f"Strong clamp providing secure hold. Easy adjustment and quick release. Essential for workshop and carpentry projects."
        
        elif 'angle grinder' in name_lower or 'grinder' in name_lower:
            description = f"Powerful angle grinder for cutting and grinding. Adjustable guard and side handle. Suitable for metal, stone, and masonry work."
        
        elif 'sander' in name_lower:
            description = f"Efficient sander for smooth finishes. Variable speed control and dust collection. Perfect for wood, metal, and painted surfaces."
        
        elif 'router' in name_lower and 'tool' in name_lower.lower() or 'wood' in name_lower:
            description = f"Versatile router for cutting decorative edges and grooves. Variable speed and depth adjustment. Essential for woodworking projects."
        
        elif 'plane' in name_lower and ('wood' in name_lower or 'block' in name_lower or 'jack' in name_lower):
            description = f"Precision plane for smoothing and shaping wood. Sharp blade and comfortable grip. Perfect for carpentry and fine woodworking."
        
        elif 'axe' in name_lower or 'hatchet' in name_lower:
            description = f"Sharp axe with balanced design. Durable handle and hardened steel head. Ideal for splitting wood and outdoor work."
        
        elif 'pickaxe' in name_lower or 'pick' in name_lower and 'axe' in name_lower:
            description = f"Heavy-duty pickaxe for breaking hard ground. Drop-forged steel head with comfortable handle. Essential for excavation work."
        
        elif 'crowbar' in name_lower or 'pry bar' in name_lower or 'wrecking bar' in name_lower:
            description = f"Strong crowbar for demolition and prying. Hardened steel construction. Multiple uses in construction and renovation work."
        
        elif 'stud' in name_lower and 'finder' in name_lower:
            description = f"Electronic stud finder for locating wall studs. LCD display and audio alert. Essential for hanging heavy items safely."
        
        elif 'detector' in name_lower and ('metal' in name_lower or 'pipe' in name_lower or 'cable' in name_lower):
            description = f"Multi-scanner detector for finding hidden pipes, cables, and studs. Easy to use with clear display. Prevents costly drilling mistakes."
        
        elif 'laser' in name_lower and ('measure' in name_lower or 'distance' in name_lower):
            description = f"Digital laser measure for accurate distance measurements. Easy to read display and memory function. Perfect for professional and DIY use."
        
        elif 'moisture' in name_lower and 'meter' in name_lower:
            description = f"Digital moisture meter for detecting damp. Pin or pinless operation. Essential for preventing water damage and mold."
        
        elif 'multimeter' in name_lower or 'voltage tester' in name_lower:
            description = f"Digital multimeter for electrical testing. Measures voltage, current, and resistance. Essential for electrical work and troubleshooting."
        
        elif 'timer' in name_lower and 'electrical' in name_lower:
            description = f"Programmable timer for controlling electrical devices. Multiple on/off settings. Energy-saving and security features."
        
        elif 'thermostat' in name_lower:
            description = f"Digital thermostat for precise temperature control. Easy programming and energy-saving features. Simple installation and user-friendly interface."
        
        elif 'radiator' in name_lower and ('valve' in name_lower or 'key' in name_lower or 'bleed' in name_lower):
            description = f"Radiator valve for controlling heating flow. Easy adjustment and reliable operation. Helps optimize heating efficiency."
        
        elif 'drain' in name_lower and ('cleaner' in name_lower or 'unblocker' in name_lower or 'rod' in name_lower):
            description = f"Effective drain cleaning solution. Powerful formula dissolves blockages. Safe for all pipe types when used as directed."
        
        elif 'plunger' in name_lower:
            description = f"Heavy-duty plunger for clearing blockages. Strong suction cup and comfortable handle. Essential for bathroom and kitchen maintenance."
        
        elif 'washer' in name_lower and ('tap' in name_lower or 'hose' in name_lower or 'fitting' in name_lower):
            description = f"Rubber washers for sealing connections. Various sizes for different applications. Prevents leaks in plumbing fittings."
        
        elif 'ptfe' in name_lower or 'thread tape' in name_lower:
            description = f"PTFE tape for sealing threaded pipe connections. Easy to apply and reliable seal. Essential for plumbing installations."
        
        elif 'joint' in name_lower and ('compound' in name_lower or 'cement' in name_lower):
            description = f"Joint compound for finishing plasterboard seams. Easy to apply and sand. Creates smooth, professional finish."
        
        elif 'plasterboard' in name_lower or 'drywall' in name_lower or 'gypsum' in name_lower:
            description = f"High-quality plasterboard for walls and ceilings. Easy to cut and install. Provides smooth surface for decoration."
        
        elif 'insulation' in name_lower and 'tape' not in name_lower:
            description = f"Thermal insulation for improved energy efficiency. Easy to install and long-lasting. Reduces heat loss and energy bills."
        
        elif 'membrane' in name_lower or 'vapor barrier' in name_lower or 'dpm' in name_lower:
            description = f"Damp-proof membrane for moisture protection. Heavy-duty polyethylene construction. Essential for floor and wall protection."
        
        elif 'cement' in name_lower and 'joint' not in name_lower:
            description = f"High-strength cement for construction work. Consistent quality and reliable setting. Suitable for various building applications."
        
        elif 'mortar' in name_lower:
            description = f"Ready-mixed mortar for bricklaying and blockwork. Easy to use and weather-resistant. Provides strong bond for masonry."
        
        elif 'concrete' in name_lower and 'mix' in name_lower:
            description = f"Pre-mixed concrete for various applications. Consistent quality and easy preparation. Suitable for footings, posts, and repairs."
        
        elif 'grout' in name_lower:
            description = f"Quality grout for tile joints. Water-resistant and color-fast. Easy to apply with professional finish."
        
        elif 'tile' in name_lower and ('adhesive' in name_lower or 'cement' in name_lower):
            description = f"Strong tile adhesive for wall and floor tiles. Water-resistant and durable bond. Suitable for ceramic and porcelain tiles."
        
        elif 'primer' in name_lower or 'undercoat' in name_lower:
            description = f"Quality primer for preparing surfaces. Improves paint adhesion and coverage. Essential for professional finish."
        
        elif 'varnish' in name_lower or 'lacquer' in name_lower:
            description = f"Clear protective varnish for wood surfaces. Enhances natural grain and provides durable finish. Suitable for indoor and outdoor use."
        
        elif 'stain' in name_lower and 'wood' in name_lower:
            description = f"Wood stain for enhancing natural grain. Range of colors available. Easy to apply with long-lasting results."
        
        elif 'stripper' in name_lower or 'remover' in name_lower:
            description = f"Effective paint and varnish remover. Fast-acting formula for quick results. Suitable for wood, metal, and masonry."
        
        elif 'turps' in name_lower or 'white spirit' in name_lower or 'thinner' in name_lower:
            description = f"Paint thinner for cleaning brushes and thinning oil-based paints. High-quality solvent. Essential for decorating work."
        
        else:
            # Generic description based on category
            if product.category:
                category_name = product.category.name.lower()
                if 'tool' in category_name:
                    description = f"Quality {product.name.lower()} from our professional tool range. Durable construction and reliable performance. Essential for your toolkit."
                elif 'electrical' in category_name:
                    description = f"Reliable {product.name.lower()} meeting electrical safety standards. Easy to install and use. Suitable for domestic applications."
                elif 'plumbing' in category_name:
                    description = f"Professional {product.name.lower()} for plumbing installations. Durable materials and easy to fit. Complies with regulations."
                elif 'paint' in category_name:
                    description = f"High-quality {product.name.lower()} for decorating projects. Easy application and excellent finish. Suitable for indoor and outdoor use."
                elif 'garden' in category_name:
                    description = f"Durable {product.name.lower()} for garden maintenance. Weather-resistant construction. Makes outdoor work easier."
                else:
                    description = f"Quality {product.name.lower()} suitable for professional and DIY use. Durable construction and reliable performance."
            else:
                description = f"Professional-grade {product.name.lower()} with excellent build quality. Suitable for a wide range of applications."
        
        if description:
            product.description = description
            product.save()
            updated_count += 1
    
    print(f"\n   Updated {updated_count} product descriptions")
    print("\n" + "=" * 60)


def create_price_history():
    """Create initial price history for all products"""
    print("\n" + "=" * 60)
    print("Creating Price History Records...")
    print("=" * 60)
    
    products = Product.objects.all()
    created_count = 0
    
    for product in products:
        # Create initial price history record
        ProductPriceHistory.objects.create(
            product=product,
            cost_price=product.cost_price,
            selling_price=product.price,
            changed_by=None,
            reason="Initial price record"
        )
        created_count += 1
    
    print(f"\n   Created {created_count} price history records")
    print("\n" + "=" * 60)


def create_sample_customers():
    """Create 50 sample customers"""
    print("\n" + "=" * 60)
    print("Creating Sample Customers...")
    print("=" * 60)
    
    customers_data = [
        {'username': 'sarah_jones', 'first_name': 'Sarah', 'last_name': 'Jones', 'email': 'sarah.jones@example.com'},
        {'username': 'mike_brown', 'first_name': 'Mike', 'last_name': 'Brown', 'email': 'mike.brown@example.com'},
        {'username': 'emma_wilson', 'first_name': 'Emma', 'last_name': 'Wilson', 'email': 'emma.wilson@example.com'},
        {'username': 'james_taylor', 'first_name': 'James', 'last_name': 'Taylor', 'email': 'james.taylor@example.com'},
        {'username': 'olivia_davis', 'first_name': 'Olivia', 'last_name': 'Davis', 'email': 'olivia.davis@example.com'},
        {'username': 'david_miller', 'first_name': 'David', 'last_name': 'Miller', 'email': 'david.miller@example.com'},
        {'username': 'sophie_anderson', 'first_name': 'Sophie', 'last_name': 'Anderson', 'email': 'sophie.anderson@example.com'},
        {'username': 'ryan_thomas', 'first_name': 'Ryan', 'last_name': 'Thomas', 'email': 'ryan.thomas@example.com'},
        {'username': 'lucy_jackson', 'first_name': 'Lucy', 'last_name': 'Jackson', 'email': 'lucy.jackson@example.com'},
        {'username': 'adam_white', 'first_name': 'Adam', 'last_name': 'White', 'email': 'adam.white@example.com'},
        {'username': 'emily_harris', 'first_name': 'Emily', 'last_name': 'Harris', 'email': 'emily.harris@example.com'},
        {'username': 'daniel_martin', 'first_name': 'Daniel', 'last_name': 'Martin', 'email': 'daniel.martin@example.com'},
        {'username': 'jessica_thompson', 'first_name': 'Jessica', 'last_name': 'Thompson', 'email': 'jessica.thompson@example.com'},
        {'username': 'matthew_garcia', 'first_name': 'Matthew', 'last_name': 'Garcia', 'email': 'matthew.garcia@example.com'},
        {'username': 'charlotte_martinez', 'first_name': 'Charlotte', 'last_name': 'Martinez', 'email': 'charlotte.martinez@example.com'},
        {'username': 'joshua_robinson', 'first_name': 'Joshua', 'last_name': 'Robinson', 'email': 'joshua.robinson@example.com'},
        {'username': 'amelia_clark', 'first_name': 'Amelia', 'last_name': 'Clark', 'email': 'amelia.clark@example.com'},
        {'username': 'andrew_rodriguez', 'first_name': 'Andrew', 'last_name': 'Rodriguez', 'email': 'andrew.rodriguez@example.com'},
        {'username': 'mia_lewis', 'first_name': 'Mia', 'last_name': 'Lewis', 'email': 'mia.lewis@example.com'},
        {'username': 'joseph_lee', 'first_name': 'Joseph', 'last_name': 'Lee', 'email': 'joseph.lee@example.com'},
        {'username': 'grace_walker', 'first_name': 'Grace', 'last_name': 'Walker', 'email': 'grace.walker@example.com'},
        {'username': 'christopher_hall', 'first_name': 'Christopher', 'last_name': 'Hall', 'email': 'christopher.hall@example.com'},
        {'username': 'lily_allen', 'first_name': 'Lily', 'last_name': 'Allen', 'email': 'lily.allen@example.com'},
        {'username': 'thomas_young', 'first_name': 'Thomas', 'last_name': 'Young', 'email': 'thomas.young@example.com'},
        {'username': 'hannah_king', 'first_name': 'Hannah', 'last_name': 'King', 'email': 'hannah.king@example.com'},
        {'username': 'nicholas_wright', 'first_name': 'Nicholas', 'last_name': 'Wright', 'email': 'nicholas.wright@example.com'},
        {'username': 'ava_lopez', 'first_name': 'Ava', 'last_name': 'Lopez', 'email': 'ava.lopez@example.com'},
        {'username': 'william_hill', 'first_name': 'William', 'last_name': 'Hill', 'email': 'william.hill@example.com'},
        {'username': 'isabella_scott', 'first_name': 'Isabella', 'last_name': 'Scott', 'email': 'isabella.scott@example.com'},
        {'username': 'alexander_green', 'first_name': 'Alexander', 'last_name': 'Green', 'email': 'alexander.green@example.com'},
        {'username': 'ella_adams', 'first_name': 'Ella', 'last_name': 'Adams', 'email': 'ella.adams@example.com'},
        {'username': 'benjamin_baker', 'first_name': 'Benjamin', 'last_name': 'Baker', 'email': 'benjamin.baker@example.com'},
        {'username': 'chloe_nelson', 'first_name': 'Chloe', 'last_name': 'Nelson', 'email': 'chloe.nelson@example.com'},
        {'username': 'samuel_carter', 'first_name': 'Samuel', 'last_name': 'Carter', 'email': 'samuel.carter@example.com'},
        {'username': 'madison_mitchell', 'first_name': 'Madison', 'last_name': 'Mitchell', 'email': 'madison.mitchell@example.com'},
        {'username': 'jacob_perez', 'first_name': 'Jacob', 'last_name': 'Perez', 'email': 'jacob.perez@example.com'},
        {'username': 'sofia_roberts', 'first_name': 'Sofia', 'last_name': 'Roberts', 'email': 'sofia.roberts@example.com'},
        {'username': 'ethan_turner', 'first_name': 'Ethan', 'last_name': 'Turner', 'email': 'ethan.turner@example.com'},
        {'username': 'evelyn_phillips', 'first_name': 'Evelyn', 'last_name': 'Phillips', 'email': 'evelyn.phillips@example.com'},
        {'username': 'logan_campbell', 'first_name': 'Logan', 'last_name': 'Campbell', 'email': 'logan.campbell@example.com'},
        {'username': 'scarlett_parker', 'first_name': 'Scarlett', 'last_name': 'Parker', 'email': 'scarlett.parker@example.com'},
        {'username': 'nathan_evans', 'first_name': 'Nathan', 'last_name': 'Evans', 'email': 'nathan.evans@example.com'},
        {'username': 'aria_edwards', 'first_name': 'Aria', 'last_name': 'Edwards', 'email': 'aria.edwards@example.com'},
        {'username': 'owen_collins', 'first_name': 'Owen', 'last_name': 'Collins', 'email': 'owen.collins@example.com'},
        {'username': 'victoria_stewart', 'first_name': 'Victoria', 'last_name': 'Stewart', 'email': 'victoria.stewart@example.com'},
        {'username': 'jack_morris', 'first_name': 'Jack', 'last_name': 'Morris', 'email': 'jack.morris@example.com'},
        {'username': 'zoey_rogers', 'first_name': 'Zoey', 'last_name': 'Rogers', 'email': 'zoey.rogers@example.com'},
        {'username': 'henry_reed', 'first_name': 'Henry', 'last_name': 'Reed', 'email': 'henry.reed@example.com'},
        {'username': 'penelope_cook', 'first_name': 'Penelope', 'last_name': 'Cook', 'email': 'penelope.cook@example.com'},
        {'username': 'luke_morgan', 'first_name': 'Luke', 'last_name': 'Morgan', 'email': 'luke.morgan@example.com'},
    ]
    
    created_customers = []
    for customer_data in customers_data:
        customer = User.objects.create_user(
            username=customer_data['username'],
            email=customer_data['email'],
            first_name=customer_data['first_name'],
            last_name=customer_data['last_name'],
            password='customer123'
        )
        created_customers.append(customer)
        print(f"   [+] Created: {customer.get_full_name()} ({customer.username})")
    
    print(f"\n   Created {len(created_customers)} customers")
    print("\n" + "=" * 60)
    
    return created_customers


def create_reviews_and_orders(customers):
    """Create 100 orders with reviews, distributed among existing customers"""
    import random
    from decimal import Decimal
    from datetime import timedelta, datetime
    from django.utils import timezone
    
    print("\n" + "=" * 60)
    print("Creating Orders and Reviews...")
    print("=" * 60)
    
    # Date range: January 1, 2025 to today (December 15, 2025)
    start_date = datetime(2025, 1, 1, tzinfo=timezone.get_current_timezone())
    end_date = timezone.now()
    date_range_days = (end_date - start_date).days
    
    # Get online products only
    products = list(Product.objects.filter(is_online=True, available=True))
    
    if len(products) < 200:
        print(f"   Warning: Only {len(products)} products available")
    
    # Review templates
    positive_reviews = [
        ("Excellent Quality", "This product exceeded my expectations. Very well made and works perfectly. Would definitely recommend to others."),
        ("Great Value", "Amazing value for money! The quality is outstanding and it does exactly what I needed. Very satisfied with this purchase."),
        ("Highly Recommended", "I'm very impressed with this product. It's durable, reliable, and easy to use. One of the best purchases I've made."),
        ("Perfect for the Job", "This tool is perfect for what I needed. Good quality construction and works brilliantly. Very happy customer!"),
        ("Fantastic Product", "Really fantastic product! Exactly as described and performs wonderfully. Will definitely buy from this shop again."),
        ("Love It!", "Absolutely love this product! It's made my work so much easier. Great quality and brilliant value."),
    ]
    
    neutral_reviews = [
        ("It's OK", "The product is decent for the price. It does the job but nothing special. Would be nice if it had better quality materials."),
        ("Average Quality", "Average product overall. Works as expected but build quality could be better. It's acceptable for occasional use."),
    ]
    
    negative_reviews = [
        ("Disappointed", "Unfortunately, this product didn't meet my expectations. The quality isn't great and it feels quite flimsy. Expected better."),
        ("Not Great", "Not very impressed with this purchase. It works but the quality is poor. Wouldn't buy again at this price."),
    ]
    
    total_reviews = 0
    total_orders = 0
    total_order_items = 0
    total_sales = 0
    
    # Create 500 orders (average 10 per customer)
    orders_to_create = 500
    
    for order_num in range(orders_to_create):
        # Randomly select a customer (users can have multiple orders)
        customer = random.choice(customers)
        
        # Randomly select 3-8 products for this order
        num_products = random.randint(3, 8)
        order_products = random.sample(products, min(num_products, len(products)))
        
        # Create order for this customer
        order_date = start_date + timedelta(days=random.randint(0, date_range_days))
        order = Order.objects.create(
            user=customer,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            address=f"{random.randint(1, 999)} {random.choice(['High Street', 'Main Road', 'Park Avenue', 'Church Lane', 'Station Road'])}",
            postal_code=f"{random.choice(['SW', 'SE', 'NW', 'NE', 'EC', 'WC'])}{random.randint(1, 20)} {random.randint(1, 9)}{random.choice(['AA', 'AB', 'XX', 'YY'])}",
            city=random.choice(['London', 'Manchester', 'Birmingham', 'Leeds', 'Liverpool', 'Bristol', 'Sheffield', 'Newcastle', 'Glasgow', 'Edinburgh']),
            paid=True,
            created=order_date
        )
        total_orders += 1
        
        for product in order_products:
            # Determine rating (60% positive, 20% neutral, 20% negative)
            rand = random.random()
            if rand < 0.6:  # 60% positive (4-5 stars)
                rating = random.choice([4, 5])
                title, comment = random.choice(positive_reviews)
            elif rand < 0.8:  # 20% neutral (3 stars)
                rating = 3
                title, comment = random.choice(neutral_reviews)
            else:  # 20% negative (1-2 stars)
                rating = random.choice([1, 2])
                title, comment = random.choice(negative_reviews)
            
            # Create review for 75% of purchased products (realistic - not everyone reviews)
            # Only if customer hasn't reviewed this product yet
            should_review = random.random() < 0.75
            existing_review = ProductReview.objects.filter(product=product, user=customer).exists()
            
            if should_review and not existing_review:
                ProductReview.objects.create(
                    product=product,
                    user=customer,
                    rating=rating,
                    title=title,
                    comment=comment,
                    verified_purchase=True,
                    created=order.created + timedelta(days=random.randint(1, 14))
                )
                total_reviews += 1
            
            # Create order item
            quantity = random.choice([1, 1, 1, 1, 2, 2, 3])  # Mostly 1, occasionally 2-3
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=quantity
            )
            total_order_items += 1
            
            # Create corresponding Sale record
            Sale.objects.create(
                order=order,
                category=product.category,
                item=product,
                sold_price=product.price,
                quantity=quantity,
                date=order.created
            )
            total_sales += 1
    
    print(f"\n   Created {total_reviews} reviews")
    print(f"   Created {total_orders} orders")
    print(f"   Created {total_order_items} order items")
    print(f"   Created {total_sales} sales records")
    print("\n" + "=" * 60)


if __name__ == '__main__':
    restore_database()
