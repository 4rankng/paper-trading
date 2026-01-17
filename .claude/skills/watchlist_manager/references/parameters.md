# Watchlist Manager - Complete Parameter Reference

## Mode Selection

- `--add`: Add new stock to watchlist
- `--update`: Update existing stock
- `--remove`: Remove stock from watchlist
- `--summary`: Show watchlist summary statistics
- (default): Search/filter mode

## Search/Filter Parameters

### Basic Search
- `--ticker TICKER`: Search by ticker symbol
- `--tickers T1,T2`: Batch search by comma-separated tickers
- `--search-name NAME`: Search by name (partial match)
- `--top N`: Limit results to top N

### Category Filters
- `--sector SECTOR`: Filter by sector
- `--filter-industry INDUSTRY`: Filter by industry

### Signal Filters
- `--action ACTION`: Filter by action (BUY, WATCH, AVOID, HOLD, SELL, SHORT)
- `--filter-conviction LEVEL`: Filter by conviction (VERY_HIGH, HIGH, MODERATE, LOW, VERY_LOW)
- `--priority LEVEL`: Filter by priority (HIGH, MEDIUM, LOW)
- `--filter-rating RATING`: Filter by rating (A, B, C, D, F)

### Score Filters
- `--min-score N`: Filter by minimum total score (0-100)
- `--max-score N`: Filter by maximum total score (0-100)

### Component Score Filters
- `--min-growth N`: Minimum growth component score
- `--max-growth N`: Maximum growth component score
- `--min-value N`: Minimum value component score
- `--max-value N`: Maximum value component score
- `--min-profitability N`: Minimum profitability component score
- `--max-profitability N`: Maximum profitability component score
- `--min-momentum N`: Minimum momentum component score
- `--max-momentum N`: Maximum momentum component score

### Price Filters
- `--min-price N`: Filter by minimum current price
- `--max-price N`: Filter by maximum current price

### Ratio Filters
- `--min-upside N`: Filter by minimum upside potential %
- `--max-upside N`: Filter by maximum upside potential %
- `--min-downside N`: Filter by minimum downside risk %
- `--max-downside N`: Filter by maximum downside risk %
- `--min-rr N`: Filter by minimum risk/reward ratio
- `--max-rr N`: Filter by maximum risk/reward ratio

### Factor Filters
- `--filter-flags FLAG1 FLAG2`: Filter by flags (must have at least one)
- `--catalyst TEXT`: Filter by catalyst text (contains)

### Sorting
- `--sort FIELD`: Sort options:
  - `score`: By total score (descending)
  - `priority`: By priority (HIGH → MEDIUM → LOW)
  - `ticker`: Alphabetically by ticker
  - `date_added`: By date added (newest first)
  - `upside`: By upside potential % (descending)
  - `downside`: By downside risk % (ascending)
  - `rr` or `risk_reward`: By risk/reward ratio (descending)
  - `growth`: By growth component score
  - `value`: By value component score
  - `profitability`: By profitability component score
  - `momentum`: By momentum component score

### Output Format
- `--format FORMAT`: Output format options:
  - `json`: Machine-readable JSON (default)
  - `human`: Visual format with emojis, flags, catalysts
  - `compact`: Table format optimized for quick scanning

## Add/Update Parameters

### Required for --add
- `--ticker SYMBOL`: Stock ticker symbol
- `--name NAME`: Company name
- `--sector SECTOR`: Sector classification

### Optional for --add/--update
- `--industry INDUSTRY`: Industry classification

### Score Card Parameters
- `--components K=V K=V`: Component scores (e.g., growth=95 value=60 profitability=80 momentum=75)
- `--total-score N`: Override total score (auto-calculated if not provided)
- `--rating R`: Override letter rating (auto-calculated if not provided)

### Signal Parameters
- `--action ACTION`: Set action signal (BUY, WATCH, AVOID, HOLD, SELL, SHORT)
- `--conviction LEVEL`: Set conviction level (VERY_HIGH, HIGH, MODERATE, LOW, VERY_LOW)
- `--alternatives T1,T2`: Set alternative investments (comma-separated)

### Setup Parameters
- `--current-price N`: Current stock price
- `--target-entry N`: Target entry price
- `--target-exit N`: Target exit price
- `--invalidation N`: Invalidation/stop price

### Key Factors Parameters
- `--flags F1 F2`: Add warning signs or attributes (e.g., CHINA_RISK UNPROFITABLE)
- `--catalysts C1 C2`: Add specific catalysts (e.g., "Q3 revenue +144%")
- `--breakeven-est DATE`: Set breakeven estimate (e.g., 2029)

## Usage Examples

### Complex Filtering
```bash
# Find high-quality value stocks with good upside
python .claude/skills/watchlist_manager/scripts/watchlist_manager.py \
  --min-value 80 --min-score 65 --min-upside 30 --sort value --format compact

# Find risky turnaround plays
python .claude/skills/watchlist_manager/scripts/watchlist_manager.py \
  --filter-flags "TURNAROUND" "CONTROVERSIAL" --action WATCH --format human

# Find AI-related opportunities
python .claude/skills/watchlist_manager/scripts/watchlist_manager.py \
  --catalyst "AI" --min-score 60 --sort score --top 10 --format compact
```

### Batch Operations
```bash
# Check multiple tickers at once
python .claude/skills/watchlist_manager/scripts/watchlist_manager.py \
  --tickers NVDA,AAPL,META,TSLA --format compact

# Find all A-rated stocks
python .claude/skills/watchlist_manager/scripts/watchlist_manager.py \
  --filter-rating A --format compact
```
