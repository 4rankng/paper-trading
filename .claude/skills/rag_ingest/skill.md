# RAG Ingest Skill

Ingest news articles, analytics files, and web searches into the ChromaDB vector store for semantic search.

## Scripts

### ingest_news.py
Ingest news articles from `filedb/news/{TICKER}/{YYYY}/{MM}/*.md` into the vector store.

**Usage:**
```bash
python3 ingest_news.py [--ticker TICKER] [--base-dir FILEDB_PATH] [--force]
```

**Arguments:**
- `--ticker`: Optional ticker filter (e.g., NVDA)
- `--base-dir`: Base filedb directory (default: ./filedb)
- `--force`: Re-index all files (ignore existing)

**Features:**
- Parses YAML frontmatter from markdown files
- Chunks articles into 1000-token segments with 100-token overlap
- Stores metadata: ticker, date, source, URL, filepath
- Skips already-indexed documents (by hash)

### ingest_analytics.py
Ingest analytics files from `filedb/analytics/{TICKER}/*.md` into the vector store.

**Usage:**
```bash
python3 ingest_analytics.py [--ticker TICKER] [--base-dir FILEDB_PATH] [--force]
```

**Arguments:**
- `--ticker`: Optional ticker filter (e.g., AAPL)
- `--base-dir`: Base filedb directory (default: ./filedb)
- `--force`: Re-index all files (ignore existing)

**Features:**
- Detects file type from filename (technical/fundamental/thesis)
- Chunks long documents (1000 tokens, 100 overlap)
- Stores metadata: ticker, doc_type, filename, filepath

### ingest_web_search.py
Store finance-relevant web search results in the vector store.

**Usage:**
```bash
python3 ingest_web_search.py [--base-dir FILEDB_PATH] [--force]
```

**Arguments:**
- `--base-dir`: Base filedb directory (default: ./filedb)
- `--force`: Re-index all searches (ignore existing)

**Features:**
- Filters results by finance relevance (ticker symbols + keywords)
- Skips generic queries (weather, recipes, etc.)
- Stores metadata: query, URL, title, relevance_score

## API Integration

### POST /api/rag/ingest
Trigger ingestion from the webapp.

**Request:**
```json
{
  "collections": ["news", "analytics"] | ["all"],
  "force": false,
  "ticker": "NVDA"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Ingestion completed",
  "stats": {
    "news": 150,
    "analytics": 45
  }
}
```

## Dependencies

- chromadb>=0.4.0
- ollama>=0.1.0
- tiktoken>=0.5.0
- pyyaml
