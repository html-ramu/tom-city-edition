#!/usr/bin/env python3
"""
TOM CITY EDITION - CLEAN PREVIEW PROCESSOR
==========================================
1. Converts PDF to Images
2. CROPS the Top Headlines for WhatsApp (No borders, No text added)
3. Updates app.js & index.html
"""

import os
import sys
import shutil
import glob
import re
from pdf2image import convert_from_path
from PIL import Image

# ===================================
# CONFIGURATION
# ===================================

UPLOADS_DIR = "uploads"
PAPERS_DIR = "papers"
ASSETS_DIR = "assets"
APP_JS_FILE = "app.js"
INDEX_FILE = "index.html"

# ===================================
# MAIN LOGIC
# ===================================

def main():
    print("🚀 Starting Clean-Paper Processor...")
    
    # 1. Find Uploaded PDF
    pdfs = glob.glob(os.path.join(UPLOADS_DIR, "*.pdf"))
    if not pdfs:
        print("❌ No PDF found in uploads/")
        return

    pdf_path = pdfs[0]
    filename = os.path.basename(pdf_path)
    
    # Extract Date
    match = re.search(r"(\d{2}-\d{2}-\d{4})", filename)
    if not match:
        print("❌ Filename must be DD-MM-YYYY.pdf")
        return
        
    date_str = match.group(1)
    print(f"📅 Processing Edition: {date_str}")
    
    # 2. Create Edition Folder
    edition_dir = os.path.join(PAPERS_DIR, date_str)
    os.makedirs(edition_dir, exist_ok=True)
    
    # Move PDF
    final_pdf_path = os.path.join(edition_dir, "full.pdf")
    shutil.copy(pdf_path, final_pdf_path)
    
    # 3. Convert Pages
    print("📸 Converting PDF pages...")
    images = convert_from_path(final_pdf_path, dpi=150, fmt="png")
    total_pages = len(images)
    
    for i, img in enumerate(images):
        page_num = i + 1
        img.save(os.path.join(edition_dir, f"{page_num}.png"), "PNG", optimize=True)

    # 4. Generate CLEAN PREVIEW (Crop Top Headlines)
    print("🎨 Generating WhatsApp Preview (Headlines Only)...")
    preview_path = os.path.join(edition_dir, "preview.jpg")
    generate_clean_preview(images[0], preview_path)
    
    # Copy to assets for global sharing
    global_preview = os.path.join(ASSETS_DIR, "latest-cover.jpg")
    shutil.copy(preview_path, global_preview)

    # 5. Update app.js
    update_app_js(date_str, total_pages)

    # 6. Update index.html (Force WhatsApp Refresh)
    update_index_html(date_str)
    
    # 7. Cleanup
    os.remove(pdf_path)
    print("✅ Done! Headlines Preview Ready.")

# ===================================
# PREVIEW GENERATOR (CROP LOGIC)
# ===================================

def generate_clean_preview(first_page_img, output_path):
    """
    Crops the top part of the newspaper to fit WhatsApp (1.91:1 Ratio).
    No borders, no extra text. Just the paper.
    """
    img_w, img_h = first_page_img.size

    # WhatsApp Standard Ratio is 1.91:1
    # We calculate the height needed for the full width
    target_height = int(img_w / 1.91)

    # Crop the top rectangle (Left, Top, Right, Bottom)
    # This takes the full width, but cuts off the bottom to make it landscape
    crop_img = first_page_img.crop((0, 0, img_w, target_height))

    # Resize to exactly 1200x630 for WhatsApp consistency
    final_preview = crop_img.resize((1200, 630), Image.Resampling.LANCZOS)

    # Save with compression (Max 200KB)
    quality = 95
    while True:
        final_preview.save(output_path, "JPEG", quality=quality, optimize=True)
        size_kb = os.path.getsize(output_path) / 1024
        
        if size_kb <= 200:
            print(f"   - Preview saved: {size_kb:.1f}KB (Quality: {quality})")
            break
        
        quality -= 5
        if quality < 15: break

# ===================================
# UPDATERS
# ===================================

def update_app_js(date_key, total_pages):
    try:
        with open(APP_JS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            
        if f'"{date_key}":' in content:
            # Update existing
            pattern = rf'"{date_key}": \{{ pages: \d+, pdf: "full\.pdf" \}},'
            replacement = f'"{date_key}": {{ pages: {total_pages}, pdf: "full.pdf" }},'
            new_content = re.sub(pattern, replacement, content)
        else:
            # Add new
            marker = "// ROBOT_ENTRY_POINT"
            new_entry = f'    "{date_key}": {{ pages: {total_pages}, pdf: "full.pdf" }},'
            new_content = content.replace(marker, marker + "\n" + new_entry)
            
        with open(APP_JS_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        print(f"Error updating app.js: {e}")

def update_index_html(date_str):
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Forces WhatsApp to see new image by changing ?v=DATE
        pattern = r"assets/latest-cover\.jpg\?v=[0-9-]+"
        replacement = f"assets/latest-cover.jpg?v={date_str}"
        
        new_content = re.sub(pattern, replacement, content)
        
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
    except Exception as e:
        print(f"Error updating index.html: {e}")

if __name__ == "__main__":
    main()