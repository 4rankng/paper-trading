#!/usr/bin/env python3
"""
Web search using duckduckgo-search library.
Free, open-source, no API key required.
"""
import sys
import json
from typing import List, Dict

try:
    from ddgs import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False


def web_search(query: str, limit: int = 5) -> Dict:
    """
    Perform web search using DuckDuckGo.

    Args:
        query: Search query
        limit: Maximum number of results

    Returns:
        Dict with results array
    """
    if not HAS_DDGS:
        return {
            'query': query,
            'results': [],
            'count': 0,
            'error': 'ddgs library not installed. Run: pip install ddgs'
        }

    try:
        ddgs = DDGS()
        results = []

        # Search using DuckDuckGo
        search_results = ddgs.text(
            query,
            max_results=limit
        )

        for item in search_results:
            results.append({
                'title': item.get('title', ''),
                'url': item.get('href', ''),
                'snippet': item.get('body', '')[:300],
                'source': 'DuckDuckGo'
            })

        return {
            'query': query,
            'results': results,
            'count': len(results)
        }

    except Exception as e:
        return {
            'query': query,
            'results': [],
            'count': 0,
            'error': str(e)
        }


def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: web_search.py <query> [limit]", file=sys.stderr)
        sys.exit(1)

    # Parse arguments
    limit = 5
    query_parts = []

    for arg in sys.argv[1:]:
        if arg.isdigit():
            limit = int(arg)
        else:
            query_parts.append(arg)

    query = ' '.join(query_parts)

    result = web_search(query, limit)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
