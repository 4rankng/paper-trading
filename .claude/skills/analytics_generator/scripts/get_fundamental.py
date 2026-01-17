#!/usr/bin/env python3
import yfinance as yf
import json
import sys

# Critical fields required for basic fundamental analysis
CRITICAL_FIELDS = ["market_cap", "current_price", "sector", "industry"]

# All fields we attempt to fetch
ALL_FIELDS = [
    "market_cap", "shares_outstanding", "current_price",
    "fifty_two_week_low", "fifty_two_week_high", "fifty_two_week_change",
    "trailing_pe", "forward_pe", "price_to_sales",
    "profit_margins", "operating_margins", "gross_margins",
    "quarterly_revenue_growth_yoy",
    "total_cash", "total_debt", "debt_to_equity", "current_ratio", "return_on_equity",
    "sector", "industry", "beta",
]

# Mapping from our field names to yfinance info keys
YFINANCE_MAP = {
    "market_cap": "marketCap",
    "shares_outstanding": "sharesOutstanding",
    "current_price": "currentPrice",
    "fifty_two_week_low": "fiftyTwoWeekLow",
    "fifty_two_week_high": "fiftyTwoWeekHigh",
    "fifty_two_week_change": "fiftyTwoWeekChange",
    "trailing_pe": "trailingPE",
    "forward_pe": "forwardPE",
    "price_to_sales": "priceToSalesTrailing12Months",
    "profit_margins": "profitMargins",
    "operating_margins": "operatingMargins",
    "gross_margins": "grossMargins",
    "quarterly_revenue_growth_yoy": "quarterlyRevenueGrowthYoY",
    "total_cash": "totalCash",
    "total_debt": "totalDebt",
    "debt_to_equity": "debtToEquity",
    "current_ratio": "currentRatio",
    "return_on_equity": "returnOnEquity",
    "sector": "sector",
    "industry": "industry",
    "beta": "beta",
}


def validate_data(data: dict) -> dict:
    """
    Validate fundamental data and return quality metrics.

    Returns a dict with:
    - completeness_pct: percentage of fields with non-null values
    - critical_fields_present: boolean indicating if all critical fields have data
    - warnings: list of warning messages
    - missing_critical: list of critical field names that are None
    - missing_optional: list of optional field names that are None
    """
    warnings = []
    missing_critical = []
    missing_optional = []

    # Check critical fields
    for field in CRITICAL_FIELDS:
        value = data.get(field)
        if value is None:
            missing_critical.append(field)

    # Check optional fields
    optional_fields = [f for f in ALL_FIELDS if f not in CRITICAL_FIELDS]
    for field in optional_fields:
        value = data.get(field)
        if value is None:
            missing_optional.append(field)

    # Calculate completeness
    non_null_count = sum(1 for field in ALL_FIELDS if data.get(field) is not None)
    completeness_pct = int((non_null_count / len(ALL_FIELDS)) * 100)

    # Generate warnings
    if missing_critical:
        warnings.append(f"Missing {len(missing_critical)} critical field(s): {', '.join(missing_critical)}")

    if len(missing_optional) > 3:
        warnings.append(f"Missing {len(missing_optional)} optional field(s)")

    if completeness_pct < 50:
        warnings.append(f"Data completeness ({completeness_pct}%) is below 50% - analysis may be unreliable")

    return {
        "completeness_pct": completeness_pct,
        "critical_fields_present": len(missing_critical) == 0,
        "warnings": warnings,
        "missing_critical": missing_critical,
        "missing_optional": missing_optional,
    }


ticker = None
if len(sys.argv) > 2 and sys.argv[1] == "--ticker":
    ticker = sys.argv[2]

if not ticker:
    ticker = input("Enter ticker symbol: ").strip()

stock = yf.Ticker(ticker)
info = stock.info

# Fetch all data using mapping
data = {"ticker": ticker.upper()}
for field, yf_key in YFINANCE_MAP.items():
    data[field] = info.get(yf_key)

# Validate data
data_quality = validate_data(data)

# Add validation metadata to output
data["data_quality"] = data_quality

# Print warnings to stderr for human visibility
if data_quality["warnings"]:
    for warning in data_quality["warnings"]:
        print(f"WARNING: {warning}", file=sys.stderr)

# Output JSON
print(json.dumps(data, indent=2, default=str))

# Exit with error code if critical fields missing
if not data_quality["critical_fields_present"]:
    sys.exit(1)
