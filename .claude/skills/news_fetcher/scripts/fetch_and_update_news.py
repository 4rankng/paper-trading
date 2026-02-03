#!/usr/bin/env python3
"""
Script to fetch news content using web reader and update files.
Processes news files in batches to avoid overwhelming the system.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

# Get script directory and project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent
DATA_FILE = SCRIPT_DIR / "news_to_update.json"

# Find all .md files in news directory that need content
news_dir = PROJECT_ROOT / "news"
files_needing_content = []

print("Finding news files that need content...")
for md_file in news_dir.rglob("*.md"):
    line_count = sum(1 for _ in open(md_file, 'r', encoding='utf-8'))

    # Files with 15 or fewer lines likely missing content
    if line_count <= 15:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract URL
        url_match = re.search(r'url:\s*(.+)', content)
        if url_match:
            url = url_match.group(1).strip()
            files_needing_content.append({
                'file': str(md_file.relative_to(PROJECT_ROOT)),
                'url': url,
                'current_content': content
            })

print(f"Found {len(files_needing_content)} files needing content")
print()

# Save to JSON file for batch processing
with open(DATA_FILE, 'w') as f:
    json.dump(files_needing_content, f, indent=2)

print(f"Saved list to {DATA_FILE}")
print(f"Will process in batches of 5 URLs at a time.")
