#!/usr/bin/env python3
"""
Value Hunting Screener - Find undervalued equities using margin-of-safety approach.

This script performs initial screening on quantifiable filters and outputs
detailed data for LLM agent vetting of qualitative criteria.

Python Filtered (hard thresholds):
- Exchange: Nasdaq only
- Market Cap: >= $200M
- ADV: > 1M shares
- Price: Down 15-60% from 52-week high (widened range)

LLM Vetting (manual assessment):
- Debt/Equity assessment (context-dependent)
- Interest Coverage quality
- FCF Yield sustainability
- ROE/ROIC trend analysis
- Balance sheet strength
- Growth trajectory
- Economic moat evaluation
- Value trap detection
"""

import yfinance as yf
import pandas as pd
import json
import sys
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')


@dataclass
class FilterResult:
    """Track which filters passed/failed for a stock."""
    ticker: str
    passed_filters: Dict[str, bool]
    fundamental_data: Dict
    is_candidate: bool


class ValueHunter:
    """Screen for undervalued equities using margin-of-safety approach."""

    # Strategy-specific filter configurations
    STRATEGY_CONFIGS = {
        'scalping': {
            'min_market_cap': 500_000_000,  # $500M
            'min_adv': 5_000_000,  # 5M shares
            'min_decline': 0.05,  # 5% (mean reversion)
            'max_decline': 0.30,  # 30%
            'min_rsi': None,  # RSI check optional
            'max_rsi': None,
        },
        'swing': {
            'min_market_cap': 300_000_000,  # $300M
            'min_adv': 2_000_000,  # 2M shares
            'min_decline': 0.10,  # 10%
            'max_decline': 0.40,  # 40%
            'min_rsi': None,
            'max_rsi': None,
        },
        'position': {
            'min_market_cap': 200_000_000,  # $200M
            'min_adv': 1_500_000,  # 1.5M shares
            'min_decline': 0.15,  # 15%
            'max_decline': 0.50,  # 50%
            'min_rsi': None,
            'max_rsi': None,
        },
        'investment': {
            'min_market_cap': 200_000_000,  # $200M
            'min_adv': 1_000_000,  # 1M shares
            'min_decline': 0.20,  # 20% (intrinsic value focus)
            'max_decline': 0.50,  # 50%
            'min_rsi': None,
            'max_rsi': None,
        },
    }

    # Default (investment strategy)
    MIN_MARKET_CAP = 200_000_000
    MIN_ADV = 500_000
    MIN_DECLINE_FROM_HIGH = 0.15
    MAX_DECLINE_FROM_HIGH = 0.60

    def __init__(self, max_workers: int = 10, strategy: str = 'investment'):
        self.max_workers = max_workers
        self.nasdaq_stocks = []
        self.strategy = strategy

        # Apply strategy-specific filters
        if strategy in self.STRATEGY_CONFIGS:
            config = self.STRATEGY_CONFIGS[strategy]
            self.MIN_MARKET_CAP = config['min_market_cap']
            self.MIN_ADV = config['min_adv']
            self.MIN_DECLINE_FROM_HIGH = config['min_decline']
            self.MAX_DECLINE_FROM_HIGH = config['max_decline']

    def fetch_nasdaq_list(self) -> List[str]:
        """Fetch list of Nasdaq-traded stocks from Wikipedia."""
        import requests
        from io import StringIO

        try:
            # Fetch Nasdaq listed companies from Wikipedia
            url = "https://en.wikipedia.org/wiki/List_of_Nasdaq-100_companies"
            response = requests.get(url, timeout=30)
            tables = pd.read_html(StringIO(response.text))

            # Nasdaq-100 table is usually first
            nasdaq_100 = tables[0]
            tickers = nasdaq_100['Ticker'].str.strip().tolist()

            # Also fetch from broader Nasdaq page
            url2 = "https://en.wikipedia.org/wiki/Nasdaq"
            response2 = requests.get(url2, timeout=30)
            tables2 = pd.read_html(StringIO(response2.text))

            # Get additional tickers from other tables
            all_tickers = set(tickers)

            for table in tables2[1:3]:  # Skip first table usually headers
                if 'Ticker' in table.columns or 'Symbol' in table.columns:
                    col = 'Ticker' if 'Ticker' in table.columns else 'Symbol'
                    for t in table[col]:
                        if pd.notna(t):
                            ticker = str(t).strip().replace('^', '')
                            if len(ticker) <= 5 and ticker.isalpha():
                                all_tickers.add(ticker)

            self.nasdaq_stocks = sorted(list(all_tickers))
            print(f"Loaded {len(self.nasdaq_stocks)} Nasdaq tickers", file=sys.stderr)
            return self.nasdaq_stocks

        except Exception as e:
            print(f"Error fetching Nasdaq list: {e}", file=sys.stderr)
            # Fallback to a subset of well-known Nasdaq stocks
            fallback = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD',
                       'INTC', 'CSCO', 'ADBE', 'CRM', 'PYPL', 'NFLX', 'AVGO', 'QCOM',
                       'TXN', 'SBUX', 'INTU', 'AMAT', 'ADI', 'MRVL', 'LRCX', 'KLAC',
                       'SNPS', 'CDNS', 'FTNT', 'PANW', 'CRWD', 'ZS', 'NET', 'OKTA',
                       'DOCU', 'SPLK', 'TWLO', 'SHOP', 'SQ', 'ABNB', 'UBER', 'LYFT',
                       'SNOW', 'PLTR', 'U', 'DDOG', 'FVRR', 'ETSY', 'ZM', 'RBLX']
            self.nasdaq_stocks = fallback
            return fallback

    def get_average_daily_volume(self, ticker: str) -> Optional[float]:
        """Calculate average daily volume over past 90 days."""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="3mo", interval="1d")

            if hist.empty or len(hist) < 20:
                return None

            # Calculate ADV over trading days we have data for
            return hist['Volume'].mean()
        except Exception:
            return None

    def calculate_cagr(self, start_value: float, end_value: float, years: int) -> Optional[float]:
        """Calculate compound annual growth rate."""
        if start_value is None or end_value is None or start_value <= 0 or years <= 0:
            return None
        try:
            return (end_value / start_value) ** (1 / years) - 1
        except (ZeroDivisionError, ValueError):
            return None

    def get_historical_cagr(self, ticker: str) -> Tuple[Optional[float], Optional[float]]:
        """Calculate 5-year revenue and EPS CAGR from financials."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Try to get from info first
            revenue_growth = info.get('revenueGrowth')  # This is YoY growth
            earnings_growth = info.get('earningsGrowth')  # This is quarterly YoY

            # If not available, try to estimate from other fields
            if revenue_growth is None:
                revenue_growth = info.get('quarterlyRevenueGrowthYoY')

            # For 5-year CAGR, we'd need historical financials
            # For now, use available growth rates as approximation
            return revenue_growth, earnings_growth

        except Exception:
            return None, None

    def calculate_roic(self, info: Dict) -> Optional[float]:
        """
        Calculate Return on Invested Capital.
        ROIC = NOPAT / (Debt + Equity - Cash)

        NOPAT ≈ EBIT * (1 - Tax Rate)
        """
        try:
            ebit = info.get('ebit') or info.get('operatingIncome')
            total_debt = info.get('totalDebt') or info.get('longTermDebt')
            total_equity = info.get('totalStockholderEquity')
            total_cash = info.get('totalCash')
            tax_rate = info.get('effectiveTaxRate') or info.get('taxRate') or 0.21

            if None in [ebit, total_debt, total_equity]:
                return None

            nopat = ebit * (1 - tax_rate)
            invested_capital = (total_debt + total_equity) - (total_cash or 0)

            if invested_capital <= 0:
                return None

            return nopat / invested_capital

        except (ZeroDivisionError, TypeError):
            return None

    def calculate_fcf_yield(self, ticker: str, info: Dict) -> Optional[float]:
        """
        Calculate Free Cash Flow Yield.
        FCF Yield = FCF / Market Cap
        """
        try:
            market_cap = info.get('marketCap')
            if not market_cap or market_cap <= 0:
                return None

            # Try to get FCF from info
            fcf = info.get('freeCashflow')

            if fcf is None:
                # Estimate FCF ≈ Operating Cash Flow - CapEx
                ocf = info.get('operatingCashflow')
                capex = info.get('capitalExpenditures')
                if ocf is not None and capex is not None:
                    fcf = ocf - abs(capex)

            if fcf is None:
                return None

            return fcf / market_cap

        except (ZeroDivisionError, TypeError):
            return None

    def calculate_ev_ebitda(self, info: Dict) -> Optional[float]:
        """Calculate EV/EBITDA."""
        try:
            market_cap = info.get('marketCap')
            total_debt = info.get('totalDebt') or 0
            total_cash = info.get('totalCash') or 0
            ebitda = info.get('ebitda') or info.get('ebitdA')

            if None in [market_cap, ebitda] or ebitda <= 0:
                return None

            enterprise_value = market_cap + total_debt - total_cash
            return enterprise_value / ebitda

        except (ZeroDivisionError, TypeError):
            return None

    def calculate_dividend_payout(self, info: Dict) -> Optional[float]:
        """Calculate dividend payout ratio."""
        try:
            dividend_yield = info.get('dividendYield') or 0
            eps = info.get('trailingEps')

            if dividend_yield == 0 or eps is None:
                return None

            # Payout ≈ (Dividend Yield * Price) / EPS
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            if price is None:
                return None

            annual_dividend = dividend_yield * price
            return annual_dividend / eps if eps > 0 else None

        except (ZeroDivisionError, TypeError):
            return None

    def get_decline_from_high(self, info: Dict) -> Optional[float]:
        """Calculate decline from 52-week high as percentage."""
        try:
            current = info.get('currentPrice') or info.get('regularMarketPrice')
            high = info.get('fiftyTwoWeekHigh')

            if None in [current, high] or high <= 0:
                return None

            return (high - current) / high

        except (ZeroDivisionError, TypeError):
            return None

    def is_financial(self, info: Dict) -> bool:
        """Check if company is in financial sector."""
        industry = info.get('industry', '')
        sector = info.get('sector', '')

        financial_keywords = {'Bank', 'Insurance', 'Financial', 'Capital Markets',
                            'Credit', 'Asset Management', 'Mortgage', 'Thrift'}

        for keyword in financial_keywords:
            if keyword in industry or keyword in sector:
                return True

        return False

    def screen_stock(self, ticker: str) -> Optional[FilterResult]:
        """
        Screen a single stock - collect all fundamental data and apply
        only basic quantifiable filters. Detailed vetting left to LLM agent.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Basic data check
            market_cap = info.get('marketCap')
            if not market_cap:
                return None

            passed_filters = {}
            fundamental_data = {}

            # 1. MARKET CAP FILTER (hard filter)
            passed_filters['market_cap'] = market_cap >= self.MIN_MARKET_CAP
            fundamental_data['market_cap'] = market_cap

            # 2. VOLUME FILTER (hard filter - check ADV)
            adv = self.get_average_daily_volume(ticker)
            if adv:
                passed_filters['avg_daily_volume'] = adv >= self.MIN_ADV
                fundamental_data['avg_daily_volume'] = adv
            else:
                passed_filters['avg_daily_volume'] = False

            # 3. PRICE DECLINE FROM HIGH (hard filter)
            decline = self.get_decline_from_high(info)
            if decline is not None:
                passed_filters['price_decline'] = (
                    self.MIN_DECLINE_FROM_HIGH <= decline <= self.MAX_DECLINE_FROM_HIGH
                )
                fundamental_data['decline_from_high_pct'] = decline * 100
                fundamental_data['current_price'] = info.get('currentPrice')
                fundamental_data['fifty_two_week_high'] = info.get('fiftyTwoWeekHigh')
                fundamental_data['fifty_two_week_low'] = info.get('fiftyTwoWeekLow')
            else:
                passed_filters['price_decline'] = False

            # COLLECT ALL FUNDAMENTAL DATA FOR LLM VETTING

            # Valuation Metrics (for LLM analysis)
            fundamental_data['trailing_pe'] = info.get('trailingPE')
            fundamental_data['forward_pe'] = info.get('forwardPE')
            fundamental_data['price_to_book'] = info.get('priceToBook')
            fundamental_data['price_to_sales'] = info.get('priceToSalesTrailing12Months')
            fundamental_data['peg_ratio'] = info.get('pegRatio')

            # Profitability
            fundamental_data['profit_margins'] = info.get('profitMargins')
            fundamental_data['operating_margins'] = info.get('operatingMargins')
            fundamental_data['gross_margins'] = info.get('grossMargins')
            fundamental_data['roe'] = info.get('returnOnEquity')
            fundamental_data['roa'] = info.get('returnOnAssets')

            # Balance Sheet
            d_e = info.get('debtToEquity')
            if d_e is not None:
                # yfinance returns as number (e.g., 150 for 150%), convert to ratio
                fundamental_data['debt_to_equity'] = d_e / 100 if d_e > 1 else d_e
            else:
                fundamental_data['debt_to_equity'] = None
            fundamental_data['current_ratio'] = info.get('currentRatio')
            fundamental_data['quick_ratio'] = info.get('quickRatio')
            fundamental_data['total_cash'] = info.get('totalCash')
            fundamental_data['total_debt'] = info.get('totalDebt')
            fundamental_data['total_debt_per_equity'] = info.get('debtToEquity')

            # Cash Flow
            fcf_yield = self.calculate_fcf_yield(ticker, info)
            fundamental_data['fcf_yield'] = fcf_yield
            fundamental_data['operating_cashflow'] = info.get('operatingCashflow')
            fundamental_data['free_cashflow'] = info.get('freeCashflow')
            fundamental_data['capital_expenditures'] = info.get('capitalExpenditures')

            # Calculated ROIC for LLM analysis
            roic = self.calculate_roic(info)
            fundamental_data['roic'] = roic

            # Interest Coverage
            ebit = info.get('ebit') or info.get('operatingIncome')
            interest_expense = info.get('interestExpense')
            if ebit and interest_expense and interest_expense != 0:
                fundamental_data['interest_coverage'] = abs(ebit / interest_expense)
            else:
                fundamental_data['interest_coverage'] = None

            # EV/EBITDA
            ev_ebitda = self.calculate_ev_ebitda(info)
            fundamental_data['ev_ebitda'] = ev_ebitda

            # Growth
            fundamental_data['revenue_growth_yoy'] = info.get('revenueGrowth')
            fundamental_data['quarterly_revenue_growth_yoy'] = info.get('quarterlyRevenueGrowthYoY')
            fundamental_data['earnings_growth_yoy'] = info.get('earningsGrowth')
            fundamental_data['earnings_quarterly_growth_yoy'] = info.get('earningsQuarterlyGrowthYoY')

            # Dividend
            fundamental_data['dividend_yield'] = info.get('dividendYield')
            fundamental_data['dividend_rate'] = info.get('dividendRate')

            # Company Info
            fundamental_data['ticker'] = ticker
            fundamental_data['sector'] = info.get('sector')
            fundamental_data['industry'] = info.get('industry')
            fundamental_data['company_name'] = info.get('longName')
            fundamental_data['beta'] = info.get('beta')

            # Only hard filters are: market cap, volume, and price decline
            is_candidate = all(passed_filters.values())

            return FilterResult(
                ticker=ticker,
                passed_filters=passed_filters,
                fundamental_data=fundamental_data,
                is_candidate=is_candidate
            )

        except Exception as e:
            # Silently skip problematic tickers
            return None

    def screen_universe(self, tickers: List[str], limit: int = None) -> List[FilterResult]:
        """Screen multiple stocks in parallel."""
        candidates = []
        total = len(tickers[:limit]) if limit else len(tickers)

        print(f"Screening {total} stocks...", file=sys.stderr)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.screen_stock, ticker): ticker for ticker in (tickers[:limit] if limit else tickers)}

            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                ticker = futures[future]
                if i % 50 == 0:
                    print(f"Progress: {i}/{total}", file=sys.stderr)

                try:
                    result = future.result(timeout=30)
                    if result and result.is_candidate:
                        candidates.append(result)
                        print(f"✓ Candidate found: {ticker}", file=sys.stderr)
                except Exception:
                    pass

        print(f"Found {len(candidates)} candidates from {total} stocks screened", file=sys.stderr)
        return candidates

    def format_output(self, candidates: List[FilterResult]) -> str:
        """Format screening results for LLM agent vetting."""
        if not candidates:
            return "No candidates found. Consider relaxing filter criteria."

        output = []
        output.append("# VALUE HUNTING SCREENING RESULTS")
        output.append(f"Found {len(candidates)} candidate(s) passing initial filters")
        output.append("\nInitial filters applied: Market Cap >= $200M, ADV >= 500K, Down 15-60% from 52W High")
        output.append("=" * 80)

        for c in candidates:
            d = c.fundamental_data
            output.append(f"\n## {c.ticker}: {d.get('company_name', 'N/A')}")
            output.append(f"Sector: {d.get('sector', 'N/A')} | Industry: {d.get('industry', 'N/A')}")

            output.append("\n### Price & Volume")
            output.append(f"  Current Price: ${d.get('current_price', 0):.2f}")
            output.append(f"  52W Range: ${d.get('fifty_two_week_low', 0):.2f} - ${d.get('fifty_two_week_high', 0):.2f}")
            output.append(f"  Decline from High: {d.get('decline_from_high_pct', 0):.1f}%")
            output.append(f"  Market Cap: ${d.get('market_cap', 0)/1e9:.2f}B")
            output.append(f"  Avg Daily Volume: {d.get('avg_daily_volume', 0):.0f}")

            output.append("\n### Valuation Metrics")
            if d.get('trailing_pe'):
                output.append(f"  P/E (trailing): {d['trailing_pe']:.2f}x")
            if d.get('forward_pe'):
                output.append(f"  P/E (forward): {d['forward_pe']:.2f}x")
            if d.get('price_to_book'):
                output.append(f"  P/B: {d['price_to_book']:.2f}x")
            if d.get('price_to_sales'):
                output.append(f"  P/S: {d['price_to_sales']:.2f}x")
            if d.get('ev_ebitda'):
                output.append(f"  EV/EBITDA: {d['ev_ebitda']:.2f}x")
            if d.get('peg_ratio'):
                output.append(f"  PEG: {d['peg_ratio']:.2f}")

            output.append("\n### Profitability")
            if d.get('roe') is not None:
                output.append(f"  ROE: {d['roe']*100:.1f}%")
            if d.get('roa') is not None:
                output.append(f"  ROA: {d['roa']*100:.1f}%")
            if d.get('roic') is not None:
                output.append(f"  ROIC: {d['roic']*100:.1f}%")
            if d.get('profit_margins') is not None:
                output.append(f"  Profit Margin: {d['profit_margins']*100:.1f}%")
            if d.get('operating_margins') is not None:
                output.append(f"  Operating Margin: {d['operating_margins']*100:.1f}%")
            if d.get('gross_margins') is not None:
                output.append(f"  Gross Margin: {d['gross_margins']*100:.1f}%")

            output.append("\n### Balance Sheet")
            if d.get('debt_to_equity') is not None:
                output.append(f"  Debt/Equity: {d['debt_to_equity']:.2f}")
            if d.get('current_ratio'):
                output.append(f"  Current Ratio: {d['current_ratio']:.2f}")
            if d.get('quick_ratio'):
                output.append(f"  Quick Ratio: {d['quick_ratio']:.2f}")
            if d.get('total_cash'):
                output.append(f"  Total Cash: ${d['total_cash']/1e9:.2f}B")
            if d.get('total_debt'):
                output.append(f"  Total Debt: ${d['total_debt']/1e9:.2f}B")
            if d.get('interest_coverage'):
                output.append(f"  Interest Coverage: {d['interest_coverage']:.1f}x")

            output.append("\n### Cash Flow")
            if d.get('fcf_yield') is not None:
                output.append(f"  FCF Yield: {d['fcf_yield']*100:.1f}%")
            if d.get('operating_cashflow'):
                output.append(f"  Operating CF: ${d['operating_cashflow']/1e9:.2f}B")
            if d.get('free_cashflow'):
                output.append(f"  Free CF: ${d['free_cashflow']/1e9:.2f}B")

            output.append("\n### Growth")
            if d.get('revenue_growth_yoy') is not None:
                output.append(f"  Revenue Growth (YoY): {d['revenue_growth_yoy']*100:.1f}%")
            if d.get('quarterly_revenue_growth_yoy') is not None:
                output.append(f"  Revenue Growth (Quarterly YoY): {d['quarterly_revenue_growth_yoy']*100:.1f}%")
            if d.get('earnings_growth_yoy') is not None:
                output.append(f"  Earnings Growth (YoY): {d['earnings_growth_yoy']*100:.1f}%")

            output.append("\n### Other")
            if d.get('dividend_yield'):
                output.append(f"  Dividend Yield: {d['dividend_yield']*100:.1f}%")
            if d.get('beta'):
                output.append(f"  Beta: {d['beta']:.2f}")

            output.append("\n" + "-" * 80)

        output.append("\n### Next Steps for LLM Agent:")
        output.append("1. Assess quality of balance sheet (debt levels, interest coverage)")
        output.append("2. Evaluate ROIC/ROE trends and sustainability")
        output.append("3. Check FCF yield quality and growth")
        output.append("4. Identify economic moat sources")
        output.append("5. Screen for value traps (secular decline vs cyclical downturn)")
        output.append("6. Calculate margin of safety and intrinsic value")

        return "\n".join(output)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Value Hunting Screener')
    parser.add_argument('--tickers', nargs='+', help='Specific tickers to screen')
    parser.add_argument('--limit', type=int, help='Limit number of stocks to screen')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--workers', type=int, default=10, help='Number of parallel workers')
    parser.add_argument('--strategy', type=str, default='investment',
                        choices=['scalping', 'swing', 'position', 'investment'],
                        help='Trading strategy timeframe (default: investment)')

    args = parser.parse_args()

    hunter = ValueHunter(max_workers=args.workers, strategy=args.strategy)

    # Get ticker universe
    if args.tickers:
        tickers = [t.upper().strip() for t in args.tickers]
    else:
        tickers = hunter.fetch_nasdaq_list()

    # Screen the universe
    candidates = hunter.screen_universe(tickers, limit=args.limit)

    # Output results
    if args.json:
        output = [asdict(c) for c in candidates]
        print(json.dumps(output, indent=2, default=str))
    else:
        print(hunter.format_output(candidates))


if __name__ == '__main__':
    main()
