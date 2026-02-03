"""
Parallel data fetching for improved workflow efficiency.

Enables concurrent execution of the 3-step data-first workflow:
1. Load analytics files (disk I/O)
2. Load price data (disk I/O)
3. List news files (disk I/O)

These operations can run in parallel since they're independent.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .data_access import DataAccess
from .quality_scoring import QualityScore, score_analytics_files, score_price_data, score_news_data


@dataclass
class DataFetchResult:
    """
    Result of parallel data fetch operation.

    Attributes:
        ticker: Stock ticker symbol
        analytics: Dict with technical/fundamental/thesis content
        prices: DataFrame with price data (or None)
        news_files: List of recent news file paths
        quality: Overall quality assessment
        timestamp: When fetch was completed
        errors: List of any errors encountered
    """
    ticker: str
    analytics: Dict[str, Optional[str]] = field(default_factory=dict)
    prices: Optional[Any] = None
    news_files: List[Any] = field(default_factory=list)
    quality: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    errors: List[str] = field(default_factory=list)

    @property
    def overall_quality(self) -> int:
        """Get overall quality score."""
        return self.quality.get("overall", 0)

    @property
    def recommended_action(self) -> str:
        """Get recommended action based on quality."""
        return self.quality.get("action", "UNKNOWN")


def fetch_all_data(
    ticker: str,
    data_access: Optional[DataAccess] = None,
    score_quality: bool = True,
    max_age_hours: int = 24
) -> DataFetchResult:
    """
    Fetch all data for a ticker using parallel execution.

    This function concurrently executes:
    1. Load analytics files (disk I/O)
    2. Load price data (disk I/O)
    3. List news files (disk I/O)

    Args:
        ticker: Stock ticker symbol
        data_access: Optional DataAccess instance
        score_quality: Whether to calculate quality scores
        max_age_hours: Maximum age for full freshness score

    Returns:
        DataFetchResult with all fetched data
    """
    da = data_access or DataAccess()
    ticker_upper = ticker.upper()

    # Define fetch tasks
    tasks = {
        "analytics": lambda: _fetch_analytics(da, ticker_upper),
        "prices": lambda: _fetch_prices(da, ticker_upper),
        "news_list": lambda: _fetch_news_list(da, ticker_upper),
    }

    # Execute in parallel (thread pool for I/O bound tasks)
    results: Dict[str, Any] = {}
    errors: List[str] = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all tasks
        future_to_name = {
            executor.submit(func): name
            for name, func in tasks.items()
        }

        # Collect results as they complete
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                result = future.result()
                results.update(result)
            except Exception as e:
                errors.append(f"{name}: {str(e)}")

    # Calculate quality scores if requested
    quality = {}
    if score_quality:
        quality = _calculate_quality(
            ticker_upper,
            results,
            da,
            max_age_hours
        )

    return DataFetchResult(
        ticker=ticker_upper,
        analytics=results.get("analytics", {}),
        prices=results.get("prices"),
        news_files=results.get("news_files", []),
        quality=quality,
        errors=errors
    )


def fetch_multiple_tickers(
    tickers: List[str],
    data_access: Optional[DataAccess] = None,
    score_quality: bool = True
) -> Dict[str, DataFetchResult]:
    """
    Fetch data for multiple tickers in parallel.

    Args:
        tickers: List of ticker symbols
        data_access: Optional DataAccess instance
        score_quality: Whether to calculate quality scores

    Returns:
        Dict mapping ticker to DataFetchResult
    """
    da = data_access or DataAccess()
    results = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ticker = {
            executor.submit(
                fetch_all_data,
                ticker,
                da,
                score_quality
            ): ticker
            for ticker in tickers
        }

        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                results[ticker.upper()] = future.result()
            except Exception as e:
                # Create error result
                results[ticker.upper()] = DataFetchResult(
                    ticker=ticker.upper(),
                    errors=[str(e)]
                )

    return results


# ========== Internal Helpers ==========

def _fetch_analytics(da: DataAccess, ticker: str) -> Dict[str, Any]:
    """Fetch analytics files."""
    content = da.read_analytics(ticker)
    return {"analytics": content}


def _fetch_prices(da: DataAccess, ticker: str) -> Dict[str, Any]:
    """Fetch price data."""
    prices = da.read_price_data(ticker)
    return {"prices": prices}


def _fetch_news_list(da: DataAccess, ticker: str) -> Dict[str, Any]:
    """Fetch news file list."""
    news_files = da.list_news_files(ticker, limit=20)
    return {"news_files": news_files}


def _calculate_quality(
    ticker: str,
    results: Dict,
    da: DataAccess,
    max_age_hours: int
) -> Dict[str, Any]:
    """Calculate overall quality scores."""
    # Score each data source
    analytics_quality = score_analytics_files(ticker, max_age_hours, da)
    price_quality = score_price_data(ticker, da)
    news_quality = score_news_data(ticker, max_age_hours=168, data_access=da)

    # Calculate overall quality (weighted)
    overall = int(
        analytics_quality.overall * 0.5 +
        price_quality.overall * 0.3 +
        news_quality.overall * 0.2
    )

    # Determine action based on lowest quality component
    scores = {
        "analytics": analytics_quality.overall,
        "prices": price_quality.overall,
        "news": news_quality.overall
    }
    min_score = min(scores.values())

    if min_score < 40:
        action = "REFRESH_REQUIRED"
    elif min_score < 60:
        action = "REFRESH_RECOMMENDED"
    elif min_score < 80:
        action = "PROCEED_WITH_WEB_SEARCH"
    else:
        action = "PROCEED"

    return {
        "overall": overall,
        "analytics": analytics_quality.overall,
        "prices": price_quality.overall,
        "news": news_quality.overall,
        "action": action,
        "breakdown": {
            "analytics": analytics_quality.breakdown,
            "analytics_freshness": analytics_quality.freshness,
            "analytics_completeness": analytics_quality.completeness,
            "price_freshness": price_quality.freshness,
        }
    }


# ========== Async Variant ==========

async def fetch_all_data_async(
    ticker: str,
    data_access: Optional[DataAccess] = None,
    score_quality: bool = True,
    max_age_hours: int = 24
) -> DataFetchResult:
    """
    Async variant of fetch_all_data.

    Uses asyncio for I/O-bound operations in async contexts.
    """
    loop = asyncio.get_event_loop()
    da = data_access or DataAccess()

    # Run blocking fetch in executor
    result = await loop.run_in_executor(
        None,
        lambda: fetch_all_data(ticker, da, score_quality, max_age_hours)
    )

    return result
