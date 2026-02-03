#!/usr/bin/env python3
"""
Technical Signal Aggregator - Main Script

Aggregates 40+ technical indicators into unified scores with:
- Market regime detection (trending/ranging/volatile)
- Category-based scoring (momentum, trend, volatility, volume, ob_os)
- Overall Technical Health Score (0-100)
- Signal dashboard with bullish/bearish/neutral classifications
- Cross-confirmation analysis with confidence levels

Usage:
    python aggregate_signals.py --ticker AAPL
    python aggregate_signals.py --tickers NVDA,AAPL,MSFT --format json
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional, List

# Add paths for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

import yaml


def get_project_root() -> Path:
    """Get project root directory using marker files."""
    p = Path(__file__).resolve()

    # Look for known project markers
    markers = ['prices/', '.git/', 'watchlist.json']

    for parent in [p, *p.parents]:
        if any((parent / m).exists() for m in markers):
            return parent

    # Fallback: use .claude as reference
    if ".claude" in p.parts:
        idx = p.parts.index(".claude")
        return Path(*p.parts[:idx])

    raise RuntimeError("Project root not found")


def load_config() -> Dict:
    """Load signal weights configuration."""
    config_path = script_dir / 'signal_weights.yaml'
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


def load_price_data(ticker: str) -> Optional[Dict]:
    """Load price data from CSV."""
    project_root = get_project_root()
    csv_path = project_root / 'prices' / f"{ticker.upper()}.csv"

    if not csv_path.exists():
        return None

    try:
        import pandas as pd
        df = pd.read_csv(csv_path)

        # Normalize column names to lowercase for consistent access
        df.columns = df.columns.str.lower()

        data = []
        for _, row in df.iterrows():
            data.append({
                'date': row['date'],
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume'])
            })

        return {
            'ticker': ticker.upper(),
            'data_points': len(data),
            'start_date': data[0]['date'],
            'end_date': data[-1]['date'],
            'latest_price': round(data[-1]['close'], 4),
            'data': data
        }
    except Exception as e:
        print(f"Error loading price data: {e}")
        return None


def calculate_indicators(price_data: Dict) -> Optional[Dict]:
    """Calculate technical indicators."""
    try:
        from technical_indicators import TechnicalIndicators

        indicators_calc = TechnicalIndicators(price_data['data'])
        return indicators_calc.calculate_all()
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return None


def classify_regime(indicators: Dict, config: Dict) -> Dict:
    """Classify market regime."""
    from regime_classifier import RegimeClassifier
    classifier = RegimeClassifier(indicators)
    return classifier.classify()


def score_signals(indicators: Dict, config: Dict) -> Dict:
    """Score all technical signals."""
    from signal_scorer import SignalScorer
    scorer = SignalScorer(indicators, config)
    return scorer.score_all()


def aggregate_scores(
    category_scores: Dict,
    signal_scores: Dict,
    regime: str,
    config: Dict
) -> Dict:
    """Aggregate scores with regime-based weights."""
    from score_aggregator import ScoreAggregator
    aggregator = ScoreAggregator(category_scores, signal_scores, regime, config)
    result = aggregator.aggregate()

    # Add additional info
    result['divergent_signals'] = aggregator.get_divergent_signals()
    result['key_signals'] = aggregator.get_key_signals()

    return result


def generate_dashboard(
    ticker: str,
    price_data: Dict,
    indicators: Dict,
    regime_result: Dict,
    score_result: Dict,
    aggregation_result: Dict
) -> str:
    """Generate markdown dashboard output for appending to technical_analysis.md."""
    lines = []

    # Note: No main header since this is appended as a section
    lines.append(f"**Analysis Date:** {price_data['end_date']}")
    lines.append(f"**Current Price:** ${price_data['latest_price']}")
    lines.append(f"**Data Points:** {price_data['data_points']} days")
    lines.append("")

    # Market Regime Section
    lines.append("## Market Regime")
    lines.append("")
    regime = regime_result['regime'].replace('_', ' ').title()
    confidence_pct = regime_result['confidence'] * 100
    lines.append(f"**Current Regime:** {regime}")
    lines.append(f"**Confidence:** {confidence_pct:.0f}%")
    lines.append("")

    lines.append("**Indicators:**")
    lines.append(f"- ADX: {regime_result['adx']:.2f}")
    lines.append(f"- ATR %: {regime_result['atr_pct']:.2f}%")
    lines.append(f"- Volatility Score: {regime_result['volatility_score']:.0f}/100")
    lines.append(f"- Trend Direction: {regime_result['trend_direction']}")
    lines.append("")

    # Overall Score Section
    lines.append("## Overall Technical Health Score")
    lines.append("")

    overall = aggregation_result['overall_score']
    classification = aggregation_result['classification']
    convergence = aggregation_result['convergence']
    conf_level = aggregation_result['confidence_level']

    # Classification emoji
    emoji = "🟢" if overall >= 60 else "🔴" if overall <= 40 else "⚪"

    lines.append(f"{emoji} **Overall:** {overall}/100 - {classification}")
    lines.append("")
    lines.append("| Category | Score | Weight | Classification |")
    lines.append("|----------|-------|--------|----------------|")

    for cat, data in aggregation_result['weighted_scores'].items():
        cat_emoji = "🟢" if data['score'] >= 60 else "🔴" if data['score'] <= 40 else "⚪"
        lines.append(f"| {cat.title()} | {data['score']}/100 | {data['weight']}% | {cat_emoji} {data['classification']} |")

    lines.append("")
    lines.append(f"**Signal Convergence:** {convergence}%")
    lines.append(f"**Confidence Level:** {conf_level}")
    lines.append("")

    # Cross-Confirmation Analysis
    lines.append("## Cross-Confirmation Analysis")
    lines.append("")

    aligned_bullish = 0
    aligned_bearish = 0
    total_signals = 0

    for cat, signals in score_result['signal_scores'].items():
        for sig, score in signals.items():
            if score is not None:
                total_signals += 1
                if score > 0.2:
                    aligned_bullish += 1
                elif score < -0.2:
                    aligned_bearish += 1

    active = aligned_bullish + aligned_bearish
    if active > 0:
        bullish_pct = (aligned_bullish / active) * 100
        bearish_pct = (aligned_bearish / active) * 100
        lines.append(f"- **Bullish Signals:** {aligned_bullish} ({bullish_pct:.0f}%)")
        lines.append(f"- **Bearish Signals:** {aligned_bearish} ({bearish_pct:.0f}%)")
        lines.append(f"- **Neutral/Weak Signals:** {total_signals - active}")
    lines.append("")

    # Divergence Warnings
    divergent = aggregation_result.get('divergent_signals', [])
    if divergent:
        lines.append("### ⚠️ Signal Divergences")
        lines.append("")
        lines.append("The following signals diverge from the overall trend:")
        lines.append("")
        for cat, sig, score in divergent[:5]:
            direction = "🟢 Bullish" if score > 0 else "🔴 Bearish"
            lines.append(f"- **{cat.title()} - {sig}:** {direction} ({score:.2f})")
        lines.append("")

    # Key Signals
    key_signals = aggregation_result.get('key_signals', [])
    if key_signals:
        lines.append("## Key Signals")
        lines.append("")
        lines.append("### Strongest Signals")
        lines.append("")
        lines.append("| Category | Signal | Score | Classification |")
        lines.append("|----------|--------|-------|----------------|")

        for cat, sig, score, classification in key_signals[:10]:
            emoji = "🟢" if score > 0.3 else "🔴" if score < -0.3 else "⚪"
            lines.append(f"| {cat.title()} | {sig} | {score:.2f} | {emoji} {classification} |")

        lines.append("")

    # Detailed Signal Dashboard
    lines.append("## Signal Dashboard")
    lines.append("")
    lines.append("### Momentum Signals")
    lines.append("")

    momentum = score_result['signal_scores'].get('momentum', {})
    if momentum:
        lines.append("| Signal | Score | Classification |")
        lines.append("|--------|-------|----------------|")
        for sig, score in sorted(momentum.items(), key=lambda x: abs(x[1]) if x[1] else 0, reverse=True):
            if score is not None:
                emoji = "🟢" if score > 0.3 else "🔴" if score < -0.3 else "⚪"
                classification = classify_single_score(score)
                lines.append(f"| {sig} | {score:.2f} | {emoji} {classification} |")
    else:
        lines.append("*No momentum signals available*")
    lines.append("")

    lines.append("### Trend Signals")
    lines.append("")

    trend = score_result['signal_scores'].get('trend', {})
    if trend:
        lines.append("| Signal | Score | Classification |")
        lines.append("|--------|-------|----------------|")
        for sig, score in sorted(trend.items(), key=lambda x: abs(x[1]) if x[1] else 0, reverse=True):
            if score is not None:
                emoji = "🟢" if score > 0.3 else "🔴" if score < -0.3 else "⚪"
                classification = classify_single_score(score)
                lines.append(f"| {sig} | {score:.2f} | {emoji} {classification} |")
    else:
        lines.append("*No trend signals available*")
    lines.append("")

    lines.append("### Volatility Signals")
    lines.append("")

    volatility = score_result['signal_scores'].get('volatility', {})
    if volatility:
        lines.append("| Signal | Score | Classification |")
        lines.append("|--------|-------|----------------|")
        for sig, score in sorted(volatility.items(), key=lambda x: abs(x[1]) if x[1] else 0, reverse=True):
            if score is not None:
                emoji = "🟢" if score > 0.3 else "🔴" if score < -0.3 else "⚪"
                classification = classify_single_score(score)
                lines.append(f"| {sig} | {score:.2f} | {emoji} {classification} |")
    else:
        lines.append("*No volatility signals available*")
    lines.append("")

    lines.append("### Volume Signals")
    lines.append("")

    volume = score_result['signal_scores'].get('volume', {})
    if volume:
        lines.append("| Signal | Score | Classification |")
        lines.append("|--------|-------|----------------|")
        for sig, score in sorted(volume.items(), key=lambda x: abs(x[1]) if x[1] else 0, reverse=True):
            if score is not None:
                emoji = "🟢" if score > 0.3 else "🔴" if score < -0.3 else "⚪"
                classification = classify_single_score(score)
                lines.append(f"| {sig} | {score:.2f} | {emoji} {classification} |")
    else:
        lines.append("*No volume signals available*")
    lines.append("")

    lines.append("### Overbought/Oversold Signals")
    lines.append("")

    obos = score_result['signal_scores'].get('ob_os', {})
    if obos:
        lines.append("| Signal | Score | Classification |")
        lines.append("|--------|-------|----------------|")
        for sig, score in sorted(obos.items(), key=lambda x: abs(x[1]) if x[1] else 0, reverse=True):
            if score is not None:
                emoji = "🟢" if score > 0.3 else "🔴" if score < -0.3 else "⚪"
                classification = classify_single_score(score)
                lines.append(f"| {sig} | {score:.2f} | {emoji} {classification} |")
    else:
        lines.append("*No overbought/oversold signals available*")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*Generated by Technical Signal Aggregator*")
    lines.append("")

    return "\n".join(lines)


def classify_single_score(score: float) -> str:
    """Classify a single signal score."""
    if score >= 0.6:
        return "Strongly Bullish"
    elif score >= 0.3:
        return "Moderately Bullish"
    elif score >= -0.3:
        return "Neutral"
    elif score >= -0.6:
        return "Moderately Bearish"
    else:
        return "Strongly Bearish"


def save_trading_volume_summary(ticker: str, dashboard: str) -> Optional[Path]:
    """Append signal dashboard to technical_analysis.md file."""
    project_root = get_project_root()
    analytics_dir = project_root / 'analytics' / ticker.upper()

    # Create directory if it doesn't exist
    analytics_dir.mkdir(parents=True, exist_ok=True)

    output_path = analytics_dir / f"{ticker.upper()}_technical_analysis.md"

    try:
        # Read existing technical analysis if it exists
        existing_content = ""
        if output_path.exists():
            existing_content = output_path.read_text()

        # Append signal dashboard to the file
        with open(output_path, 'w') as f:
            # Write existing content first
            if existing_content:
                f.write(existing_content)
                # Add separator if file doesn't end with one
                if not existing_content.rstrip().endswith("---"):
                    f.write("\n\n---\n\n")

            # Write signal dashboard section
            f.write("## Technical Signal Dashboard\n\n")
            f.write(dashboard)

        return output_path
    except Exception as e:
        print(f"Error saving signal summary: {e}")
        return None


def process_ticker(ticker: str, config: Dict, save_output: bool = True) -> Dict:
    """
    Process a single ticker through the full aggregation pipeline.

    Returns:
        Dict with all results or error info
    """
    # Load price data
    price_data = load_price_data(ticker)
    if not price_data:
        return {
            'ticker': ticker.upper(),
            'status': 'error',
            'error': f"Price file not found for {ticker}"
        }

    # Calculate indicators
    indicators = calculate_indicators(price_data)
    if not indicators:
        return {
            'ticker': ticker.upper(),
            'status': 'error',
            'error': f"Could not calculate indicators for {ticker}"
        }

    # Classify regime
    regime_result = classify_regime(indicators, config)

    # Score signals
    score_result = score_signals(indicators, config)

    # Aggregate scores
    aggregation_result = aggregate_scores(
        score_result['category_scores'],
        score_result['signal_scores'],
        regime_result['regime'],
        config
    )

    # Generate dashboard
    dashboard = generate_dashboard(
        price_data['ticker'],
        price_data,
        indicators,
        regime_result,
        score_result,
        aggregation_result
    )

    # Save output
    output_path = None
    if save_output:
        output_path = save_trading_volume_summary(ticker, dashboard)

    return {
        'ticker': ticker.upper(),
        'status': 'success',
        'regime': regime_result,
        'scores': aggregation_result,
        'dashboard': dashboard,
        'output_path': str(output_path) if output_path else None
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Aggregate technical signals into unified scores',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python aggregate_signals.py --ticker AAPL
  python aggregate_signals.py --tickers NVDA,AAPL,MSFT
  python aggregate_signals.py AAPL MSFT
  python aggregate_signals.py --ticker AAPL --format json
        """
    )

    parser.add_argument('tickers_pos', nargs='*', help='Tickers as positional arguments')
    parser.add_argument('--ticker', type=str, help='Single ticker symbol')
    parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers')
    parser.add_argument('--format', choices=['text', 'json', 'compact'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save output to file')

    args = parser.parse_args()

    # Collect tickers
    all_tickers = []
    if args.tickers_pos:
        all_tickers.extend(args.tickers_pos)
    if args.ticker:
        all_tickers.append(args.ticker)
    if args.tickers:
        all_tickers.extend(args.tickers.split(','))

    if not all_tickers:
        parser.error("--ticker, --tickers, or positional tickers required")

    # Load config
    config = load_config()

    # Process tickers
    results = []
    for ticker in all_tickers:
        result = process_ticker(ticker, config, save_output=not args.no_save)
        results.append(result)

    # Output
    if args.format == 'json':
        # For JSON, output summary (full dashboard would be too large)
        json_output = []
        for r in results:
            if r['status'] == 'success':
                # Extract category scores from weighted_scores
                category_scores = {}
                for cat, data in r['scores'].get('weighted_scores', {}).items():
                    category_scores[cat] = data.get('score', 50)

                json_output.append({
                    'ticker': r['ticker'],
                    'regime': r['regime']['regime'],
                    'overall_score': r['scores']['overall_score'],
                    'classification': r['scores']['classification'],
                    'convergence': r['scores']['convergence'],
                    'confidence': r['scores']['confidence_level'],
                    'category_scores': category_scores
                })
            else:
                json_output.append({
                    'ticker': r['ticker'],
                    'status': 'error',
                    'error': r.get('error', 'Unknown error')
                })
        print(json.dumps(json_output, indent=2))

    elif args.format == 'compact':
        # Compact one-line output per ticker
        for r in results:
            if r['status'] == 'success':
                print(f"{r['ticker']}: {r['scores']['overall_score']}/100 - {r['scores']['classification']} "
                      f"({r['regime']['regime']}, {r['scores']['confidence_level']} confidence)")
            else:
                print(f"{r['ticker']}: ERROR - {r.get('error', 'Unknown error')}")

    else:
        # Full text output (default)
        for i, r in enumerate(results):
            if r['status'] == 'success':
                print(r['dashboard'])
                if i < len(results) - 1:
                    print("\n" + "=" * 80 + "\n")
            else:
                print(f"ERROR {r['ticker']}: {r.get('error', 'Unknown error')}")

    # Exit code
    if all(r['status'] == 'error' for r in results):
        sys.exit(1)
    elif any(r['status'] == 'error' for r in results):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
