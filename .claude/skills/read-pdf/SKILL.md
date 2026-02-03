---
name: read-pdf
description: Extract text and data from PDF files using Python. Use for: "read pdf", "extract pdf text", "parse pdf", "pdf content", "read pdf file", "get pdf data". Supports password-protected PDFs, page ranges, and text extraction.
allowed-tools:
  - Read
  - Write
  - Bash(python:*)
---

# PDF Reader - Quick Reference

Extract text and structured data from PDF files for analysis and processing.

---

## Quick Start

```bash
# Read entire PDF
python .claude/skills/read-pdf/scripts/read_pdf.py --path /path/to/file.pdf

# Read specific pages (1-3)
python .claude/skills/read-pdf/scripts/read_pdf.py --path file.pdf --pages 1-3

# Read with password
python .claude/skills/read-pdf/scripts/read_pdf.py --path file.pdf --password secret

# Output to file
python .claude/skills/read-pdf/scripts/read_pdf.py --path file.pdf --output extracted.txt
```

---

## When to Use

| Use | Don't Use |
|-----|-----------|
| Extract text from PDFs | Image-only PDFs (use OCR) |
| Parse financial reports | |
| Read research documents | |
| Convert PDF to text | |

---

## Available Scripts

**read_pdf.py** - Main PDF reading script
- `--path` - PDF file path (required)
- `--pages` - Page range (e.g., "1-3", "5", "1,3,5")
- `--password` - Password for protected PDFs
- `--output` - Save extracted text to file
- `--metadata` - Show PDF metadata (author, title, etc.)

---

## Output Format

Returns extracted text with page markers:
```
--- Page 1 ---
[Text content from page 1]

--- Page 2 ---
[Text content from page 2]
```

---

## Requirements

- PyPDF2 library: `pip install PyPDF2`

---

## Constraints

- PDF must contain extractable text (not scanned images)
- Password-protected PDFs require password
- Complex layouts may need manual cleanup
