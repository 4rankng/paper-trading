#!/usr/bin/env python3
"""
Generate Technical Analysis Data for LLM Consumption

This script reads price data from CSV, calculates all technical indicators,
and outputs them in a structured, human-readable format for LLM analysis.

Usage:
    python generate_technical.py --ticker TCOM
    python generate_technical.py --ticker NVDA --period 6M

Output:
    Structured text format (not JSON) that LLM can parse to create
    {TICKER}_technical_analysis.md markdown files
"""
import argparse
import sys
from pathlib import Path
from typing import Dict, Optional
import json


def get_project_root() -> Path:
    """Get project root directory."""
    p = Path(__file__).resolve()
    if "skills" in p.parts:
        idx = p.parts.index("skills")
        return Path(*p.parts[:idx - 1])
    return p.parent.parent.parent.parent


def load_price_data(ticker: str) -> Optional[Dict]:
    """Load price data from prices/{TICKER}.csv."""
    project_root = get_project_root()
    csv_path = project_root / 'prices' / f"{ticker.upper()}.csv"

    if not csv_path.exists():
        print(f"Error: Price file not found: {csv_path}")
        print(f"Run: python .claude/skills/analytics_generator/scripts/fetch_prices.py --ticker {ticker}")
        return None

    try:
        import pandas as pd
        df = pd.read_csv(csv_path)

        # Ensure column names match expected format
        expected_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        actual_columns = [col.lower() for col in df.columns]

        # Convert to standard format
        data = []
        for _, row in df.iterrows():
            data.append({
                'date': row['date'],
                'open': float(row['Open']) if 'Open' in row.index else float(row.iloc[1]),
                'high': float(row['High']) if 'High' in row.index else float(row.iloc[2]),
                'low': float(row['Low']) if 'Low' in row.index else float(row.iloc[3]),
                'close': float(row['Close']) if 'Close' in row.index else float(row.iloc[4]),
                'volume': float(row['Volume']) if 'Volume' in row.index else float(row.iloc[5])
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


def calculate_indicators(price_data: Dict) -> Dict:
    """Calculate all technical indicators using TechnicalIndicators class."""
    try:
        from technical_indicators import TechnicalIndicators

        indicators_calc = TechnicalIndicators(price_data['data'])
        all_indicators = indicators_calc.calculate_all()

        # Add metadata
        all_indicators['_metadata'] = {
            'ticker': price_data['ticker'],
            'current_price': price_data['latest_price'],
            'data_points': price_data['data_points'],
            'period_start': price_data['start_date'],
            'period_end': price_data['end_date']
        }

        return all_indicators

    except ImportError as e:
        print(f"Error: {e}")
        print("Install required dependencies: pip install pandas numpy TA-Lib")
        return None
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return None


def format_indicators_for_llm(indicators: Dict) -> str:
    """Format indicators in structured text for LLM consumption."""

    if not indicators or '_metadata' not in indicators:
        return "Error: Invalid indicators data"

    meta = indicators.pop('_metadata')
    ticker = meta['ticker']
    current_price = meta['current_price']

    output = []
    output.append("=" * 80)
    output.append(f"TECHNICAL ANALYSIS DATA FOR {ticker}")
    output.append("=" * 80)
    output.append(f"Analysis Date: {meta['period_end']}")
    output.append(f"Data Period: {meta['period_start']} to {meta['period_end']} ({meta['data_points']} trading days)")
    output.append(f"Current Price: ${current_price}")
    output.append("")

    # Price Action
    output.append("-" * 80)
    output.append("PRICE ACTION")
    output.append("-" * 80)
    output.append(f"52-Week Range: ${indicators.get('52_week_range', {}).get('high', 'N/A')} - ${indicators.get('52_week_range', {}).get('low', 'N/A')}")

    range_52w = indicators.get('52_week_range', {})
    if range_52w:
        pct_from_high = range_52w.get('current_pct_from_high', 'N/A')
        pct_from_low = range_52w.get('current_pct_from_low', 'N/A')
        output.append(f"Current Position: {pct_from_high}% below 52-week high, {pct_from_low}% above 52-week low")

    output.append("")

    # Moving Averages
    output.append("-" * 80)
    output.append("MOVING AVERAGES")
    output.append("-" * 80)

    # SMAs are stored under 'moving_averages' sub-dictionary
    ma_dict = indicators.get('moving_averages', {})
    ma_10 = ma_dict.get('ma_10', 'N/A')
    ma_20 = ma_dict.get('ma_20', 'N/A')
    ma_50 = ma_dict.get('ma_50', 'N/A')
    ma_100 = ma_dict.get('ma_100', 'N/A')
    ma_200 = ma_dict.get('ma_200', 'N/A')

    output.append(f"MA-10:   ${ma_10}")
    output.append(f"MA-20:   ${ma_20}")
    output.append(f"MA-50:   ${ma_50}")
    output.append(f"MA-100:  ${ma_100}")
    output.append(f"MA-200:  ${ma_200}")

    # EMAs
    ema_20 = indicators.get('ema_20', 'N/A')
    dema_20 = indicators.get('dema_20', 'N/A')
    tema_20 = indicators.get('tema_20', 'N/A')
    output.append(f"\nEMA-20:  ${ema_20}")
    output.append(f"DEMA-20: ${dema_20}")
    output.append(f"TEMA-20: ${tema_20}")

    # Other MAs
    t3_20 = indicators.get('t3_20', 'N/A')
    wma_20 = indicators.get('wma_20', 'N/A')
    kama_30 = indicators.get('kama_30', 'N/A')
    mama = indicators.get('mama', 'N/A')
    fama = indicators.get('fama', 'N/A')
    sar = indicators.get('sar', 'N/A')

    output.append(f"\nT3-20:   ${t3_20}")
    output.append(f"WMA-20:  ${wma_20}")
    output.append(f"KAMA-30: ${kama_30}")
    output.append(f"MAMA:    ${mama}")
    output.append(f"FAMA:    ${fama}")
    output.append(f"SAR:     ${sar}")

    output.append("")

    # Momentum Indicators
    output.append("-" * 80)
    output.append("MOMENTUM INDICATORS")
    output.append("-" * 80)

    rsi = indicators.get('rsi', {})
    output.append(f"RSI (14): {rsi.get('current', 'N/A')} - Signal: {rsi.get('signal', 'N/A')}")

    macd = indicators.get('macd', {})
    output.append(f"\nMACD:")
    output.append(f"  MACD Line:   {macd.get('macd_line', 'N/A')}")
    output.append(f"  Signal Line: {macd.get('signal_line', 'N/A')}")
    output.append(f"  Histogram:   {macd.get('histogram', 'N/A')}")
    output.append(f"  Trend:       {macd.get('macd_trend', 'N/A')}")

    stoch = indicators.get('stochastic', {})
    output.append(f"\nStochastic:")
    output.append(f"  %K: {stoch.get('k_value', 'N/A')}")
    output.append(f"  %D: {stoch.get('d_value', 'N/A')}")
    output.append(f"  Signal: {stoch.get('signal', 'N/A')}")

    output.append("")

    # Volatility
    output.append("-" * 80)
    output.append("VOLATILITY")
    output.append("-" * 80)

    atr = indicators.get('atr', {})
    output.append(f"ATR (14): {atr.get('current', 'N/A')} ({atr.get('current_pct', 'N/A')}%)")

    bb = indicators.get('bollinger_bands', {})
    output.append(f"\nBollinger Bands:")
    output.append(f"  Upper Band:  ${bb.get('upper_band', 'N/A')}")
    output.append(f"  Middle Band: ${bb.get('middle_band', 'N/A')}")
    output.append(f"  Lower Band:  ${bb.get('lower_band', 'N/A')}")
    output.append(f"  Bandwidth:   ${bb.get('bandwidth', 'N/A')}")
    output.append(f"  Position:    {bb.get('position', 'N/A')}")

    output.append("")

    # Volume Analysis
    output.append("-" * 80)
    output.append("VOLUME ANALYSIS")
    output.append("-" * 80)

    vol = indicators.get('volume', {})
    output.append(f"Average Volume: {vol.get('avg_volume', 'N/A'):,.0f}")
    output.append(f"Current Volume: {vol.get('current_volume', 'N/A'):,.0f}")
    output.append(f"Volume Ratio:   {vol.get('volume_ratio', 'N/A')}x")
    output.append(f"Trend:          {vol.get('trend', 'N/A')}")

    # OBV & AD
    adv = indicators.get('advanced', {})
    obv = adv.get('obv', {})
    ad = adv.get('ad', {})
    ad_osc = adv.get('adosc', 'N/A')

    output.append(f"\nOn-Balance Volume: {obv.get('current', 'N/A'):,.0f} - Trend: {obv.get('trend', 'N/A')}")
    output.append(f"Accumulation/Distribution: {ad.get('current', 'N/A'):,.0f}")
    output.append(f"A/D Oscillator: {ad_osc:,.0f}")

    output.append("")

    # Support & Resistance
    output.append("-" * 80)
    output.append("SUPPORT & RESISTANCE")
    output.append("-" * 80)

    sr = indicators.get('support_resistance', {})
    output.append("Support Levels:")
    for level in sr.get('support_levels', []):
        output.append(f"  ${level}")
    output.append(f"Nearest Support: ${sr.get('nearest_support', 'N/A')}")

    output.append("\nResistance Levels:")
    for level in sr.get('resistance_levels', []):
        output.append(f"  ${level}")
    output.append(f"Nearest Resistance: ${sr.get('nearest_resistance', 'N/A')}")

    # Enhanced S/R if available
    esr = indicators.get('enhanced_support_resistance', {})
    if esr:
        output.append("\nEnhanced Support/Resistance:")
        output.append(f"Support Levels: {esr.get('support_levels', [])}")
        output.append(f"Resistance Levels: {esr.get('resistance_levels', [])}")

    output.append("")

    # Trend Analysis
    output.append("-" * 80)
    output.append("TREND ANALYSIS")
    output.append("-" * 80)

    trend = indicators.get('trend', {})
    output.append(f"Overall Trend: {trend.get('trend', 'N/A').upper()} - {trend.get('strength', 'N/A').upper()}")
    output.append(f"Price vs Short MA (20): {trend.get('price_vs_short_ma', 'N/A')}")
    output.append(f"Price vs Long MA (200): {trend.get('price_vs_long_ma', 'N/A')}")
    output.append(f"Short MA vs Long MA: {trend.get('short_ma_vs_long_ma', 'N/A')}")
    output.append(f"Short MA Slope: {trend.get('short_ma_slope', 'N/A')}")
    output.append(f"Long MA Slope: {trend.get('long_ma_slope', 'N/A')}")
    output.append(f"Distance to Short MA: {trend.get('distance_to_short_ma_pct', 'N/A')}%")
    output.append(f"Distance to Long MA: {trend.get('distance_to_long_ma_pct', 'N/A')}%")

    # Trendline
    tl = indicators.get('trendline', {})
    output.append(f"\nTrendline (50-day):")
    output.append(f"  Slope: {tl.get('slope', 'N/A')}")
    output.append(f"  Angle: {tl.get('angle', 'N/A')}")
    output.append(f"  R²: {tl.get('r_squared', 'N/A')}")
    output.append(f"  Price vs Trendline: {tl.get('price_vs_trendline_pct', 'N/A')}%")
    output.append(f"  Direction: {tl.get('trend_direction', 'N/A')}")

    output.append("")

    # Advanced Indicators
    output.append("-" * 80)
    output.append("ADVANCED INDICATORS")
    output.append("-" * 80)

    adv = indicators.get('advanced', {})

    adx = adv.get('adx', {})
    output.append(f"ADX: {adx.get('current', 'N/A')} - Signal: {adx.get('signal', 'N/A')}")

    aroon = adv.get('aroon', {})
    output.append(f"\nAroon:")
    output.append(f"  Up: {aroon.get('up', 'N/A')}")
    output.append(f"  Down: {aroon.get('down', 'N/A')}")
    output.append(f"  Oscillator: {aroon.get('oscillator', 'N/A')}")

    cci = adv.get('cci', {})
    output.append(f"\nCCI: {cci.get('current', 'N/A')} - Signal: {cci.get('signal', 'N/A')}")

    mfi = adv.get('mfi', {})
    output.append(f"MFI: {mfi.get('current', 'N/A')} - Signal: {mfi.get('signal', 'N/A')}")

    willr = adv.get('willr', {})
    output.append(f"Williams %R: {willr.get('current', 'N/A')} - Signal: {willr.get('signal', 'N/A')}")

    ultosc = adv.get('ultosc', 'N/A')
    output.append(f"Ultimate Oscillator: {ultosc}")

    output.append("")

    # Fibonacci Retracements
    fib = indicators.get('fibonacci', {})
    if fib:
        output.append("-" * 80)
        output.append("FIBONACCI RETRACEMENTS")
        output.append("-" * 80)
        output.append(f"Swing High: ${fib.get('swing_high', 'N/A')}")
        output.append(f"Swing Low: ${fib.get('swing_low', 'N/A')}")

        output.append("\nFibonacci Levels:")
        levels = fib.get('levels', {})
        for level_name, price in levels.items():
            output.append(f"  {level_name}: ${price}")

        output.append(f"\nNearest Level: {fib.get('nearest_level', 'N/A')} (${fib.get('nearest_level_price', 'N/A')})")

        output.append("")

    # Pivot Points
    pp = indicators.get('pivot_points', {})
    if pp:
        output.append("-" * 80)
        output.append("PIVOT POINTS")
        output.append("-" * 80)

        classic = pp.get('classic', {})
        output.append("Classic Pivot Points:")
        output.append(f"  Pivot: ${classic.get('pivot', 'N/A')}")
        output.append(f"  Resistance: R1=${classic.get('resistance', {}).get('r1', 'N/A')}, "
                    f"R2=${classic.get('resistance', {}).get('r2', 'N/A')}, "
                    f"R3=${classic.get('resistance', {}).get('r3', 'N/A')}")
        output.append(f"  Support: S1=${classic.get('support', {}).get('s1', 'N/A')}, "
                    f"S2=${classic.get('support', {}).get('s2', 'N/A')}, "
                    f"S3=${classic.get('support', {}).get('s3', 'N/A')}")

        fib_pp = pp.get('fibonacci', {})
        output.append("\nFibonacci Pivot Points:")
        output.append(f"  Pivot: ${fib_pp.get('pivot', 'N/A')}")
        output.append(f"  Resistance: R1=${fib_pp.get('resistance', {}).get('r1', 'N/A')}, "
                    f"R2=${fib_pp.get('resistance', {}).get('r2', 'N/A')}, "
                    f"R3=${fib_pp.get('resistance', {}).get('r3', 'N/A')}")
        output.append(f"  Support: S1=${fib_pp.get('support', {}).get('s1', 'N/A')}, "
                    f"S2=${fib_pp.get('support', {}).get('s2', 'N/A')}, "
                    f"S3=${fib_pp.get('support', {}).get('s3', 'N/A')}")

        output.append("")

    # Statistical Indicators
    stat = indicators.get('statistical', {})
    if stat:
        output.append("-" * 80)
        output.append("STATISTICAL METRICS")
        output.append("-" * 80)
        output.append(f"Beta: {stat.get('beta', 'N/A')}")
        output.append(f"Price-Volume Correlation: {stat.get('price_volume_correlation', 'N/A')}")
        output.append(f"30-Day Volatility (Std Dev): ${stat.get('volatility_std_30d', 'N/A')}")

        output.append("")

    # Cycle Indicators
    cycle = indicators.get('cycle', {})
    if cycle:
        output.append("-" * 80)
        output.append("CYCLE INDICATORS")
        output.append("-" * 80)
        dc_period = cycle.get('dc_period', 'N/A')
        dc_phase = cycle.get('dc_phase', 'N/A')
        output.append(f"DC Period: {dc_period}")
        output.append(f"DC Phase: {dc_phase}")

        phasor = cycle.get('phasor', {})
        output.append(f"\nPhasor:")
        output.append(f"  In-Phase: {phasor.get('inphase', 'N/A')}")
        output.append(f"  Quadrature: {phasor.get('quadrature', 'N/A')}")

        sinewave = cycle.get('sineWave', {})
        output.append(f"\nSine Wave:")
        output.append(f"  Sine: {sinewave.get('sine', 'N/A')}")
        output.append(f"  Leadsine: {sinewave.get('leadsine', 'N/A')}")

        output.append(f"\nTrend Mode: {cycle.get('trend_mode', 'N/A')}")

        output.append("")

    output.append("=" * 80)
    output.append("END OF TECHNICAL DATA")
    output.append("=" * 80)

    return "\n".join(output)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate technical analysis data for LLM consumption',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_technical.py --ticker TCOM
  python generate_technical.py --ticker NVDA
        """
    )

    parser.add_argument('--ticker', required=True, type=str, help='Stock ticker symbol')

    args = parser.parse_args()

    # Load price data
    price_data = load_price_data(args.ticker)
    if not price_data:
        sys.exit(1)

    # Calculate indicators
    indicators = calculate_indicators(price_data)
    if not indicators:
        sys.exit(1)

    # Format and output
    formatted_output = format_indicators_for_llm(indicators)
    print(formatted_output)


if __name__ == '__main__':
    main()
