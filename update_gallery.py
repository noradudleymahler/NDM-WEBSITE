#!/usr/bin/env python3
"""
update_gallery.py
-----------------
Scans each Images/<section>/ folder and rewrites the matching gallery
blocks in index.html.  Run this any time you add, remove, or reorder images.

Usage:
    python3 update_gallery.py          # update index.html
    python3 update_gallery.py --push   # update + git add/commit/push automatically

Ordering:
  - If a folder contains sort_order.txt, images appear in that order.
  - Otherwise images are sorted naturally (1.jpg, 2.jpg … 10.jpg …).
  - To reorder: just edit sort_order.txt (one filename per line).
"""

import os
import re
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "index.html")
IMAGES_DIR = os.path.join(BASE_DIR, "Images")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff", ".JPG", ".JPEG", ".PNG", ".JPG"}

# ── Sections that use the standard 2-column .gallery layout ──────────────────
GALLERY_SECTIONS = [
    {
        "id": "experimental",
        "folder": "experimental",
    },
    {
        "id": "traditional",
        "folder": "traditional",
    },
    {
        "id": "darkroom",
        "folder": "darkroom",
    },
    {
        "id": "color",
        "folder": "color",
    },
]

# ── Digital Art sections that use the 3-column .thumbnail-grid layout ────────
THUMBNAIL_SECTIONS = [
    {
        "id": "composites",
        "folder": "digitalart",
        "label": "Composites & Digital Works",
    },
    {
        "id": "inthesameworld",
        "folder": "inthesameworld",
        "label": "In The Same World",
    },
]


HERO_NAMES = ["hero.jpg", "hero.jpeg", "hero.png", "hero.JPG", "hero.JPEG", "hero.PNG"]

# All sections (gallery + thumbnail) that have a hero div
ALL_SECTIONS = [
    {"id": "experimental", "folder": "experimental"},
    {"id": "traditional",  "folder": "traditional"},
    {"id": "darkroom",     "folder": "darkroom"},
    {"id": "color",        "folder": "color"},
    {"id": "digitalart",   "folder": "digitalart"},
]


def find_hero(folder_path):
    """Return the hero filename if one exists in the folder, else None."""
    for name in HERO_NAMES:
        if os.path.isfile(os.path.join(folder_path, name)):
            return name
    return None


def update_heroes(html):
    """Update each hero div's class and background-image style."""
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

        # Replace whatever the hero div currently looks like
        pattern = rf'<div id="{re.escape(div_id)}"[^>]*>'
        html, count = re.subn(pattern, replacement, html)
        if count == 0:
            print(f"  ⚠  Hero div 'id={div_id}' not found in HTML — skipped.")
    return html
// ...existing code...
def build_thumbnail_block(section_id, images, folder, label):
    """Build HTML for a 3-column thumbnail-grid block."""
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
        lines.append('      <p style="color:#999;font-style:italic;grid-column:1/-1;padding:2rem 0;">Images coming soon.</p>')
    lines.append(f"      <!-- GALLERY:{section_id} END -->")
    return "\n".join(lines)
// ...existing code...

def natural_sort_key(name):
    """Sort filenames so 2.jpg < 10.jpg (numeric-aware)."""
    parts = re.split(r"(\d+)", name)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def get_images(folder_path):
    """Return ordered list of image filenames for a folder."""
    if not os.path.isdir(folder_path):
        return []

    sort_file = os.path.join(folder_path, "sort_order.txt")
    if os.path.isfile(sort_file):
        with open(sort_file) as f:
            ordered = [line.strip() for line in f if line.strip()]
        # Only include files that actually exist on disk (exclude hero images)
        existing = set(os.listdir(folder_path))
        images = [fn for fn in ordered if fn in existing and fn.lower() not in {h.lower() for h in HERO_NAMES}]
        # Append any new files not yet in sort_order.txt
        in_order = set(images)
        extras = sorted(
            [fn for fn in existing if fn not in in_order
             and os.path.splitext(fn)[1] in IMAGE_EXTS
             and fn.lower() not in {h.lower() for h in HERO_NAMES}],
            key=natural_sort_key,
        )
        if extras:
            print(f"  ⚠  New files not in sort_order.txt (appended at end): {extras}")
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
    """Build HTML for a standard 2-column gallery block."""
    lines = [f"      <!-- GALLERY:{section_id} START -->"]
    for fn in images:
        path = f"Images/{folder}/{fn}"
        lines.append(f'      <div class="gallery-item">')
        lines.append(f'        <img src="{path}" alt="{section_id} - {fn}">')
        lines.append(f'      </div>')
    lines.append(f"      <!-- GALLERY:{section_id} END -->")
    return "\n".join(lines)


def build_thumbnail_block(section_id, images, folder, label):
    """Build HTML for a 3-column thumbnail-grid block."""
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
        lines.append('      <p style="color:#999;font-style:italic;grid-column:1/-1;padding:2rem 0;">Images coming soon.</p>')
    lines.append(f"      <!-- GALLERY:{section_id} END -->")
    return "\n".join(lines)


def replace_block(html, section_id, new_block):
    """Replace everything between START and END markers for a section."""
    pattern = (
        rf"([ \t]*<!-- GALLERY:{re.escape(section_id)} START -->)"
        rf".*?"
        rf"([ \t]*<!-- GALLERY:{re.escape(section_id)} END -->)"
    )
    replacement = new_block
    new_html, count = re.subn(pattern, replacement, html, flags=re.DOTALL)
    if count == 0:
        print(f"  ⚠  No markers found for section '{section_id}' — skipped.")
    return new_html


def main():
    auto_push = "--push" in sys.argv

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # ── Hero backdrops ────────────────────────────────────────────────────────
    print("Heroes:")
    html = update_heroes(html)

    # ── Standard gallery sections ─────────────────────────────────────────────
    for sec in GALLERY_SECTIONS:
        folder_path = os.path.join(IMAGES_DIR, sec["folder"])
        images = get_images(folder_path)
        print(f"  {sec['id']}: {len(images)} image(s)")
        block = build_gallery_block(sec["id"], images, sec["folder"])
        html = replace_block(html, sec["id"], block)

    # ── Thumbnail sections (Digital Art) ─────────────────────────────────────
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
        print("\n📤  Committing and pushing to GitHub...")
        subprocess.run(["git", "-C", BASE_DIR, "add", "."], check=True)
        subprocess.run(["git", "-C", BASE_DIR, "commit", "-m", "Auto-update galleries from local image folders"], check=True)
        subprocess.run(["git", "-C", BASE_DIR, "push", "origin", "main"], check=True)
        print("🚀  Pushed! Your live site will update in ~1-2 minutes.")
    else:
        print("\nTo push to your live site, run:")
        print("    python3 update_gallery.py --push")
        print("  or manually:")
        print('    git add . && git commit -m "Update galleries" && git push origin main')


if __name__ == "__main__":
    main()
