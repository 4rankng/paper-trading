"""
Shared validation functions for stock advisor data.

Provides common validation logic used across multiple skills.
"""
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .data_access import AnalyticsFiles, DataAccess, get_file_age_hours


@dataclass
class ValidationResult:
    """
    Result of a validation operation.

    Attributes:
        valid: Whether validation passed
        errors: List of error messages
        warnings: List of warning messages
        details: Additional validation details
    """
    valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        """Add an error message and mark as invalid."""
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)


def validate_ticker(ticker: str) -> ValidationResult:
    """
    Validate a ticker symbol.

    Args:
        ticker: Ticker symbol to validate

    Returns:
        ValidationResult with errors if invalid
    """
    result = ValidationResult()

    if not ticker:
        result.add_error("Ticker is empty")
        return result

    # Check length
    if len(ticker) > 10:
        result.add_error(f"Ticker too long: {ticker}")

    # Check for valid characters (letters, numbers, dot, hyphen)
    if not re.match(r'^[A-Za-z0-9.\-]{1,10}$', ticker):
        result.add_error(f"Ticker contains invalid characters: {ticker}")

    return result


def validate_analytics_structure(
    ticker: str,
    data_access: Optional[DataAccess] = None,
    max_age_hours: int = 24
) -> ValidationResult:
    """
    Validate analytics files exist, are fresh, and have content.

    Args:
        ticker: Stock ticker symbol
        data_access: Optional DataAccess instance
        max_age_hours: Maximum age for freshness check

    Returns:
        ValidationResult with any issues found
    """
    da = data_access or DataAccess()
    files = da.get_analytics_files(ticker)
    result = ValidationResult()

    # Check each required file
    required_files = {
        "technical": files.technical,
        "fundamental": files.fundamental,
        "thesis": files.thesis,
    }

    for file_type, filepath in required_files.items():
        if not filepath or not filepath.exists():
            result.add_error(f"Missing {file_type}: {filepath}")
            continue

        # Check file age
        age_hours = get_file_age_hours(filepath)
        result.details[f"{file_type}_age_hours"] = round(age_hours, 1)

        if age_hours > max_age_hours:
            result.add_warning(
                f"Stale {file_type}: {age_hours:.1f}h old (max {max_age_hours}h)"
            )

        # Check file not empty
        if filepath.stat().st_size == 0:
            result.add_error(f"Empty {file_type}: {filepath}")

        # Check file has reasonable content
        if filepath.stat().st_size < 200:
            result.add_warning(
                f"Small {file_type}: {filepath.stat().st_size} bytes"
            )

    # Check price data
    if files.price_csv and files.price_csv.exists():
        price_age = get_file_age_hours(files.price_csv)
        result.details["price_age_hours"] = round(price_age, 1)
    else:
        result.add_warning("No price data file found")

    return result


def validate_portfolio_structure(portfolio: Dict) -> ValidationResult:
    """
    Validate portfolio has required v3.0 minimal structure.

    Args:
        portfolio: Portfolio dict to validate

    Returns:
        ValidationResult with any issues
    """
    result = ValidationResult()

    # Check required top-level keys
    required_keys = ["holdings"]
    for key in required_keys:
        if key not in portfolio:
            result.add_error(f"Missing required key: {key}")

    # Validate holdings
    if "holdings" in portfolio:
        if not isinstance(portfolio["holdings"], list):
            result.add_error("holdings must be a list")
        else:
            for i, h in enumerate(portfolio["holdings"]):
                if not isinstance(h, dict):
                    result.add_error(f"holdings[{i}] must be a dict")
                    continue

                # Check required holding keys
                required_keys = ["ticker", "shares", "avg_cost", "current_price"]
                for key in required_keys:
                    if key not in h:
                        result.add_error(f"holdings[{i}].{key} is required")

                # Warn if analysis fields present (should be in analytics/)
                analysis_fields = [
                    "name", "sector", "industry", "machine_type", "time_horizon",
                    "thesis_status", "thesis_validation_confidence", "contracts_validated",
                    "sell_signal_triggered", "invalidation_level", "technical_alignment",
                    "thesis", "major_partnerships", "council_analysis", "key_metrics",
                ]
                for field in analysis_fields:
                    if field in h:
                        ticker = h.get("ticker", "TICKER")
                        result.add_warning(
                            f"holdings[{i}].{field} should be in analytics/{ticker}/"
                        )

    return result


def validate_watchlist_structure(watchlist: Dict) -> ValidationResult:
    """
    Validate watchlist has correct structure.

    Args:
        watchlist: Watchlist dict to validate

    Returns:
        ValidationResult with any issues
    """
    result = ValidationResult()

    # Check for tickers key
    if "tickers" not in watchlist:
        result.add_error("Missing 'tickers' key")
        return result

    if not isinstance(watchlist["tickers"], dict):
        result.add_error("'tickers' must be a dict")
        return result

    # Validate each ticker entry
    for ticker, data in watchlist["tickers"].items():
        if not isinstance(data, dict):
            result.add_error(f"watchlist['{ticker}'] must be a dict")
            continue

        # Check for required fields
        if "fit" in data:
            try:
                fit_value = float(data["fit"])
                if not 0 <= fit_value <= 100:
                    result.add_warning(
                        f"watchlist['{ticker}'].fit should be 0-100, got {fit_value}"
                    )
            except (ValueError, TypeError):
                result.add_error(f"watchlist['{ticker}'].fit must be a number")

    return result


def validate_price_csv(path: Path) -> ValidationResult:
    """
    Validate price CSV file structure.

    Args:
        path: Path to price CSV file

    Returns:
        ValidationResult with any issues
    """
    result = ValidationResult()

    if not path.exists():
        result.add_error(f"File does not exist: {path}")
        return result

    # Check file size
    if path.stat().st_size == 0:
        result.add_error(f"File is empty: {path}")
        return result

    # Try to read and validate structure
    try:
        with open(path) as f:
            first_line = f.readline().strip()
            second_line = f.readline().strip()

        # Check for header
        if "date" not in first_line.lower():
            result.add_warning(f"Missing 'date' column in header: {path}")

        # Check for data rows
        if not second_line:
            result.add_error(f"No data rows in: {path}")
        else:
            # Check expected column count
            cols = first_line.split(",")
            if len(cols) < 5:
                result.add_warning(
                    f"Expected at least 5 columns, got {len(cols)}"
                )

    except Exception as e:
        result.add_error(f"Error reading file: {e}")

    return result


def validate_news_file(path: Path) -> ValidationResult:
    """
    Validate news file has required YAML frontmatter.

    Args:
        path: Path to news markdown file

    Returns:
        ValidationResult with any issues
    """
    result = ValidationResult()

    if not path.exists():
        result.add_error(f"File does not exist: {path}")
        return result

    try:
        content = path.read_text()
    except Exception as e:
        result.add_error(f"Error reading file: {e}")
        return result

    # Check for YAML frontmatter
    if not content.startswith("---"):
        result.add_warning(f"Missing YAML frontmatter: {path}")
    else:
        # Extract frontmatter and check for required fields
        frontmatter_end = content.find("---", 3)
        if frontmatter_end == -1:
            result.add_error(f"Unclosed YAML frontmatter: {path}")
        else:
            frontmatter = content[3:frontmatter_end]
            required_fields = ["title", "date", "source"]

            for field in required_fields:
                if field not in frontmatter:
                    result.add_warning(
                        f"Missing frontmatter field '{field}': {path}"
                    )

    # Check file has content
    if len(content) < 100:
        result.add_warning(f"File content very short: {path}")

    return result


def validate_data_freshness(
    ticker: str,
    max_age_hours: int = 24,
    data_access: Optional[DataAccess] = None
) -> ValidationResult:
    """
    Validate all data for a ticker is fresh.

    Args:
        ticker: Stock ticker symbol
        max_age_hours: Maximum age for data to be considered fresh
        data_access: Optional DataAccess instance

    Returns:
        ValidationResult with freshness issues
    """
    da = data_access or DataAccess()
    files = da.get_analytics_files(ticker)
    result = ValidationResult()

    # Check analytics files
    for file_type in ["technical", "fundamental", "thesis"]:
        filepath = getattr(files, file_type)
        if filepath and filepath.exists():
            age_hours = get_file_age_hours(filepath)
            if age_hours > max_age_hours:
                result.add_error(
                    f"{file_type} is {age_hours:.1f}h old (max {max_age_hours}h)"
                )

    # Check price data
    if files.price_csv and files.price_csv.exists():
        price_age = get_file_age_hours(files.price_csv)
        if price_age > max_age_hours * 2:  # Allow price data to be 2x as old
            result.add_warning(
                f"Price data is {price_age:.1f}h old (max {max_age_hours * 2}h)"
            )

    return result
