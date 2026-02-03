"""
Quality scoring for analytics and data.

Replaces binary fresh/stale validation with 0-100 quality scoring
based on freshness, completeness, and accuracy.
"""
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from .data_access import AnalyticsFiles, DataAccess, get_file_age_hours


@dataclass
class QualityScore:
    """
    Quality score with breakdown.

    Attributes:
        overall: 0-100 overall quality score
        freshness: 0-100 based on data age
        completeness: 0-100 based on required fields present
        accuracy: 0-100 based on data validation
        breakdown: Detailed scoring breakdown
        action: Recommended action based on score
        timestamp: When the score was calculated
    """
    overall: int
    freshness: int
    completeness: int
    accuracy: int
    breakdown: Dict[str, int] = field(default_factory=dict)
    action: str = "UNKNOWN"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def is_acceptable(self, threshold: int = 60) -> bool:
        """Check if quality score meets threshold."""
        return self.overall >= threshold

    def is_excellent(self) -> bool:
        """Check if quality is excellent (80+)."""
        return self.overall >= 80

    def needs_refresh(self) -> bool:
        """Check if data should be refreshed."""
        return self.overall < 60


# Required sections for each analytics file type
REQUIRED_SECTIONS = {
    "technical": [
        "Price Action", "Moving Average", "Trend", "Support", "Resistance",
        "Momentum", "Signal", "Dashboard"
    ],
    "fundamental": [
        "Valuation", "Financial", "Growth", "Profitability", "Health",
        "Metrics", "Margin", "ROE", "Debt"
    ],
    "thesis": [
        "Thesis", "Investment", "Bull", "Bear", "Catalyst", "Target",
        "Upside", "Strategy", "Risk"
    ]
}


def score_analytics_files(
    ticker: str,
    max_age_hours: int = 24,
    data_access: Optional[DataAccess] = None
) -> QualityScore:
    """
    Score analytics files on 0-100 scale.

    Scoring weights:
    - Freshness (40%): How recent is the data?
    - Completeness (30%): Are all required sections present?
    - Accuracy (30%): Does data validate correctly?

    Args:
        ticker: Stock ticker symbol
        max_age_hours: Maximum age for full freshness score
        data_access: Optional DataAccess instance

    Returns:
        QualityScore with detailed breakdown
    """
    da = data_access or DataAccess()
    files = da.get_analytics_files(ticker)

    scores = {
        "technical": {"freshness": 0, "completeness": 0, "accuracy": 0},
        "fundamental": {"freshness": 0, "completeness": 0, "accuracy": 0},
        "thesis": {"freshness": 0, "completeness": 0, "accuracy": 0},
    }

    # Score each file
    for file_type in ["technical", "fundamental", "thesis"]:
        file_path = getattr(files, file_type)
        if file_path and file_path.exists():
            scores[file_type]["freshness"] = _score_freshness(
                file_path, max_age_hours
            )
            scores[file_type]["completeness"] = _score_completeness(
                file_path, file_type
            )
            scores[file_type]["accuracy"] = _score_accuracy(file_path)

    # Aggregate scores (weighted average)
    avg_freshness = _average_score(scores, "freshness")
    avg_completeness = _average_score(scores, "completeness")
    avg_accuracy = _average_score(scores, "accuracy")

    # Calculate overall (40% freshness, 30% completeness, 30% accuracy)
    overall = int(
        avg_freshness * 0.4 +
        avg_completeness * 0.3 +
        avg_accuracy * 0.3
    )

    # Determine action
    action = _get_action_for_score(overall)

    return QualityScore(
        overall=overall,
        freshness=avg_freshness,
        completeness=avg_completeness,
        accuracy=avg_accuracy,
        breakdown={
            f"{k}_{metric}": v
            for k, metrics in scores.items()
            for metric, v in metrics.items()
        },
        action=action
    )


def score_price_data(
    ticker: str,
    data_access: Optional[DataAccess] = None
) -> QualityScore:
    """
    Score price data quality.

    Args:
        ticker: Stock ticker symbol
        data_access: Optional DataAccess instance

    Returns:
        QualityScore for price data
    """
    da = data_access or DataAccess()
    price_path = da.get_price_csv(ticker)

    if not price_path or not price_path.exists():
        return QualityScore(
            overall=0, freshness=0, completeness=0, accuracy=0,
            action="REFRESH_REQUIRED"
        )

    # Freshness: based on how recent the last data point is
    freshness = _score_freshness(price_path, max_age_hours=48)  # 2 days for prices

    # Completeness: based on data point count
    if HAS_PANDAS:
        try:
            df = pd.read_csv(price_path)
            data_points = len(df)
            # 500+ days = 100, 250+ days = 80, etc.
            if data_points >= 500:
                completeness = 100
            elif data_points >= 252:  # ~1 trading year
                completeness = 80
            elif data_points >= 126:  # ~6 months
                completeness = 60
            elif data_points >= 30:
                completeness = 40
            else:
                completeness = 20
        except Exception:
            completeness = 0
    else:
        completeness = 50  # Can't verify without pandas

    # Accuracy: basic validation
    try:
        with open(price_path) as f:
            first_line = f.readline()
            has_header = "date" in first_line.lower() or "Date" in first_line
        accuracy = 100 if has_header else 50
    except Exception:
        accuracy = 0

    overall = int((freshness * 0.4 + completeness * 0.4 + accuracy * 0.2))

    return QualityScore(
        overall=overall,
        freshness=freshness,
        completeness=completeness,
        accuracy=accuracy,
        action=_get_action_for_score(overall)
    )


def score_news_data(
    ticker: str,
    max_age_hours: int = 168,  # 1 week
    data_access: Optional[DataAccess] = None
) -> QualityScore:
    """
    Score news data quality for a ticker.

    Args:
        ticker: Stock ticker symbol
        max_age_hours: Maximum age for fresh news
        data_access: Optional DataAccess instance

    Returns:
        QualityScore for news data
    """
    da = data_access or DataAccess()
    news_files = da.list_news_files(ticker, limit=100)

    if not news_files:
        return QualityScore(
            overall=0, freshness=0, completeness=0, accuracy=0,
            action="REFRESH_REQUIRED"
        )

    # Freshness: age of most recent news
    latest_age = news_files[0].age_hours
    if latest_age <= 24:
        freshness = 100
    elif latest_age <= 72:  # 3 days
        freshness = 75
    elif latest_age <= max_age_hours:
        freshness = 50
    else:
        freshness = 25

    # Completeness: number of articles
    article_count = len(news_files)
    if article_count >= 20:
        completeness = 100
    elif article_count >= 10:
        completeness = 75
    elif article_count >= 5:
        completeness = 50
    elif article_count >= 1:
        completeness = 25
    else:
        completeness = 0

    # Accuracy: check file structure
    valid_count = sum(
        1 for f in news_files
        if f.path.exists() and f.path.stat().st_size > 100
    )
    accuracy = int((valid_count / article_count) * 100) if article_count > 0 else 0

    overall = int((freshness * 0.5 + completeness * 0.3 + accuracy * 0.2))

    return QualityScore(
        overall=overall,
        freshness=freshness,
        completeness=completeness,
        accuracy=accuracy,
        action=_get_action_for_score(overall)
    )


# ========== Internal Helpers ==========

def _score_freshness(path: Path, max_age_hours: int = 24) -> int:
    """Calculate freshness score (0-100)."""
    age_hours = get_file_age_hours(path)

    if age_hours <= max_age_hours * 0.25:
        return 100  # Very fresh
    elif age_hours <= max_age_hours * 0.5:
        return 90
    elif age_hours <= max_age_hours:
        return 75  # Fresh
    elif age_hours <= max_age_hours * 2:
        return 50  # Getting stale
    elif age_hours <= max_age_hours * 4:
        return 25  # Stale
    else:
        return 10  # Very stale


def _score_completeness(path: Path, file_type: str) -> int:
    """Calculate completeness score (0-100)."""
    try:
        content = path.read_text()
    except Exception:
        return 0

    required_keywords = REQUIRED_SECTIONS.get(file_type, [])
    if not required_keywords:
        return 100  # No requirements defined

    # Count how many required keywords/phrases are present
    present = sum(
        1 for keyword in required_keywords
        if keyword.lower() in content.lower()
    )

    # Also check for reasonable file size
    size_score = 100 if len(content) > 500 else 50

    keyword_score = (present / len(required_keywords)) * 100
    return int((keyword_score * 0.8 + size_score * 0.2))


def _score_accuracy(path: Path) -> int:
    """Calculate accuracy score via validation (0-100)."""
    try:
        content = path.read_text()
    except Exception:
        return 0

    checks = []

    # Check for markdown headers
    has_headers = bool(re.search(r'^#+\s+\w+', content, re.MULTILINE))
    checks.append(100 if has_headers else 50)

    # Check for data/content
    has_data = len(content) > 300
    checks.append(100 if has_data else 30)

    # Check for structured sections
    has_sections = content.count("##") >= 2
    checks.append(100 if has_sections else 50)

    return int(sum(checks) / len(checks)) if checks else 0


def _average_score(scores: Dict, metric: str) -> int:
    """Calculate average score across all file types for a metric."""
    values = [
        file_scores[metric]
        for file_scores in scores.values()
        if file_scores[metric] > 0
    ]
    if not values:
        return 0
    return int(sum(values) / len(values))


def _get_action_for_score(score: int) -> str:
    """Get recommended action based on quality score."""
    if score >= 80:
        return "PROCEED"
    elif score >= 60:
        return "PROCEED_WITH_WEB_SEARCH"
    elif score >= 40:
        return "REFRESH_RECOMMENDED"
    else:
        return "REFRESH_REQUIRED"
