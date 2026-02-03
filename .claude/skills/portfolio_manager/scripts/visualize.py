#!/usr/bin/env python3
"""
Visualization scripts for stock advisor.

Features:
- Price charts with technical overlays
- Portfolio P&L waterfall
- Thesis status heatmaps

Requirements:
    pip install plotly matplotlib pandas

Usage:
    python visualize.py price-chart NVDA
    python visualize.py portfolio-waterfall CORE
    python visualize.py thesis-heatmap
"""
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Add shared module to path
# visualize.py is at .claude/skills/portfolio_manager/scripts/
# parents[0]=scripts, [1]=portfolio_manager, [2]=skills, [3]=.claude
# Add .claude to sys.path so we can import as "shared.data_access"
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

try:
    from shared.data_access import DataAccess, get_project_root
    SHARED_AVAILABLE = True
except ImportError:
    SHARED_AVAILABLE = False
    # Fallback implementations
    def get_project_root() -> Path:
        """Get the project root directory."""
        current = Path(__file__).resolve()
        markers = ['.git', 'watchlist.json', 'prices/', 'analytics/']
        for parent in [current, *current.parents]:
            if any((parent / m).exists() for m in markers):
                return parent
        if ".claude" in current.parts:
            idx = current.parts.index(".claude")
            return Path(*current.parts[:idx])
        raise RuntimeError("Project root not found")

    class DataAccess:
        """Minimal fallback DataAccess."""
        def __init__(self):
            self.root = get_project_root()
            self._prices_dir = self.root / "prices"

        def get_analytics_dir(self, ticker):
            return self.root / "analytics" / ticker

        def read_price_data(self, ticker):
            import pandas as pd
            price_path = self._prices_dir / f"{ticker}.csv"
            if price_path.exists():
                df = pd.read_csv(price_path, index_col='date', parse_dates=True)
                return df
            return None

        def read_analytics(self, ticker):
            files = self.get_analytics_files(ticker)
            return {
                "technical": self._read_file(files.technical),
                "fundamental": self._read_file(files.fundamental),
                "thesis": self._read_file(files.thesis),
            }

        def get_analytics_files(self, ticker):
            analytics_dir = self.get_analytics_dir(ticker)
            from dataclasses import dataclass
            @dataclass
            class AnalyticsFiles:
                technical: Path
                fundamental: Path
                thesis: Path
            return AnalyticsFiles(
                technical=analytics_dir / f"{ticker}_technical_analysis.md",
                fundamental=analytics_dir / f"{ticker}_fundamental_analysis.md",
                thesis=analytics_dir / f"{ticker}_investment_thesis.md"
            )

        def _read_file(self, path):
            if path and path.exists():
                return path.read_text()
            return None

        def load_watchlist(self):
            import json
            watchlist_path = self.root / "watchlist.json"
            if watchlist_path.exists():
                return json.load(open(watchlist_path))
            return {"tickers": {}}

        def get_portfolio(self, portfolio_name=None):
            import json
            portfolios_path = self.root / "portfolios.json"
            if portfolios_path.exists():
                portfolios = json.load(open(portfolios_path))
                if portfolio_name is None:
                    portfolio_name = portfolios.get("metadata", {}).get("default_portfolio", "CORE")
                return portfolios.get("portfolios", {}).get(portfolio_name, {})
            return {}

        def load_portfolios(self):
            import json
            portfolios_path = self.root / "portfolios.json"
            if portfolios_path.exists():
                return json.load(open(portfolios_path))
            return {"portfolios": {}, "cash": {}}

# Check for plotting libraries
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def create_price_chart(ticker: str, da: DataAccess = None, period: str = "3M") -> str:
    """
    Create an interactive price chart with technical overlays.

    Args:
        ticker: Stock ticker symbol
        da: DataAccess instance
        period: Time period (1M, 3M, 6M, 1Y, 2Y)

    Returns:
        HTML string with plotly chart
    """
    if not HAS_PLOTLY or not HAS_PANDAS:
        return "Error: plotly and pandas required for charts"

    da = da or DataAccess()
    ticker = ticker.upper()

    # Load price data
    df = da.read_price_data(ticker)
    if df is None or df.empty:
        return f"Error: No price data for {ticker}"

    # Filter by period
    period_days = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "2Y": 730}
    days = period_days.get(period, 90)
    cutoff = df.index[-1] - timedelta(days=days)
    df = df[df.index >= cutoff]

    # Calculate moving averages
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["MA200"] = df["Close"].rolling(window=200).mean()

    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=(f"{ticker} Price & Moving Averages", "Volume")
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="OHLC"
        ),
        row=1, col=1
    )

    # Moving averages
    if "MA20" in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["MA20"], name="MA20", line=dict(color="orange", width=1)),
            row=1, col=1
        )
    if "MA50" in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["MA50"], name="MA50", line=dict(color="blue", width=1)),
            row=1, col=1
        )
    if "MA200" in df.columns and len(df) >= 200:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["MA200"], name="MA200", line=dict(color="red", width=1)),
            row=1, col=1
        )

    # Volume
    colors = ["red" if close < open else "green"
              for close, open in zip(df["Close"], df["Open"])]
    fig.add_trace(
        go.Bar(x=df.index, y=df["Volume"], name="Volume", marker_color=colors, opacity=0.5),
        row=2, col=1
    )

    # Layout
    fig.update_layout(
        title=f"{ticker} - Last {period} Price Action",
        xaxis_rangeslider_visible=False,
        height=600,
        hovermode="x unified"
    )

    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig.to_html(include_plotlyjs="cdn")


def create_portfolio_waterfall(portfolio_name: str = None, da: DataAccess = None) -> str:
    """
    Create a P&L waterfall chart for portfolio.

    Args:
        portfolio_name: Portfolio name (None for default)
        da: DataAccess instance

    Returns:
        HTML string with plotly waterfall chart
    """
    if not HAS_PLOTLY:
        return "Error: plotly required for charts"

    da = da or DataAccess()

    # Get portfolio
    if portfolio_name:
        portfolio = da.get_portfolio(portfolio_name)
    else:
        portfolio = da.get_portfolio(None)
        portfolio_name = "default"

    holdings = portfolio.get("holdings", [])
    summary = portfolio.get("summary", {})

    if not holdings:
        return f"Error: No holdings in {portfolio_name}"

    # Waterfall data
    categories = ["Starting Cash"]
    values = [summary.get("cash_invested", 0)]

    for h in holdings:
        ticker = h.get("ticker", "UNKNOWN")
        gl = h.get("gain_loss", 0)
        categories.append(ticker)
        values.append(gl)

    categories.append("Total P&L")
    values.append(summary.get("total_gain_loss", 0))

    # Create waterfall using bar chart with base
    fig = go.Figure()

    # Calculate base positions
    base = 0
    bases = []
    for i, val in enumerate(values):
        if i == 0:
            bases.append(0)
        elif i == len(values) - 1:
            # Total
            bases.append(0)
        else:
            bases.append(base)
        if i < len(values) - 1:
            base += val

    # Colors
    colors = ["lightblue"] + ["green" if v > 0 else "red" for v in values[1:-1]] + ["darkblue"]

    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            base=bases,
            marker_color=colors,
            text=[f"${v:,.0f}" for v in values],
            textposition="outside"
        )
    )

    fig.update_layout(
        title=f"{portfolio_name} P&L Waterfall",
        yaxis_title="Gain/Loss ($)",
        height=500,
        showlegend=False
    )

    return fig.to_html(include_plotlyjs="cdn")


def create_thesis_heatmap(da: DataAccess = None) -> str:
    """
    Create a thesis status heatmap for all watchlist tickers.

    Args:
        da: DataAccess instance

    Returns:
        HTML string with plotly heatmap
    """
    if not HAS_PLOTLY or not HAS_PANDAS:
        return "Error: plotly and pandas required for charts"

    da = da or DataAccess()

    # Get all tickers from watchlist
    watchlist = da.load_watchlist()
    tickers = list(watchlist.get("tickers", {}).keys())[:50]  # Limit to 50

    if not tickers:
        return "Error: No tickers in watchlist"

    # Status levels mapping
    status_map = {
        "DANGER": 1,
        "WARNING": 2,
        "CAUTION": 3,
        "ON_TRACK": 4,
        "ACCELERATING": 5
    }

    status_labels = {
        1: "DANGER 🔴",
        2: "WARNING 🟡",
        3: "CAUTION 🟠",
        4: "ON_TRACK 🟢",
        5: "ACCELERATING 🚀"
    }

    # Get status for each ticker
    ticker_status = []
    ticker_prices = []

    for ticker in tickers:
        # Read thesis for status
        analytics = da.read_analytics(ticker)
        thesis = analytics.get("thesis", "")

        status = "ON_TRACK"  # Default
        for level in ["DANGER", "WARNING", "CAUTION", "ACCELERATING"]:
            if level in thesis.upper():
                status = level
                break

        ticker_status.append(status_map.get(status, 3))
        ticker_prices.append(ticker)

    # Get current prices
    prices = []
    for ticker in ticker_prices:
        df = da.read_price_data(ticker)
        if df is not None and not df.empty:
            prices.append(float(df["Close"].iloc[-1]))
        else:
            prices.append(0)

    # Create heatmap
    # We'll create a simple bar chart colored by status
    colors = ["darkred", "orange", "yellow", "lightgreen", "darkgreen"]

    fig = go.Figure(data=go.Bar(
        x=ticker_prices,
        y=[status_map.get(s, 3) for s in ticker_status],
        marker_color=[colors[status_map.get(s, 3) - 1] for s in ticker_status],
        text=[status_labels.get(status_map.get(s, 3), s) for s in ticker_status],
        textposition="outside"
    ))

    fig.update_layout(
        title="Thesis Status Heatmap",
        xaxis_title="Ticker",
        yaxis_title="Status",
        yaxis=dict(
            tickmode="array",
            tickvals=[1, 2, 3, 4, 5],
            ticktext=["DANGER", "WARNING", "CAUTION", "ON_TRACK", "ACCELERATING"]
        ),
        height=500
    )

    return fig.to_html(include_plotlyjs="cdn")


def save_chart(html: str, filename: str) -> str:
    """Save HTML chart to file."""
    output_dir = get_project_root() / "charts"
    output_dir.mkdir(exist_ok=True)

    filepath = output_dir / filename
    filepath.write_text(html)
    return str(filepath)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Visualize stock advisor data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python visualize.py price-chart NVDA
  python visualize.py price-chart NVDA --period 6M
  python visualize.py portfolio-waterfall CORE
  python visualize.py thesis-heatmap
  python visualize.py price-chart NVDA --save nvda_chart.html
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Visualization type")

    # Price chart command
    price_parser = subparsers.add_parser("price-chart", help="Create price chart with overlays")
    price_parser.add_argument("ticker", help="Stock ticker symbol")
    price_parser.add_argument("--period", default="3M", choices=["1M", "3M", "6M", "1Y", "2Y"])
    price_parser.add_argument("--save", help="Save to file")

    # Portfolio waterfall command
    waterfall_parser = subparsers.add_parser("portfolio-waterfall", help="Create P&L waterfall chart")
    waterfall_parser.add_argument("portfolio", nargs="?", default=None, help="Portfolio name")
    waterfall_parser.add_argument("--save", help="Save to file")

    # Thesis heatmap command
    heatmap_parser = subparsers.add_parser("thesis-heatmap", help="Create thesis status heatmap")
    heatmap_parser.add_argument("--save", help="Save to file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    da = DataAccess()
    html = ""

    if args.command == "price-chart":
        html = create_price_chart(args.ticker, da, args.period)
        if args.save:
            filepath = save_chart(html, args.save)
            print(f"Chart saved to: {filepath}")
        else:
            print(html)

    elif args.command == "portfolio-waterfall":
        html = create_portfolio_waterfall(args.portfolio, da)
        if args.save:
            filepath = save_chart(html, args.save)
            print(f"Chart saved to: {filepath}")
        else:
            print(html)

    elif args.command == "thesis-heatmap":
        html = create_thesis_heatmap(da)
        if args.save:
            filepath = save_chart(html, args.save)
            print(f"Chart saved to: {filepath}")
        else:
            print(html)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
