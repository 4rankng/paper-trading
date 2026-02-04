"""
Common utilities for portfolio management scripts.

Multi-Portfolio Architecture (v3.0 Minimal):
- Uses filedb/portfolios.json with multiple portfolios
- SHARED cash pool at top level (all portfolios share the same cash)
- Portfolios only contain MINIMAL stock position data (ticker, shares, avg_cost, current_price, status)
- All analysis data (thesis, sector, machine_type, etc.) stored in filedb/analytics/[TICKER]/ folder

Structure:
{
  "cash": {"amount": 1000.00, "target_buffer_pct": 15},
  "portfolios": {
    "CORE": {
      "name": "Core Holdings",
      "description": "...",
      "config": {...},
      "holdings": [
        {
          "ticker": "TICKER",
          "shares": 100,
          "avg_cost": 10.50,
          "current_price": 12.00,
          "status": "active"
        }
      ],
      "summary": {...}
    }
  },
  "metadata": {"default_portfolio": "CORE", "version": "3.0"}
}

IMPORTANT: filedb/portfolios.json is for MINIMAL data only.
Analysis data lives in filedb/analytics/[TICKER]/:
  - {TICKER}_investment_thesis.md
  - {TICKER}_technical_analysis.md
  - {TICKER}_fundamental_analysis.md
  - price.csv (historical prices in filedb/prices/)
"""
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

# Add shared module to path
# common.py is at .claude/skills/portfolio_manager/scripts/
# parents[0]=scripts, [1]=portfolio_manager, [2]=skills, [3]=.claude
# Add .claude to sys.path so we can import as "shared.project"
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

try:
    from shared.project import get_project_root, get_filedb_dir
    from shared.data_access import DataAccess as _DataAccess
    from shared.validators import validate_portfolio_structure as _validate_portfolio_structure
    SHARED_AVAILABLE = True
except ImportError:
    SHARED_AVAILABLE = False

    def get_project_root() -> Path:
        """Get the project root directory (my-stock-advisor)."""
        current = Path(__file__).resolve().parent
        # Walk up max 6 levels looking for project markers
        for _ in range(6):
            if (current / ".git").exists():
                return current
            if (current / "watchlist.json").exists():
                return current
            if (current / "filedb").exists():
                return current
            parent = current.parent
            if parent == current:  # reached root
                break
            current = parent
        # Fallback: use original logic
        current_path = Path(__file__).resolve()
        if "skills" in current_path.parts:
            skills_idx = current_path.parts.index("skills")
            parts = list(current_path.parts[:skills_idx - 1])
            # Filter out empty strings from Path parts
            parts = [p for p in parts if p]
            return Path(*parts) if parts else Path.cwd()
        return Path.cwd()

    def get_filedb_dir() -> Path:
        """Get the filedb directory."""
        root = get_project_root()
        return root / "filedb"


def load_portfolios(path: Path | None = None) -> dict:
    """Load portfolios.json from filedb/."""
    if path is None:
        path = get_filedb_dir() / "portfolios.json"
    if not path.exists():
        raise FileNotFoundError(f"Portfolios not found: {path}")
    with open(path) as f:
        return json.load(f)


def save_portfolios(portfolios: dict, path: Path | None = None) -> None:
    """Save portfolios.json to filedb/."""
    if path is None:
        path = get_filedb_dir() / "portfolios.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(portfolios, f, indent=2)


def get_shared_cash(path: Path | None = None) -> dict:
    """Get the shared cash pool from filedb/portfolios.json.

    Args:
        path: Path to portfolios.json

    Returns:
        Dict with amount and target_buffer_pct
    """
    if path is None:
        path = get_filedb_dir() / "portfolios.json"
    if not path.exists():
        raise FileNotFoundError(f"Portfolios not found: {path}")

    portfolios = json.load(open(path))
    return portfolios.get("cash", {"amount": 0.0, "target_buffer_pct": 15})


def update_shared_cash(amount: float, path: Path | None = None) -> None:
    """Update the shared cash pool amount.

    Args:
        amount: New cash amount
        path: Path to portfolios.json
    """
    if path is None:
        path = get_filedb_dir() / "portfolios.json"

    portfolios = load_portfolios(path)
    portfolios["cash"]["amount"] = round(amount, 2)
    portfolios["metadata"]["last_updated"] = datetime.now().isoformat()

    save_portfolios(portfolios, path)


def get_portfolio(portfolio_name: str | None = None, path: Path | None = None, include_cash: bool = True) -> dict:
    """Get a specific portfolio from filedb/portfolios.json.

    Args:
        portfolio_name: Name of portfolio (e.g., "CORE", "AI_PICKS").
                      If None, returns the default portfolio from metadata.
        path: Path to portfolios.json
        include_cash: If True, include shared cash in returned dict

    Returns:
        Portfolio dict with holdings, config, summary keys.
        If include_cash=True, also includes _shared_cash dict.

    Raises:
        FileNotFoundError: If portfolios.json doesn't exist
        ValueError: If portfolio_name not found
    """
    if path is None:
        path = get_filedb_dir() / "portfolios.json"
    if not path.exists():
        raise FileNotFoundError(f"Portfolios not found: {path}")

    portfolios = json.load(open(path))

    if portfolio_name is None:
        portfolio_name = portfolios.get("metadata", {}).get("default_portfolio", "CORE")

    if portfolio_name not in portfolios.get("portfolios", {}):
        available = list(portfolios.get("portfolios", {}).keys())
        raise ValueError(f"Portfolio '{portfolio_name}' not found. Available: {available}")

    result = portfolios["portfolios"][portfolio_name].copy()

    # Add shared cash if requested (for calculations)
    if include_cash:
        result["_shared_cash"] = portfolios.get("cash", {"amount": 0.0, "target_buffer_pct": 15})

    return result


def list_portfolios(path: Path | None = None) -> dict:
    """List all available portfolios with shared cash info.

    Returns:
        Dict with shared_cash and portfolios list
    """
    if path is None:
        path = get_filedb_dir() / "portfolios.json"
    if not path.exists():
        return {"shared_cash": {"amount": 0, "target_buffer_pct": 15}, "portfolios": []}

    portfolios = json.load(open(path))
    result = {"shared_cash": portfolios.get("cash", {"amount": 0, "target_buffer_pct": 15}), "portfolios": []}

    for name, data in portfolios.get("portfolios", {}).items():
        summary = data.get("summary", {})
        result["portfolios"].append({
            "name": name,
            "description": data.get("description", ""),
            "holdings_value": summary.get("holdings_value", 0),
            "total_cost_basis": summary.get("total_cost_basis", 0),
            "holdings_count": summary.get("holdings_count", 0),
            "total_gain_loss": summary.get("total_gain_loss", 0),
            "total_gain_loss_pct": summary.get("total_gain_loss_pct", 0),
        })

    return result


def recalculate_portfolio_totals(portfolio: dict, shared_cash: float | dict | None = None) -> dict:
    """Recalculate holdings totals and position percentages.

    Args:
        portfolio: Portfolio dict with holdings
        shared_cash: Either cash amount (float) or cash dict with 'amount' key.
                     If None, looks for _shared_cash in portfolio (set by get_portfolio).

    Returns:
        Updated portfolio dict

    Note: Position percentages are calculated as: position / (holdings_value + shared_cash)
    """
    holdings = portfolio.get("holdings", [])

    # Get shared cash amount
    cash_amount = 0
    if shared_cash is not None:
        if isinstance(shared_cash, dict):
            cash_amount = shared_cash.get("amount", 0)
        else:
            cash_amount = shared_cash
    elif "_shared_cash" in portfolio:
        cash_amount = portfolio["_shared_cash"].get("amount", 0)

    # Update each holding's market_value and gain_loss
    total_cost = 0
    total_gl = 0
    for h in holdings:
        shares = h.get("shares", 0)
        avg_cost = h.get("avg_cost", 0)
        current_price = h.get("current_price", avg_cost)

        market_value = shares * current_price
        cost_basis = shares * avg_cost
        gain_loss = market_value - cost_basis
        gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0

        h["market_value"] = round(market_value, 2)
        h["gain_loss"] = round(gain_loss, 2)
        h["gain_loss_pct"] = round(gain_loss_pct, 2)

        total_cost += cost_basis
        total_gl += gain_loss

    total_holdings_value = sum(h["market_value"] for h in holdings)
    total_value = total_holdings_value + cash_amount

    # Update summary
    portfolio["summary"] = portfolio.get("summary", {})
    portfolio["summary"]["holdings_value"] = round(total_holdings_value, 2)
    portfolio["summary"]["total_cost_basis"] = round(total_cost, 2)
    portfolio["summary"]["total_gain_loss"] = round(total_gl, 2)
    portfolio["summary"]["total_gain_loss_pct"] = round((total_gl / total_cost) * 100, 2) if total_cost > 0 else 0
    portfolio["summary"]["holdings_count"] = len(holdings)

    # Update position percentages (includes shared cash in denominator)
    for h in holdings:
        h["pct_portfolio"] = round((h["market_value"] / total_value) * 100, 2) if total_value > 0 else 0

    return portfolio


def update_portfolio(portfolio_name: str, portfolio: dict, path: Path | None = None, shared_cash: float | dict | None = None) -> None:
    """Update a specific portfolio in portfolios.json.

    Args:
        portfolio_name: Name of portfolio to update (e.g., "CORE", "AI_PICKS")
        portfolio: Portfolio dict with updated data
        path: Path to portfolios.json
        shared_cash: Optional shared cash amount/dict for position % calculations
    """
    if path is None:
        path = get_project_root() / "portfolios.json"

    portfolios = load_portfolios(path)

    # Remove temporary _shared_cash if present (it's only for calculation)
    clean_portfolio = {k: v for k, v in portfolio.items() if k != "_shared_cash"}

    # Recalculate with shared cash
    portfolios["portfolios"][portfolio_name] = recalculate_portfolio_totals(
        clean_portfolio, shared_cash or portfolios.get("cash", {}).get("amount", 0)
    )
    portfolios["metadata"]["last_updated"] = datetime.now().isoformat()

    save_portfolios(portfolios, path)


def format_currency(value: float) -> str:
    """Format a number as currency."""
    return f"${value:,.2f}"


def format_percent(value: float) -> str:
    """Format a number as percentage."""
    return f"{value:+.2f}%"


def validate_portfolio_structure(portfolio: dict) -> tuple[bool, list[str]]:
    """Validate portfolio has required v3.0 minimal structure.

    Args:
        portfolio: Portfolio dict to validate

    Returns:
        (is_valid, list of error messages)
    """
    errors = []

    # Check required top-level keys
    required_keys = ["holdings", "summary"]

    for key in required_keys:
        if key not in portfolio:
            errors.append(f"Missing required key: {key}")

    # Validate holdings - MINIMAL schema only
    if "holdings" in portfolio:
        if not isinstance(portfolio["holdings"], list):
            errors.append("holdings must be a list")
        else:
            # v3.0 minimal required keys
            required_holding_keys = ["ticker", "shares", "avg_cost", "current_price"]
            for i, h in enumerate(portfolio["holdings"]):
                if not isinstance(h, dict):
                    errors.append(f"holdings[{i}] must be a dict")
                    continue
                for key in required_holding_keys:
                    if key not in h:
                        errors.append(f"holdings[{i}].{key} is required")

                # Warn if analysis fields present (should be in analytics/ folder)
                analysis_fields = [
                    "name", "sector", "industry", "machine_type", "time_horizon",
                    "thesis_status", "thesis_validation_confidence", "contracts_validated",
                    "sell_signal_triggered", "invalidation_level", "technical_alignment",
                    "thesis", "major_partnerships", "council_analysis", "key_metrics",
                    "last_news_update"
                ]
                for field in analysis_fields:
                    if field in h:
                        errors.append(f"holdings[{i}].{field} should be in analytics/{h.get('ticker', 'TICKER')}/ not portfolios.json")

    # Validate summary
    if "summary" in portfolio:
        if not isinstance(portfolio["summary"], dict):
            errors.append("summary must be a dict")
        else:
            required_summary_keys = ["holdings_value"]
            for key in required_summary_keys:
                if key not in portfolio["summary"]:
                    errors.append(f"summary.{key} is required")

    return len(errors) == 0, errors


def ensure_portfolio_structure(portfolio: dict) -> dict:
    """Ensure portfolio has all required keys, filling in defaults if missing."""
    # Ensure holdings
    if "holdings" not in portfolio:
        portfolio["holdings"] = []

    # Ensure summary
    if "summary" not in portfolio:
        portfolio["summary"] = {}

    return portfolio


def log_trade(
    ticker: str,
    action: str,
    shares: int,
    price: float,
    cost_basis: float,
    portfolio_pct: float,
    thesis_status: str,
    reasoning: str,
    evidence_files: list = None,
    timestamp: str = None,
    trade_log_path: Path = None,
    portfolio_name: str = "CORE",
) -> dict:
    """
    Log a trade to filedb/trade_log.csv with portfolio_name support.

    Returns:
        dict with trade details
    """
    if trade_log_path is None:
        trade_log_path = get_filedb_dir() / "trade_log.csv"
        trade_log_path.parent.mkdir(parents=True, exist_ok=True)

    if timestamp is None:
        timestamp = datetime.now().isoformat()

    trade = {
        "timestamp": timestamp,
        "portfolio": portfolio_name,
        "ticker": ticker,
        "action": action,
        "shares": shares,
        "price": price,
        "cost_basis": cost_basis,
        "portfolio_pct": portfolio_pct,
        "thesis_status": thesis_status,
        "reasoning": reasoning,
        "evidence_files": ",".join(evidence_files or []),
    }

    file_exists = trade_log_path.exists()

    # Check if file needs header update (for portfolio column)
    needs_header = not file_exists
    if file_exists:
        with open(trade_log_path, 'r') as f:
            first_line = f.readline().strip()
            if "portfolio" not in first_line:
                # Need to rewrite with new header
                import shutil
                temp_path = trade_log_path.with_suffix('.tmp')
                with open(trade_log_path, 'r') as f_in:
                    reader = csv.DictReader(f_in)
                    rows = list(reader)
                with open(temp_path, 'w', newline='') as f_out:
                    writer = csv.DictWriter(f_out, fieldnames=list(rows[0].keys()) + ["portfolio"] if rows else ["portfolio"])
                    if rows:
                        writer.writeheader()
                    for row in rows:
                        row["portfolio"] = portfolio_name
                        writer.writerow(row)
                shutil.move(temp_path, trade_log_path)
                needs_header = False

    with open(trade_log_path, "a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "portfolio",
                "ticker",
                "action",
                "shares",
                "price",
                "cost_basis",
                "portfolio_pct",
                "thesis_status",
                "reasoning",
                "evidence_files",
            ],
        )
        if needs_header:
            writer.writeheader()
        writer.writerow(trade)

    return trade
