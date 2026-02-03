"""
Unified data access layer for stock advisor.

This module provides a single, consistent API for all data operations
across the stock advisor system, eliminating duplicated file access code.
"""
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from .project import get_project_root


@dataclass
class AnalyticsFiles:
    """
    Container for analytics file paths and metadata.

    Attributes:
        ticker: Uppercase ticker symbol
        technical: Path to technical analysis file
        fundamental: Path to fundamental analysis file
        thesis: Path to investment thesis file
        price_csv: Path to price data CSV file
    """
    ticker: str
    technical: Optional[Path] = None
    fundamental: Optional[Path] = None
    thesis: Optional[Path] = None
    price_csv: Optional[Path] = None

    def exists(self) -> bool:
        """Check if all required analytics files exist."""
        return all([
            self.technical and self.technical.exists(),
            self.fundamental and self.fundamental.exists(),
            self.thesis and self.thesis.exists(),
        ])

    def missing_files(self) -> List[str]:
        """Return list of missing file types."""
        missing = []
        if not self.technical or not self.technical.exists():
            missing.append("technical")
        if not self.fundamental or not self.fundamental.exists():
            missing.append("fundamental")
        if not self.thesis or not self.thesis.exists():
            missing.append("thesis")
        return missing


@dataclass
class PortfolioHolding:
    """Minimal portfolio holding data (v3.0 schema)."""
    ticker: str
    shares: int
    avg_cost: float
    current_price: float
    status: str = "active"
    market_value: float = 0.0
    gain_loss: float = 0.0
    gain_loss_pct: float = 0.0
    pct_portfolio: float = 0.0


@dataclass
class NewsFile:
    """Container for news file metadata."""
    path: Path
    ticker: str
    date: Optional[datetime] = None
    age_hours: float = 0.0


class DataAccess:
    """
    Central data access layer for all stock advisor data.

    This class provides a unified API for reading and writing all
    data types in the stock advisor system.

    Example:
        da = DataAccess()
        analytics = da.read_analytics("NVDA")
        prices = da.read_price_data("NVDA")
        portfolio = da.get_portfolio("CORE")
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize DataAccess with project root.

        Args:
            project_root: Optional project root path. If not provided,
                         will be detected automatically.
        """
        self.root = project_root or get_project_root()
        self._analytics_dir = self.root / "analytics"
        self._prices_dir = self.root / "prices"
        self._news_dir = self.root / "news"
        self._portfolios_path = self.root / "portfolios.json"
        self._watchlist_path = self.root / "watchlist.json"
        self._trade_log_path = self.root / "trade_log.csv"

        # Cache for expensive operations
        self._cache: Dict[str, Any] = {}

    # ========== Analytics ==========

    def get_analytics_dir(self, ticker: str) -> Path:
        """Get analytics directory for a ticker."""
        return self._analytics_dir / ticker.upper()

    def get_analytics_files(self, ticker: str) -> AnalyticsFiles:
        """
        Get all analytics file paths for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            AnalyticsFiles with all file paths
        """
        ticker_dir = self.get_analytics_dir(ticker)
        t = ticker.upper()

        return AnalyticsFiles(
            ticker=t,
            technical=ticker_dir / f"{t}_technical_analysis.md",
            fundamental=ticker_dir / f"{t}_fundamental_analysis.md",
            thesis=ticker_dir / f"{t}_investment_thesis.md",
            price_csv=self._prices_dir / f"{t}.csv"
        )

    def read_analytics(self, ticker: str) -> Dict[str, Optional[str]]:
        """
        Read all analytics file contents for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dict with 'technical', 'fundamental', 'thesis' keys.
            Missing files return None values.
        """
        files = self.get_analytics_files(ticker)

        return {
            "technical": self._read_file(files.technical),
            "fundamental": self._read_file(files.fundamental),
            "thesis": self._read_file(files.thesis),
        }

    def write_analytics(
        self,
        ticker: str,
        content_type: str,
        content: str
    ) -> Path:
        """
        Write analytics content to file.

        Args:
            ticker: Stock ticker symbol
            content_type: One of 'technical', 'fundamental', 'thesis'
            content: Markdown content to write

        Returns:
            Path to written file
        """
        if content_type not in ("technical", "fundamental", "thesis"):
            raise ValueError(f"Invalid content_type: {content_type}")

        ticker_dir = self.get_analytics_dir(ticker)
        ticker_dir.mkdir(parents=True, exist_ok=True)

        t = ticker.upper()
        filename = {
            "technical": f"{t}_technical_analysis.md",
            "fundamental": f"{t}_fundamental_analysis.md",
            "thesis": f"{t}_investment_thesis.md",
        }[content_type]

        filepath = ticker_dir / filename
        filepath.write_text(content)
        return filepath

    # ========== Price Data ==========

    def get_price_csv(self, ticker: str) -> Optional[Path]:
        """
        Get price CSV path for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Path if file exists, None otherwise
        """
        path = self._prices_dir / f"{ticker.upper()}.csv"
        return path if path.exists() else None

    def read_price_data(self, ticker: str) -> Optional["pd.DataFrame"]:
        """
        Read price data as DataFrame.

        Args:
            ticker: Stock ticker symbol

        Returns:
            DataFrame with date index or None if file doesn't exist
        """
        if not HAS_PANDAS:
            raise ImportError("pandas is required for read_price_data")

        csv_path = self.get_price_csv(ticker)
        if csv_path:
            try:
                return pd.read_csv(csv_path, parse_dates=["date"], index_col="date")
            except Exception as e:
                # Log error but don't crash
                return None
        return None

    def list_price_files(self) -> List[Path]:
        """List all price CSV files."""
        if not self._prices_dir.exists():
            return []
        return sorted(self._prices_dir.glob("*.csv"))

    # ========== News ==========

    def get_news_dir(self, ticker: str, year: int, month: int) -> Path:
        """Get news directory path for a specific year/month."""
        return self._news_dir / ticker.upper() / str(year) / f"{month:02d}"

    def list_news_files(
        self,
        ticker: str,
        since: Optional[datetime] = None,
        limit: int = 50
    ) -> List[NewsFile]:
        """
        List news files for a ticker.

        Args:
            ticker: Stock ticker symbol
            since: Optional datetime filter
            limit: Maximum number of files to return

        Returns:
            List of NewsFile objects, sorted by modification time (newest first)
        """
        news_base = self._news_dir / ticker.upper()
        if not news_base.exists():
            return []

        files = []
        for md_file in news_base.rglob("*.md"):
            stat = md_file.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)

            if since and mtime < since:
                continue

            age_hours = (datetime.now() - mtime).total_seconds() / 3600
            files.append(NewsFile(
                path=md_file,
                ticker=ticker.upper(),
                date=mtime,
                age_hours=age_hours
            ))

        # Sort by modification time (newest first)
        files.sort(key=lambda f: f.date or datetime.min, reverse=True)
        return files[:limit]

    def read_news_file(self, path: Path) -> Optional[str]:
        """Read a news file's content."""
        return self._read_file(path)

    # ========== Portfolios ==========

    def load_portfolios(self) -> Dict:
        """Load portfolios.json."""
        if not self._portfolios_path.exists():
            return {
                "cash": {"amount": 0.0, "target_buffer_pct": 15},
                "portfolios": {},
                "metadata": {"version": "3.0", "default_portfolio": "CORE"}
            }
        return json_load(self._portfolios_path)

    def save_portfolios(self, data: Dict) -> None:
        """Save portfolios.json."""
        data.setdefault("metadata", {})["last_updated"] = datetime.now().isoformat()
        json_save(data, self._portfolios_path)

    def get_portfolio(self, name: Optional[str] = None) -> Dict:
        """
        Get a specific portfolio or default.

        Args:
            name: Portfolio name (e.g., "CORE", "AI_PICKS").
                  If None, returns default portfolio from metadata.

        Returns:
            Portfolio dict with holdings, config, summary keys.
        """
        data = self.load_portfolios()

        if name is None:
            name = data.get("metadata", {}).get("default_portfolio", "CORE")

        portfolios = data.get("portfolios", {})
        if name not in portfolios:
            raise ValueError(
                f"Portfolio '{name}' not found. "
                f"Available: {list(portfolios.keys())}"
            )

        return portfolios[name]

    def get_shared_cash(self) -> Dict[str, Union[float, int]]:
        """Get the shared cash pool from portfolios.json."""
        data = self.load_portfolios()
        return data.get("cash", {"amount": 0.0, "target_buffer_pct": 15})

    def update_shared_cash(self, amount: float) -> None:
        """Update the shared cash pool amount."""
        data = self.load_portfolios()
        data["cash"]["amount"] = round(amount, 2)
        self.save_portfolios(data)

    def list_portfolios(self) -> List[Dict]:
        """List all portfolios with summary info."""
        data = self.load_portfolios()
        result = []

        for name, portfolio_data in data.get("portfolios", {}).items():
            summary = portfolio_data.get("summary", {})
            result.append({
                "name": name,
                "description": portfolio_data.get("description", ""),
                "holdings_value": summary.get("holdings_value", 0),
                "holdings_count": summary.get("holdings_count", 0),
                "total_gain_loss_pct": summary.get("total_gain_loss_pct", 0),
            })

        return result

    # ========== Watchlist ==========

    def load_watchlist(self) -> Dict:
        """Load watchlist.json."""
        if not self._watchlist_path.exists():
            return {"tickers": {}, "metadata": {"version": "3.0"}}
        return json_load(self._watchlist_path)

    def save_watchlist(self, data: Dict) -> None:
        """Save watchlist.json."""
        json_save(data, self._watchlist_path)

    def get_watchlist_tickers(self) -> List[str]:
        """Get list of tickers in watchlist."""
        data = self.load_watchlist()
        return list(data.get("tickers", {}).keys())

    # ========== Trade Log ==========

    def load_trade_log(self) -> List[Dict]:
        """Load trade_log.csv as list of dicts."""
        if not self._trade_log_path.exists():
            return []

        import csv
        with open(self._trade_log_path, "r") as f:
            return list(csv.DictReader(f))

    # ========== Helper Methods ==========

    def _read_file(self, path: Optional[Path]) -> Optional[str]:
        """Helper to read file if exists."""
        if path and path.exists():
            return path.read_text()
        return None

    def clear_cache(self) -> None:
        """Clear the internal cache."""
        self._cache.clear()


# ========== Helper Functions ==========

def json_load(path: Path) -> Dict:
    """Load JSON file with error handling."""
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")


def json_save(data: Dict, path: Path) -> None:
    """Save data to JSON file with formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_file_age_hours(path: Path) -> float:
    """Get file age in hours."""
    if not path.exists():
        return float('inf')
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return (datetime.now() - mtime).total_seconds() / 3600
