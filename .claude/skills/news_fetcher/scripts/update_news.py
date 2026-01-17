#!/usr/bin/env python3
"""
Update existing news article content.

Usage:
    python update_news.py --file news/TCOM/2026/01/slug.md --content "Updated content..."
"""
import argparse
import json
import re
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    current_path = Path(__file__).resolve()
    if "skills" in current_path.parts:
        skills_idx = current_path.parts.index("skills")
        return Path(*current_path.parts[:skills_idx - 1])
    return Path(__file__).parent.parent.parent.parent


def update_news_article(file_path: str, new_content: str) -> dict:
    """
    Update existing news article content.

    Args:
        file_path: Path to news file
        new_content: New content for the article

    Returns:
        Dictionary with result
    """
    project_root = get_project_root()
    filepath = project_root / file_path

    if not filepath.exists():
        return {
            'status': 'error',
            'error': f'File not found: {file_path}'
        }

    try:
        # Read existing file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract frontmatter and preserve it
        frontmatter_match = re.match(r'^(---\n.*?\n---)', content, re.DOTALL)

        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            # Write updated content with preserved frontmatter
            updated_content = f"""{frontmatter}

# Updated Content

{new_content}
"""
        else:
            # No frontmatter found, just write new content
            updated_content = new_content

        # Write updated file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        return {
            'status': 'success',
            'file': file_path,
            'frontmatter_preserved': frontmatter_match is not None
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'file': file_path
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Update existing news article')
    parser.add_argument('--file', required=True, type=str, help='Path to news file')
    parser.add_argument('--content', required=True, type=str, help='New content')

    args = parser.parse_args()

    result = update_news_article(args.file, args.content)
    print(json.dumps(result, indent=2))

    if result['status'] == 'error':
        sys.exit(1)


if __name__ == '__main__':
    main()
