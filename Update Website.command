#!/bin/bash
cd /Users/noramahler/Documents/NDM-WEBSITE
echo "🔄 Scanning image folders and updating site..."
python3 update_gallery.py --push
echo ""
echo "✅ Done! Your site will be live in ~1-2 minutes."
echo "   Press any key to close this window."
read -n 1
