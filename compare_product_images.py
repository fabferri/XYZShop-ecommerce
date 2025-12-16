"""
Compare Product Images Script
This script compares images in media/products folder with the list in product_images_list.txt
and identifies any mismatches (new images or missing images).
"""

import os

def compare_images():
    """Compare actual images with the stored list"""
    
    # Define paths
    media_path = os.path.join('media', 'products')
    list_file = 'product_images_list.txt'
    output_file = 'image_differences.txt'
    
    print("=" * 60)
    print("Comparing product images with stored list...")
    print("=" * 60)
    
    # Check if directories and files exist
    if not os.path.exists(media_path):
        print(f"ERROR: Directory '{media_path}' not found!")
        return
    
    if not os.path.exists(list_file):
        print(f"ERROR: File '{list_file}' not found!")
        print("Run extract_product_images.py first to create the list.")
        return
    
    # Get current images from folder
    try:
        files = os.listdir(media_path)
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        current_images = set([f for f in files if f.lower().endswith(image_extensions)])
        
        print(f"Found {len(current_images)} images in media folder")
        
        # Read stored list
        stored_images = set()
        with open(list_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip header lines and empty lines
                if line and not line.startswith('Product Images') and not line.startswith('Total Images') and not line.startswith('Generated') and not line.startswith('='):
                    stored_images.add(line)
        
        print(f"Found {len(stored_images)} images in stored list")
        print()
        
        # Find differences
        new_images = current_images - stored_images  # In folder but not in list
        missing_images = stored_images - current_images  # In list but not in folder
        
        # Display and save results
        has_differences = bool(new_images or missing_images)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Product Images Comparison Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Images in folder: {len(current_images)}\n")
            f.write(f"Images in list: {len(stored_images)}\n")
            f.write(f"New images: {len(new_images)}\n")
            f.write(f"Missing images: {len(missing_images)}\n\n")
            
            if new_images:
                f.write("NEW IMAGES (in folder but not in list):\n")
                f.write("-" * 60 + "\n")
                for img in sorted(new_images):
                    f.write(f"  + {img}\n")
                f.write("\n")
            
            if missing_images:
                f.write("MISSING IMAGES (in list but not in folder):\n")
                f.write("-" * 60 + "\n")
                for img in sorted(missing_images):
                    f.write(f"  - {img}\n")
                f.write("\n")
            
            if not has_differences:
                f.write("No differences found - all images match!\n")
        
        # Console output
        if new_images:
            print(f"NEW IMAGES (in folder but not in list): {len(new_images)}")
            print("-" * 60)
            for img in sorted(new_images):
                print(f"  + {img}")
            print()
        
        if missing_images:
            print(f"MISSING IMAGES (in list but not in folder): {len(missing_images)}")
            print("-" * 60)
            for img in sorted(missing_images):
                print(f"  - {img}")
            print()
        
        print("=" * 60)
        if has_differences:
            print(f"Found {len(new_images)} new and {len(missing_images)} missing images")
            print(f"Detailed report saved to: {output_file}")
        else:
            print("No differences found - all images match!")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == '__main__':
    compare_images()
