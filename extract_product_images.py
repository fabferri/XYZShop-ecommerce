"""
Extract Product Image Names Script
This script extracts all product image filenames from the media/products folder
and saves them to a text file.
"""

import os

def extract_image_names():
    """Extract all product image filenames and save to file"""
    
    # Define the media folder path
    media_path = os.path.join('media', 'products')
    output_file = 'product_images_list.txt'
    
    print("=" * 60)
    print("Extracting product image filenames...")
    print("=" * 60)
    
    # Check if the directory exists
    if not os.path.exists(media_path):
        print(f"ERROR: Directory '{media_path}' not found!")
        return
    
    # Get all files in the directory
    try:
        files = os.listdir(media_path)
        
        # Filter for image files (jpg, jpeg, png, gif, webp)
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        image_files = [f for f in files if f.lower().endswith(image_extensions)]
        
        # Sort alphabetically
        image_files.sort()
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Product Images List\n")
            f.write(f"Total Images: {len(image_files)}\n")
            f.write(f"Generated: {os.path.basename(__file__)}\n")
            f.write("=" * 60 + "\n\n")
            
            for image_name in image_files:
                f.write(f"{image_name}\n")
        
        print(f"\nFound {len(image_files)} image files")
        print(f"Image list saved to: {output_file}")
        print("=" * 60)
        
        # Display first 10 and last 10 images
        print("\nFirst 10 images:")
        for img in image_files[:10]:
            print(f"  - {img}")
        
        if len(image_files) > 20:
            print("\n...")
            print(f"\nLast 10 images:")
            for img in image_files[-10:]:
                print(f"  - {img}")
        
        print("\n" + "=" * 60)
        print("SUCCESS: Image list extracted and saved")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == '__main__':
    extract_image_names()
