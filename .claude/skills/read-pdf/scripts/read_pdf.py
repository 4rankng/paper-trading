#!/usr/bin/env python3
"""
PDF Reader - Extract text from PDF files.

Usage:
    python read_pdf.py --path file.pdf
    python read_pdf.py --path file.pdf --pages 1-3
    python read_pdf.py --path file.pdf --password secret --output text.txt
"""

import argparse
import sys
from pathlib import Path


def read_pdf(path: str, pages: str = None, password: str = None) -> dict:
    """Extract text from PDF file.

    Args:
        path: Path to PDF file
        pages: Page range (e.g., "1-3", "5", "1,3,5")
        password: Password for protected PDFs

    Returns:
        Dict with metadata and pages content
    """
    try:
        import PyPDF2
    except ImportError:
        return {"error": "PyPDF2 not installed. Run: pip install PyPDF2"}

    path_obj = Path(path)
    if not path_obj.exists():
        return {"error": f"File not found: {path}"}

    result = {"metadata": {}, "pages": [], "total_pages": 0}

    try:
        with open(path_obj, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            # Handle password
            if password:
                if reader.is_encrypted:
                    reader.decrypt(password)
                else:
                    return {"error": "PDF is not encrypted"}

            # Extract metadata
            if reader.metadata:
                result["metadata"] = {
                    "title": reader.metadata.get("/Title", ""),
                    "author": reader.metadata.get("/Author", ""),
                    "subject": reader.metadata.get("/Subject", ""),
                    "creator": reader.metadata.get("/Creator", ""),
                    "producer": reader.metadata.get("/Producer", ""),
                    "creation_date": str(reader.metadata.get("/CreationDate", "")),
                }

            result["total_pages"] = len(reader.pages)

            # Parse page selection
            page_indices = _parse_pages(pages, len(reader.pages)) if pages else range(len(reader.pages))

            # Extract text from pages
            for i in page_indices:
                if 0 <= i < len(reader.pages):
                    page = reader.pages[i]
                    text = page.extract_text()
                    result["pages"].append({
                        "page_number": i + 1,
                        "text": text.strip()
                    })

    except Exception as e:
        return {"error": f"Failed to read PDF: {str(e)}"}

    return result


def _parse_pages(pages_spec: str, total_pages: int) -> list:
    """Parse page specification into list of indices.

    Args:
        pages_spec: Page string like "1-3", "5", "1,3,5"
        total_pages: Total number of pages in PDF

    Returns:
        List of zero-based page indices
    """
    indices = []

    for part in pages_spec.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            start_idx = int(start) - 1
            end_idx = int(end) - 1
            indices.extend(range(max(0, start_idx), min(total_pages, end_idx + 1)))
        else:
            idx = int(part) - 1
            if 0 <= idx < total_pages:
                indices.append(idx)

    return sorted(set(indices))


def format_output(result: dict) -> str:
    """Format result as readable text.

    Args:
        result: Result dict from read_pdf()

    Returns:
        Formatted string
    """
    if "error" in result:
        return f"Error: {result['error']}"

    output = []

    # Metadata
    if result["metadata"]:
        output.append("## PDF Metadata")
        for key, value in result["metadata"].items():
            if value:
                output.append(f"{key.capitalize()}: {value}")
        output.append("")

    # Pages
    for page in result["pages"]:
        output.append(f"--- Page {page['page_number']} ---")
        output.append(page["text"])
        output.append("")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF files")
    parser.add_argument("--path", required=True, help="Path to PDF file")
    parser.add_argument("--pages", help="Page range (e.g., '1-3', '5', '1,3,5')")
    parser.add_argument("--password", help="Password for protected PDFs")
    parser.add_argument("--output", help="Save extracted text to file")
    parser.add_argument("--metadata", action="store_true", help="Show only metadata")

    args = parser.parse_args()

    # Read PDF
    result = read_pdf(args.path, args.pages, args.password)

    # Handle metadata-only mode
    if args.metadata and "metadata" in result:
        import json
        print(json.dumps(result["metadata"], indent=2))
        return

    # Format output
    text = format_output(result)

    # Save or print
    if args.output:
        Path(args.output).write_text(text)
        print(f"Extracted text saved to: {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
