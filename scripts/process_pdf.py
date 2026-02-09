#!/usr/bin/env python3
"""
TOM CITY EDITION - PDF PROCESSOR (IMPROVED)
================================
This script automatically processes uploaded PDF newspapers:
1. Converts PDF pages to PNG images
2. Creates edition folder in papers/
3. Generates WhatsApp preview image
4. Updates app.js with new edition data (or updates existing entry)
5. Updates index.html social meta tags

Built by: html-ramu
Version: 2.0 (Fixed duplicate entry issue)
"""

import os
import sys
import shutil
import subprocess
import glob
import re
from PIL import Image

# ===================================
# CONFIGURATION
# ===================================

UPLOADS_DIR = "uploads"
PAPERS_DIR = "papers"
ASSETS_DIR = "assets"
APP_JS_FILE = "app.js"
INDEX_HTML_FILE = "index.html"
DOMAIN_URL = "https://tom-city-edition.in"

# ===================================
# MAIN PROCESSING FUNCTION
# ===================================

def main():
    """Main processing workflow"""
    print("=" * 50)
    print("TOM CITY EDITION - PDF PROCESSOR v2.0")
    print("=" * 50)
    
    # 1. Find PDF in uploads folder
    pdfs = glob.glob(os.path.join(UPLOADS_DIR, "*.pdf"))
    if not pdfs:
        print("❌ No PDF found in uploads/ folder.")
        print("📝 Please upload a PDF named: DD-MM-YYYY.pdf")
        return

    pdf_path = pdfs[0]
    filename = os.path.basename(pdf_path)
    date_str = filename.replace(".pdf", "")
    
    print(f"\n📰 Processing Edition: {date_str}")
    print(f"📄 PDF File: {filename}")

    # 2. Validate date format
    if not validate_date_format(date_str):
        print(f"❌ Invalid filename format: {filename}")
        print("📝 Please use format: DD-MM-YYYY.pdf (e.g., 08-02-2026.pdf)")
        return

    # 3. Create output directory
    output_dir = os.path.join(PAPERS_DIR, date_str)
    if os.path.exists(output_dir):
        print(f"⚠️  Edition folder already exists. Removing old version...")
        shutil.rmtree(output_dir)
    
    os.makedirs(output_dir)
    print(f"✅ Created folder: {output_dir}")

    # 4. Convert PDF to images
    print("\n🖼️  Converting PDF to images...")
    try:
        convert_pdf_to_images(pdf_path, output_dir)
    except Exception as e:
        print(f"❌ Error converting PDF: {e}")
        return

    # 5. Rename and count images
    generated_images = rename_images(output_dir)
    page_count = len(generated_images)
    print(f"✅ Generated {page_count} page(s)")

    # 6. Create WhatsApp preview
    if generated_images:
        print("\n📱 Creating WhatsApp preview...")
        create_smart_preview(date_str, generated_images[0])

    # 7. Move PDF to target folder
    target_pdf = os.path.join(output_dir, "full.pdf")
    shutil.move(pdf_path, target_pdf)
    print(f"✅ Moved PDF to: {target_pdf}")

    # 8. Update app.js (IMPROVED - handles duplicates)
    print("\n📝 Updating app.js...")
    update_app_js(date_str, page_count)

    # 9. Clean up uploads folder
    cleanup_uploads_folder()

    print("\n" + "=" * 50)
    print("✅ PROCESSING COMPLETE!")
    print("=" * 50)
    print(f"📰 Edition: {date_str}")
    print(f"📄 Pages: {page_count}")
    print(f"📁 Folder: {output_dir}")
    print("🚀 Changes ready to commit and push!")

# ===================================
# HELPER FUNCTIONS
# ===================================

def validate_date_format(date_str):
    """
    Validate date format is DD-MM-YYYY
    Returns: True if valid, False otherwise
    """
    pattern = r'^\d{2}-\d{2}-\d{4}$'
    return bool(re.match(pattern, date_str))

def convert_pdf_to_images(pdf_path, output_dir):
    """
    Convert PDF to PNG images using pdftoppm
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save images
    """
    # Use pdftoppm to convert PDF pages to PNG
    # Output format: page-1.png, page-2.png, etc.
    subprocess.run([
        "pdftoppm",
        "-png",
        "-r", "200",  # 200 DPI for good quality
        pdf_path,
        os.path.join(output_dir, "page")
    ], check=True)

def rename_images(output_dir):
    """
    Rename generated images from page-1.png to 1.png, page-2.png to 2.png, etc.
    Args:
        output_dir: Directory containing images
    Returns:
        List of final image paths
    """
    generated_images = sorted(glob.glob(os.path.join(output_dir, "*.png")))
    final_images = []
    
    for i, img_path in enumerate(generated_images):
        new_name = f"{i+1}.png"
        new_path = os.path.join(output_dir, new_name)
        os.rename(img_path, new_path)
        final_images.append(new_path)
    
    return final_images

def create_smart_preview(date_str, source_image_path):
    """
    Create optimized preview image for WhatsApp/social sharing
    - Crops top 45% of first page
    - Converts to JPG for better compression
    - Optimizes to ~200KB for fast loading
    
    Args:
        date_str: Edition date (DD-MM-YYYY)
        source_image_path: Path to first page image
    """
    target_cover = os.path.join(ASSETS_DIR, "latest-cover.jpg")
    
    try:
        with Image.open(source_image_path) as img:
            width, height = img.size
            
            # Crop top 45% (newspaper header and main story)
            crop_height = int(height * 0.45)
            cropped_img = img.crop((0, 0, width, crop_height))
            
            # Convert to RGB (required for JPG)
            cropped_img = cropped_img.convert("RGB")
            
            # Save with optimization
            # Quality=70 ensures size is small but clear
            cropped_img.save(target_cover, "JPEG", optimize=True, quality=70)
            
            print(f"✅ Created WhatsApp preview (Top 45% crop, optimized JPG)")
    
    except Exception as e:
        print(f"⚠️  Warning: Could not create preview image: {e}")
        return

    # Update index.html social tags
    update_social_tags(date_str)

def update_social_tags(date_str):
    """
    Update og:image meta tag in index.html
    Args:
        date_str: Edition date for cache busting
    """
    try:
        with open(INDEX_HTML_FILE, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Create new image URL with version parameter for cache busting
        new_image_url = f"{DOMAIN_URL}/assets/latest-cover.jpg?v={date_str}"
        
        # Regex to replace og:image content
        pattern_og = r'(<meta property="og:image" content=")(.*?)(")'
        
        if re.search(pattern_og, html_content):
            new_content = re.sub(pattern_og, r'\1' + new_image_url + r'\3', html_content)
            
            with open(INDEX_HTML_FILE, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print(f"✅ Updated index.html og:image tag")
        else:
            print("⚠️  Warning: Could not find og:image meta tag in index.html")
    
    except Exception as e:
        print(f"⚠️  Warning: Could not update social tags: {e}")

def update_app_js(date_key, pages):
    """
    Add or update edition entry in app.js
    IMPROVED: Removes duplicate entries and updates existing ones
    
    Args:
        date_key: Edition date (DD-MM-YYYY)
        pages: Number of pages in edition
    """
    try:
        with open(APP_JS_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Create new entry
        new_entry = f'    "{date_key}": {{ pages: {pages}, pdf: "full.pdf" }},'
        marker = "// ROBOT_ENTRY_POINT"

        # Check if marker exists
        if marker not in content:
            print(f"❌ Error: ROBOT_ENTRY_POINT marker not found in {APP_JS_FILE}")
            return

        # Check if entry already exists and remove it
        entry_exists = f'"{date_key}"' in content
        
        if entry_exists:
            # Remove old entry using regex
            # Pattern matches: "DD-MM-YYYY": { pages: X, pdf: "full.pdf" },
            pattern = rf'    "{re.escape(date_key)}": \{{ pages: \d+, pdf: "full\.pdf" \}},?\n?'
            content = re.sub(pattern, '', content)
            print(f"🔄 Updating existing entry for {date_key}")
        else:
            print(f"✅ Adding new entry for {date_key}")
        
        # Insert new entry after marker
        new_content = content.replace(marker, marker + "\n" + new_entry)
        
        with open(APP_JS_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"✅ Successfully updated app.js")
    
    except Exception as e:
        print(f"❌ Error updating app.js: {e}")

def cleanup_uploads_folder():
    """
    Clean up uploads folder after processing
    Removes all files except .gitkeep
    """
    try:
        for file in os.listdir(UPLOADS_DIR):
            if file != ".gitkeep":
                file_path = os.path.join(UPLOADS_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        print("✅ Cleaned uploads folder")
    except Exception as e:
        print(f"⚠️  Warning: Could not clean uploads folder: {e}")

# ===================================
# RUN SCRIPT
# ===================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)