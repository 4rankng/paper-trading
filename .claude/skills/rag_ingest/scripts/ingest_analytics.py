#!/usr/bin/env python3
"""Ingest analytics files from filedb/analytics into ChromaDB vector store."""

import os
import sys
import argparse
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import yaml


def sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Convert non-serializable metadata values to strings.

    ChromaDB only accepts str, int, float, bool in metadata.
    """
    sanitized = {}
    for key, value in metadata.items():
        if isinstance(value, datetime):
            sanitized[key] = value.isoformat()
        elif isinstance(value, (str, int, float, bool)):
            sanitized[key] = value
        else:
            sanitized[key] = str(value)
    return sanitized

# Add shared modules to path
shared_dir = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_dir))

from vector_store import get_vector_store


# Chunking parameters (same as news)
CHUNK_SIZE = 1000  # tokens
CHUNK_OVERLAP = 100  # tokens
MIN_CHUNK_SIZE = 200  # tokens


def count_tokens(text: str) -> int:
    """Estimate token count (rough approximation: 1 token ≈ 4 chars)."""
    return len(text) // 4


def chunk_text(text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Split text into chunks with overlap.

    Args:
        text: Input text to chunk
        metadata: Document metadata to attach to each chunk

    Returns:
        List of dicts with keys: id, text, metadata
    """
    chunks = []
    estimated_tokens = count_tokens(text)

    # If text is small enough, return as single chunk
    if estimated_tokens <= MIN_CHUNK_SIZE:
        return [{
            "id": metadata.get("id", "unknown"),
            "text": text,
            "metadata": metadata,
        }]

    # Simple character-based chunking
    target_chars = CHUNK_SIZE * 4
    overlap_chars = CHUNK_OVERLAP * 4
    min_chars = MIN_CHUNK_SIZE * 4

    start = 0
    chunk_idx = 0

    while start < len(text):
        end = start + target_chars

        # Try to break at sentence boundary
        if end < len(text):
            window = text[end-100:end]
            for i, char in enumerate(reversed(window)):
                if char in '.!?':
                    end = end - 100 + i + 1
                    break

        chunk_text = text[start:end].strip()

        # Skip if too small (except for last chunk)
        if len(chunk_text) >= min_chars or end >= len(text):
            chunk_id = f"{metadata.get('id', 'unknown')}_chunk{chunk_idx}"
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = chunk_idx

            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "metadata": chunk_metadata,
            })
            chunk_idx += 1

        start = end - overlap_chars

    return chunks


def parse_analytics_file(filepath: Path) -> Dict[str, Any]:
    """Parse analytics file with YAML frontmatter.

    Args:
        filepath: Path to .md file

    Returns:
        Dict with keys: metadata (dict), content (str)
    """
    content = filepath.read_text()

    # Check for YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1])
                file_content = parts[2].strip()
                return {"metadata": metadata or {}, "content": file_content}
            except yaml.YAMLError:
                pass

    # No valid frontmatter
    return {"metadata": {}, "content": content}


def scan_analytics_files(base_dir: Path, ticker: str = None) -> List[Dict[str, Any]]:
    """Scan filedb/analytics for analysis files.

    Args:
        base_dir: Base filedb directory
        ticker: Optional ticker filter (e.g., "NVDA")

    Returns:
        List of document dicts with keys: id, text, metadata
    """
    analytics_dir = base_dir / "analytics"
    documents = []

    if not analytics_dir.exists():
        print(f"Analytics directory not found: {analytics_dir}")
        return documents

    # Determine search pattern
    if ticker:
        search_dirs = [analytics_dir / ticker]
    else:
        search_dirs = [d for d in analytics_dir.iterdir() if d.is_dir()]

    for ticker_dir in search_dirs:
        if not ticker_dir.is_dir():
            continue

        ticker = ticker_dir.name

        # Find all .md files
        for md_file in ticker_dir.glob("*.md"):
            parsed = parse_analytics_file(md_file)

            # Determine file type from filename
            filename = md_file.stem.lower()
            if "technical" in filename:
                doc_type = "technical"
            elif "fundamental" in filename:
                doc_type = "fundamental"
            elif "thesis" in filename:
                doc_type = "thesis"
            else:
                doc_type = "other"

            # Build metadata
            metadata = parsed["metadata"]
            metadata.update({
                "ticker": ticker,
                "filename": md_file.name,
                "filepath": str(md_file.relative_to(base_dir)),
                "doc_type": doc_type,
                "content_type": "analytics",
            })

            # Sanitize metadata (convert datetime to string, etc.)
            metadata = sanitize_metadata(metadata)

            # Generate unique ID
            file_hash = hashlib.md5(str(md_file).encode()).hexdigest()[:8]
            doc_id = f"analytics_{ticker}_{doc_type}_{file_hash}"

            documents.append({
                "id": doc_id,
                "text": parsed["content"],
                "metadata": metadata,
            })

    print(f"Found {len(documents)} analytics documents")
    return documents


def ingest_analytics(
    base_dir: str = "./filedb",
    ticker: str = None,
    force: bool = False,
) -> None:
    """Ingest analytics files into vector store.

    Args:
        base_dir: Base filedb directory
        ticker: Optional ticker filter
        force: Re-index all files (ignore existing)
    """
    base_path = Path(base_dir)
    vector_store = get_vector_store()

    # Scan for documents
    documents = scan_analytics_files(base_path, ticker)

    if not documents:
        print("No analytics documents found to ingest")
        return

    # Chunk documents
    all_chunks = []
    for doc in documents:
        # Add doc_id to metadata for chunking
        metadata_with_id = doc["metadata"].copy()
        metadata_with_id["id"] = doc["id"]
        chunks = chunk_text(doc["text"], metadata_with_id)
        all_chunks.extend(chunks)

    print(f"Created {len(all_chunks)} chunks from {len(documents)} documents")

    # Add to vector store
    print("Adding chunks to vector store...")
    vector_store.add_documents_batch(all_chunks, collection="analytics")

    # Show stats
    stats = vector_store.get_collection_stats("analytics")
    print(f"Analytics collection now has {stats.get('analytics', 0)} documents")


def main():
    parser = argparse.ArgumentParser(description="Ingest analytics files into RAG vector store")
    parser.add_argument("--ticker", type=str, help="Ticker symbol to filter (e.g., NVDA)")
    parser.add_argument("--base-dir", type=str, default="./filedb", help="Base filedb directory")
    parser.add_argument("--force", action="store_true", help="Re-index all files")

    args = parser.parse_args()

    ingest_analytics(
        base_dir=args.base_dir,
        ticker=args.ticker,
        force=args.force,
    )


if __name__ == "__main__":
    main()
