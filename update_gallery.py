#!/usr/bin/env python3
import os
import re
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "index.html")
IMAGES_DIR = os.path.join(BASE_DIR, "Images")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff", ".JPG", ".JPEG", ".PNG"}

GALLERY_SECTIONS = [
    {"id": "experimental", "folder": "experimental"},
    {"id": "traditional",  "folder": "traditional"},
    {"id": "darkroom",     "folder": "darkroom"},
    {"id": "color",        "folder": "color"},
]

THUMBNAIL_SECTIONS = [
    {"id": "composites",     "folder": "digitalart",     "label": "Composites & Digital Works"},
    {"id": "inthesameworld", "folder": "inthesameworld", "label": "In The Same World"},
]

HERO_NAMES = ["hero.jpg", "hero.jpeg", "hero.png", "hero.JPG", "hero.JPEG", "hero.PNG"]

ALL_SECTIONS = [
    {"id": "experimental", "folder": "experimental"},
    {"id": "traditional",  "folder": "traditional"},
    {"id": "darkroom",     "folder": "darkroom"},
    {"id": "color",        "folder": "color"},
    {"id": "digitalart",   "folder": "digitalart"},
]


def find_hero(folder_path):
    for name in HERO_NAMES:
        if os.path.isfile(os.path.join(folder_path, name)):
            return name
    return None


def update_heroes(html):
    for sec in ALL_SECTIONS:
        folder_path = os.path.join(IMAGES_DIR, sec["folder"])
        hero_file = find_hero(folder_path)
        div_id = f"hero-{sec['id']}"
        if hero_file:
            hero_url = f"Images/{sec['folder']}/{hero_file}"
            replacement = (
                f'<div id="{div_id}" class="page-hero has-hero" '
                f'style="background-image: url(\'{hero_url}\')">'
            )
            print(f"  hero for {sec['id']}: {hero_file}")
        else:
            replacement = f'<div id="{div_id}" class="page-hero">'
        pattern = rf'<div id="{re.escape(div_id)}"[^>]*>'
        html, count = re.subn(pattern, replacement, html)
        if count == 0:
            print(f"  warning: Hero div 'id={div_id}' not found - skipped.")
    return html


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
        images = [fn for fn in ordered if fn in existing and fn.lower() not in {h.lower() for h in HERO_NAMES}]
        in_order = set(images)
        extras = sorted(
            [fn for fn in existing if fn not in in_order
             and os.path.splitext(fn)[1] in IMAGE_EXTS
             and fn.lower() not in {h.lower() for h in HERO_NAMES}],
            key=natural_sort_key,
        )
        if extras:
            print(f"  warning: New files not in sort_order.txt (appended): {extras}")
            images += extras
    else:
        all_files = os.listdir(folder_path)
        images = sorted(
            [fn for fn in all_files
             if os.path.splitext(fn)[1] in IMAGE_EXTS
             and fn.lower() not in {h.lower() for h in HERO_NAMES}],
            key=natural_sort_key,
        )
    return images


def build_gallery_block(section_id, images, folder):
    lines = [f"      <!-- GALLERY:{section_id} START -->"]
    for fn in images:
        path = f"Images/{folder}/{fn}"
        lines.append(f'      <div class="gallery-item">')
        lines.append(f'        <img src="{path}" alt="{section_id} - {fn}">')
        lines.append(f'      </div>')
    lines.append(f"      <!-- GALLERY:{section_id} END -->")
    return "\n".join(lines)


def build_thumbnail_block(section_id, images, folder, label):
    lines = [f"      <!-- GALLERY:{section_id} START -->"]
    if images:
        for fn in images:
            path = f"Images/{folder}/{fn}"
            if section_id == "inthesameworld":
                lines.append(f'      <div class="itsw-item" onclick="openLightbox(\'{path}\')">')
                lines.append(f'        <img src="{path}" alt="{label} - {fn}">')
                lines.append(f'      </div>')
            else:
                lines.append(f'      <div class="thumbnail-item" onclick="openLightbox(\'{path}\')">')
                lines.append(f'        <img src="{path}" alt="{label} - {fn}">')
                lines.append(f'      </div>')
    else:
        lines.append('      <p style="color:#999;font-style:italic;padding:2rem 0;">Images coming soon.</p>')
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
        print(f"  warning: No markers found for section '{section_id}' - skipped.")
    return new_html


def main():
    auto_push = True  # Always push by default

    # Clean up any stuck git lock files
    import time
    lock_file = os.path.join(BASE_DIR, ".git", "index.lock")
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
            time.sleep(1)
            print("  Cleaned up git lock file")
        except:
            pass

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    print("Galleries:")
    for sec in GALLERY_SECTIONS:
        folder_path = os.path.join(IMAGES_DIR, sec["folder"])
        images = get_images(folder_path)
        print(f"  {sec['id']}: {len(images)} image(s)")
        block = build_gallery_block(sec["id"], images, sec["folder"])
        html = replace_block(html, sec["id"], block)

    print("Digital Art:")
    for sec in THUMBNAIL_SECTIONS:
        folder_path = os.path.join(IMAGES_DIR, sec["folder"])
        images = get_images(folder_path)
        print(f"  {sec['id']}: {len(images)} image(s)")
        block = build_thumbnail_block(sec["id"], images, sec["folder"], sec["label"])
        html = replace_block(html, sec["id"], block)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("\n✅  index.html updated.")

    if auto_push:
        print("\n📤  Pushing to GitHub...")
        try:
            subprocess.run(["git", "-C", BASE_DIR, "add", "."], check=True)
            subprocess.run(["git", "-C", BASE_DIR, "commit", "-m", "Auto-update galleries"], check=True)
            subprocess.run(["git", "-C", BASE_DIR, "push", "origin", "main"], check=True)
            print("🚀  Pushed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌  Error pushing: {e}")


if __name__ == "__main__":
    main()