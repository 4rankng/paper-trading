#!/usr/bin/env python3
"""
Script to fill in content for news files that only have weblinks.
Uses MCP web reader to fetch article content.
"""

import json
import re
import sys
from pathlib import Path

# Find all .md files in news directory
news_dir = Path("news")
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
                'file': str(md_file),
                'url': url,
                'current_content': content
            })

print(f"Found {len(files_needing_content)} files needing content")
print()

# Output as JSON for the next step
print("URLs to fetch:")
for item in files_needing_content[:10]:
    print(f"- {item['file']}")
    print(f"  {item['url']}")
    print()

if len(files_needing_content) > 10:
    print(f"... and {len(files_needing_content) - 10} more files")
