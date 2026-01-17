#!/usr/bin/env python3
"""
Delete a news article.

Usage:
    python delete_news.py --file news/TCOM/2026/01/slug.md
"""
import argparse
import json
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    current_path = Path(__file__).resolve()
    if "skills" in current_path.parts:
        skills_idx = current_path.parts.index("skills")
        return Path(*current_path.parts[:skills_idx - 1])
    return Path(__file__).parent.parent.parent.parent


def delete_news_article(file_path: str, confirm: bool = False) -> dict:
    """
    Delete a news article.

    Args:
        file_path: Path to news file
        confirm: Skip confirmation prompt

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
        if not confirm:
            # Ask for confirmation
            response = input(f"Are you sure you want to delete {file_path}? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                return {
                    'status': 'cancelled',
                    'file': file_path
                }

        filepath.unlink()

        return {
            'status': 'success',
            'file': file_path,
            'deleted': True
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'file': file_path
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Delete a news article')
    parser.add_argument('--file', required=True, type=str, help='Path to news file')
    parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')

    args = parser.parse_args()

    result = delete_news_article(args.file, args.confirm)
    print(json.dumps(result, indent=2))

    if result['status'] == 'error':
        sys.exit(1)


if __name__ == '__main__':
    main()
