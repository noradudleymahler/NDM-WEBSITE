#!/usr/bin/env python3
import os
import re
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "index.html")
IMAGES_DIR = os.path.join(BASE_DIR, "Images")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff", ".JPG", ".JPEG", ".PNG"}

PAGES_WITH_SUBFOLDERS = {
    "experimental": ["PINHOLE & SILVERING", "UV PRINTS"],
    "darkroom": ["SMARTPHONE DARKROOM PRINTING", "SUPERIMPOSING & DOUBLE EXPOSURES"],
    "color": ["COLOR FILM", "DIGITAL"],
    "traditional": []
}

THUMBNAIL_SECTIONS = [
    {"id": "composites", "folder": "digitalart", "label": "Composites & Digital Works"},
    {"id": "inthesameworld", "folder": "inthesameworld", "label": "In The Same World"},
]


def natural_sort_key(name):
    parts = re.split(r"(\d+)", name)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def get_images(folder_path):
    if not os.path.isdir(folder_path):
        return []
    sort_file = os.path.join(folder_path, "sort_order.txt")
    if os.path.isfile(sort_file):
        with open(sort_file) as f:
            ordered = [line.strip() for line in f if line.strip()]
        existing = set(os.listdir(folder_path))
        images = [fn for fn in ordered if fn in existing and os.path.splitext(fn)[1] in IMAGE_EXTS]
        in_order = set(images)
        extras = sorted(
            [fn for fn in existing if fn not in in_order and os.path.splitext(fn)[1] in IMAGE_EXTS],
            key=natural_sort_key,
        )
        if extras:
            print(f"  New files in {folder_path}: {extras}")
            images += extras
    else:
        all_files = os.listdir(folder_path)
        images = sorted(
            [fn for fn in all_files if os.path.splitext(fn)[1] in IMAGE_EXTS],
            key=natural_sort_key,
        )
    return images


def build_gallery_block(section_id, images, folder):
    lines = [f"      <!-- GALLERY:{section_id} START -->"]
    for fn in images:
        path = f"Images/{folder}/{fn}"
        lines.append(f'      <div class="gallery-item"><img src="{path}" alt="{section_id} - {fn}"></div>')
    lines.append(f"      <!-- GALLERY:{section_id} END -->")
    return "\n".join(lines)


def build_thumbnail_block(section_id, images, folder, label):
    lines = [f"      <!-- GALLERY:{section_id} START -->"]
    for fn in images:
        path = f"Images/{folder}/{fn}"
        if section_id == "inthesameworld":
            lines.append(f'      <div class="itsw-item" onclick="openLightbox(\'{path}\')"><img src="{path}" alt="{label} - {fn}"></div>')
        else:
            lines.append(f'      <div class="thumbnail-item" onclick="openLightbox(\'{path}\')"><img src="{path}" alt="{label} - {fn}"></div>')
    lines.append(f"      <!-- GALLERY:{section_id} END -->")
    return "\n".join(lines)


def replace_block(html, section_id, new_block):
    pattern = (
        rf"([ \t]*<!-- GALLERY:{re.escape(section_id)} START -->)"
        rf".*?"
        rf"([ \t]*<!-- GALLERY:{re.escape(section_id)} END -->)"
    )
    new_html, count = re.subn(pattern, new_block, html, flags=re.DOTALL)
    if count == 0:
        print(f"  Warning: No markers found for '{section_id}'")
    return new_html


def main():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    print("Processing galleries...")

    # Handle pages with subfolders
    for page_id, subfolders in PAGES_WITH_SUBFOLDERS.items():
        if subfolders:
            for subfolder in subfolders:
                folder_path = os.path.join(IMAGES_DIR, page_id, subfolder)
                images = get_images(folder_path)
                gallery_id = subfolder.lower().replace(" & ", "-").replace(" ", "-")
                print(f"  {page_id}/{subfolder}: {len(images)} image(s)")
                block = build_gallery_block(gallery_id, images, f"{page_id}/{subfolder}")
                html = replace_block(html, gallery_id, block)
        else:
            folder_path = os.path.join(IMAGES_DIR, page_id)
            images = get_images(folder_path)
            print(f"  {page_id}: {len(images)} image(s)")
            block = build_gallery_block(page_id, images, page_id)
            html = replace_block(html, page_id, block)

    # Handle digital art subfolders
    for sec in THUMBNAIL_SECTIONS:
        folder_path = os.path.join(IMAGES_DIR, sec["folder"])
        images = get_images(folder_path)
        print(f"  {sec['id']}: {len(images)} image(s)")
        block = build_thumbnail_block(sec["id"], images, sec["folder"], sec["label"])
        html = replace_block(html, sec["id"], block)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("\n✅  index.html updated.")

    if "--push" in sys.argv:
        print("\n📤  Pushing to GitHub...")
        subprocess.run(["git", "-C", BASE_DIR, "add", "."], check=True)
        subprocess.run(["git", "-C", BASE_DIR, "commit", "-m", "Auto-update galleries"], check=True)
        subprocess.run(["git", "-C", BASE_DIR, "push", "origin", "main"], check=True)
        print("🚀  Pushed successfully!")


if __name__ == "__main__":
    main()
