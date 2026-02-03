#!/usr/bin/env python3
"""
Script to fetch news article content and update files.
Uses BeautifulSoup to parse article content from HTML.
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "lxml"], check=True)
    import requests
    from bs4 import BeautifulSoup

# Get script directory and project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent
DATA_FILE = SCRIPT_DIR / "news_to_update.json"

# Read the JSON file
with open(DATA_FILE, 'r') as f:
    files_needing_content = json.load(f)

print(f"Processing {len(files_needing_content)} files...")
print()

def extract_article_content(html_content, url):
    """Extract article content from HTML."""
    soup = BeautifulSoup(html_content, 'lxml')

    # Remove script and style elements
    for script in soup(["script", "style", "nav", "header", "footer"]):
        script.decompose()

    # Try different selectors for article content
    article_content = None

    # Try common article selectors
    selectors = [
        'article',
        '[data-test="article-body"]',
        '.caas-body',
        '.article-body',
        '.post-content',
        '.entry-content',
        '.news-content',
        'main'
    ]

    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            article_content = element.get_text(separator='\n', strip=True)
            break

    # If no specific selector found, try to find the largest text block
    if not article_content:
        # Get all paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            article_content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

    # Clean up the content
    if article_content:
        # Remove very short lines (likely navigation)
        lines = article_content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if len(line) > 20:  # Keep only substantial lines
                cleaned_lines.append(line)
        article_content = '\n\n'.join(cleaned_lines[:30])  # Limit to first 30 meaningful paragraphs

    return article_content or "Content could not be extracted."

def update_news_file(file_path, url, article_content):
    """Update a news file with fetched content."""
    # Handle relative paths from JSON
    file_path = PROJECT_ROOT / file_path

    with open(file_path, 'r', encoding='utf-8') as f:
        current_content = f.read()

    # Split by ---
    parts = current_content.split('---', 2)

    if len(parts) >= 3:
        # Keep YAML frontmatter and title, replace the rest with article content
        yaml_part = parts[1] if len(parts) > 1 else ""
        new_content = f"---{yaml_part}---\n\n{article_content}\n"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True
    return False

# Process each file
success_count = 0
failed_urls = []

for i, item in enumerate(files_needing_content, 1):
    file_path = item['file']
    url = item['url']

    print(f"[{i}/{len(files_needing_content)}] Processing: {file_path}")
    print(f"  URL: {url}")

    try:
        # Fetch the content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Extract article content
        article_content = extract_article_content(response.text, url)

        # Update the file
        if update_news_file(file_path, url, article_content):
            print(f"  ✓ Updated successfully")
            success_count += 1
        else:
            print(f"  ✗ Failed to update file")

        # Rate limiting - be respectful
        time.sleep(1)

    except Exception as e:
        print(f"  ✗ Error: {e}")
        failed_urls.append((file_path, url, str(e)))

    print()

# Summary
print("=" * 60)
print(f"Processing complete!")
print(f"Successfully updated: {success_count}/{len(files_needing_content)}")
print(f"Failed: {len(failed_urls)}")

if failed_urls:
    print("\nFailed URLs:")
    for file_path, url, error in failed_urls:
        print(f"  {file_path}")
        print(f"    {url}")
        print(f"    Error: {error}")
        print()
