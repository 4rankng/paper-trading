# RAG Search Skill

Search the ChromaDB vector store for relevant news, analytics, and web searches using semantic search.

## Scripts

### search.py
Perform semantic search across indexed documents.

**Usage:**
```bash
python3 search.py "NVDA earnings" [--collection COLLECTION] [--limit N] [--ticker TICKER] [--format FORMAT]
```

**Arguments:**
- `query`: Search query (required)
- `--collection`: Collection to search: `all`, `news`, `analytics`, `web_searches` (default: all)
- `--limit`: Number of results (default: 5)
- `--ticker`: Filter by ticker symbol (optional)
- `--format`: Output format: `text` or `json` (default: text)

**Examples:**
```bash
# Search for NVDA news
python3 search.py "NVDA earnings beat" --collection news --limit 5

# Search analytics for AAPL
python3 search.py "AAPL fundamental analysis" --collection analytics --ticker AAPL

# Search all collections
python3 search.py "portfolio performance" --collection all --limit 10

# JSON output for API integration
python3 search.py "market outlook" --format json
```

**Output (text format):**
```
Searching for: NVDA earnings beat
Collection: news
Embedding model: ollama:nomic-embed-text

Found 3 results:

--- Result 1 ---
[news] Score: 0.892
ID: news_NVDA_a1b2c3d4
Ticker: NVDA
Date: 2025-01-15
Title: NVIDIA Q4 Earnings Beat Estimates

NVDA reported Q4 earnings of $5.16 per share, beating estimates...
```

**Output (json format):**
```json
{
  "query": "NVDA earnings beat",
  "model": "ollama:nomic-embed-text",
  "count": 3,
  "results": [
    {
      "id": "news_NVDA_a1b2c3d4",
      "text": "NVDA reported Q4 earnings...",
      "metadata": {
        "ticker": "NVDA",
        "date": "2025-01-15",
        "title": "NVIDIA Q4 Earnings Beat Estimates"
      },
      "score": 0.892,
      "collection": "news"
    }
  ]
}
```

## API Integration

### GET /api/rag/search
Search from the webapp.

**Query Parameters:**
- `query`: Search query (required)
- `collection`: `all`, `news`, `analytics`, `web_searches` (default: all)
- `limit`: 1-50 (default: 5)
- `ticker`: Filter by ticker (optional)

**Example:**
```
GET /api/rag/search?query=NVDA+earnings&collection=news&limit=5
```

**Response:**
```json
{
  "query": "NVDA earnings",
  "model": "ollama:nomic-embed-text",
  "count": 5,
  "results": [...]
}
```

## Chat Integration

The RAG search is integrated into the chat API with a hybrid strategy:

### Automatic Search
For queries containing news keywords: "news", "latest", "recent", "headline", "breaking", "update"

**Example:**
- User: "What's the latest news on NVDA?"
- System: Auto-searches news collection and injects results into LLM context

### Explicit Tool Call
For analytics and research queries, the LLM can call the `rag_search` tool explicitly.

**Example:**
- User: "Show research on AAPL fundamentals"
- LLM: Calls `rag_search` tool with query="AAPL fundamentals", collection="analytics"

## Dependencies

- chromadb>=0.4.0
- ollama>=0.1.0
