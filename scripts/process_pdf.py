#!/usr/bin/env python3
"""
TOM CITY EDITION - PDF PROCESSOR (v3.1)
=======================================
1. Converts PDF to Images
2. Creates Edition Folder
3. Generates WhatsApp Preview (Max 200KB JPG)
4. Updates app.js automatically
"""

import os
import sys
import shutil
import glob
import re
import datetime
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont

# ===================================
# CONFIGURATION
# ===================================

UPLOADS_DIR = "uploads"
PAPERS_DIR = "papers"
ASSETS_DIR = "assets"
APP_JS_FILE = "app.js"
THEME_COLOR = "#2f96f0"  # Tom City Blue

# ===================================
# MAIN LOGIC
# ===================================

def main():
    print("🚀 Starting Tom City Processor...")
    
    # 1. Find Uploaded PDF
    pdfs = glob.glob(os.path.join(UPLOADS_DIR, "*.pdf"))
    if not pdfs:
        print("❌ No PDF found in uploads/")
        return

    pdf_path = pdfs[0]
    filename = os.path.basename(pdf_path)
    
    # Extract Date from filename (DD-MM-YYYY)
    match = re.search(r"(\d{2}-\d{2}-\d{4})", filename)
    if not match:
        print("❌ Filename must be DD-MM-YYYY.pdf")
        return
        
    date_str = match.group(1)
    print(f"📅 Processing Edition: {date_str}")
    
    # 2. Create Edition Folder
    edition_dir = os.path.join(PAPERS_DIR, date_str)
    os.makedirs(edition_dir, exist_ok=True)
    
    # Move PDF to edition folder
    final_pdf_path = os.path.join(edition_dir, "full.pdf")
    shutil.copy(pdf_path, final_pdf_path)
    
    # 3. Convert Pages to Images
    print("📸 Converting PDF pages to Images...")
    # Lower DPI slightly for speed/size (150 is good for screens)
    images = convert_from_path(final_pdf_path, dpi=150, fmt="png")
    
    total_pages = len(images)
    
    # Save each page
    for i, img in enumerate(images):
        page_num = i + 1
        img_path = os.path.join(edition_dir, f"{page_num}.png")
        img.save(img_path, "PNG", optimize=True)
        print(f"   - Saved Page {page_num}")

    # 4. Generate WhatsApp Preview Card (Strict 200KB Limit)
    print("🎨 Generating WhatsApp Preview Card...")
    preview_path = os.path.join(edition_dir, "preview.jpg")
    generate_preview_card(images[0], preview_path, date_str)
    
    # Copy preview to assets for global link sharing
    global_preview = os.path.join(ASSETS_DIR, "latest-cover.jpg")
    shutil.copy(preview_path, global_preview)

    # 5. Update app.js
    update_app_js(date_str, total_pages)
    
    # 6. Cleanup
    os.remove(pdf_path)
    print("✅ Done! PDF processed and Website updated.")

# ===================================
# PREVIEW GENERATOR (The Magic Part)
# ===================================

def generate_preview_card(first_page_img, output_path, date_text):
    """
    Creates a styled social media poster:
    [ HEADER: Date | Tom City Edition ]
    [       BIG IMAGE OF PAGE 1       ]
    [ FOOTER: Read at tom-city.in     ]
    
    * STRICTLY enforces < 200KB file size
    """
    
    # 1. Setup Canvas
    card_w, card_h = 800, 1000
    card = Image.new("RGB", (card_w, card_h), "white")
    draw = ImageDraw.Draw(card)
    
    # 2. Try to load fonts
    try:
        font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except:
        font_lg = ImageFont.load_default()
        font_sm = ImageFont.load_default()

    # 3. Draw Header (Blue Box)
    header_h = 120
    draw.rectangle([(0, 0), (card_w, header_h)], fill=THEME_COLOR)
    draw.text((card_w/2, 60), f"🗓 {date_text}", font=font_lg, fill="white", anchor="mm")
    
    # 4. Process Page 1 Image
    target_w = 700
    aspect_ratio = first_page_img.height / first_page_img.width
    target_h = int(target_w * aspect_ratio)
    
    # Cap height
    max_paper_h = 750
    if target_h > max_paper_h:
        target_h = max_paper_h
        target_w = int(target_h / aspect_ratio)
        
    paper_resized = first_page_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Draw paper with border
    paper_x = (card_w - target_w) // 2
    paper_y = header_h + 30
    draw.rectangle([(paper_x-2, paper_y-2), (paper_x+target_w+2, paper_y+target_h+2)], fill="#cccccc")
    card.paste(paper_resized, (paper_x, paper_y))
    
    # 5. Draw Footer
    footer_y = card_h - 50
    draw.rectangle([(0, card_h - 100), (card_w, card_h)], fill="#222222")
    draw.text((card_w/2, footer_y), "🔗 Read Full News: tom-city-edition.in", font=font_sm, fill="white", anchor="mm")

    # 6. Save with Size Check (Max 200KB Loop)
    quality = 95
    while True:
        card.save(output_path, "JPEG", quality=quality, optimize=True)
        file_size_kb = os.path.getsize(output_path) / 1024
        
        if file_size_kb <= 200:
            print(f"   - Preview saved: {file_size_kb:.1f}KB (Quality: {quality})")
            break
            
        # If too big, lower quality and try again
        print(f"   - File too big ({file_size_kb:.1f}KB). Compressing...")
        quality -= 5
        
        if quality < 10: # Safety break
            break

# ===================================
# APP.JS UPDATER
# ===================================

def update_app_js(date_key, total_pages):
    try:
        with open(APP_JS_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if entry already exists
        if f'"{date_key}":' in content:
            print(f"⚠️ Entry for {date_key} already exists. Updating...")
            pattern = rf'"{date_key}": \{{ pages: \d+, pdf: "full\.pdf" \}},'
            replacement = f'"{date_key}": {{ pages: {total_pages}, pdf: "full.pdf" }},'
            new_content = re.sub(pattern, replacement, content)
        else:
            print(f"✨ Adding new entry for {date_key}")
            marker = "// ROBOT_ENTRY_POINT"
            new_entry = f'    "{date_key}": {{ pages: {total_pages}, pdf: "full.pdf" }},'
            new_content = content.replace(marker, marker + "\n" + new_entry)

        with open(APP_JS_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
            
    except Exception as e:
        print(f"❌ Error updating app.js: {e}")

if __name__ == "__main__":
    main()