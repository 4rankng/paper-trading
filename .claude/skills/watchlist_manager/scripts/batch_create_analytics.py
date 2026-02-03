#!/usr/bin/env python3
"""Create fundamental and thesis markdown files for stocks that only have technical data."""

import os
import json

# Stock metadata for creating thesis files
STOCK_INFO = {
    "BBAI": {"name": "BigBear.ai", "sector": "Technology", "industry": "Information Technology Services", "type": "moonshot"},
    "RIG": {"name": "Transocean", "sector": "Energy", "industry": "Oil & Gas Drilling", "type": "moonshot"},
    "VAL": {"name": "Valaris", "sector": "Energy", "industry": "Oil & Gas Equipment & Services", "type": "compounder"},
    "BA": {"name": "Boeing", "sector": "Industrials", "industry": "Aerospace & Defense", "type": "moonshot"},
    "OXY": {"name": "Occidental Petroleum", "sector": "Energy", "industry": "Oil & Gas E&P", "type": "moonshot"},
    "STNG": {"name": "Scorpio Tankers", "sector": "Energy", "industry": "Oil & Gas Midstream", "type": "compounder"},
    "BORR": {"name": "Borr Drilling", "sector": "Energy", "industry": "Oil & Gas Drilling", "type": "moonshot"},
    "AAPL": {"name": "Apple", "sector": "Technology", "industry": "Consumer Electronics", "type": "compounder"},
    "TSLA": {"name": "Tesla", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers", "type": "moonshot"},
    "APLD": {"name": "Applied Digital", "sector": "Technology", "industry": "Information Technology Services", "type": "moonshot"},
}

# Fundamental data from yfinance (cached from earlier run)
FUNDAMENTAL_DATA = {
    "BBAI": {"market_cap": 2598542336, "current_price": 5.675, "trailing_pe": None, "forward_pe": -28.375, "price_to_sales": 18.02, "profit_margins": -2.956, "operating_margins": -0.533, "gross_margins": 0.273, "return_on_equity": -1.203, "debt_to_equity": 18.506, "current_ratio": 3.131, "beta": 3.214},
    "RIG": {"market_cap": 5418760192, "current_price": 4.92, "trailing_pe": None, "forward_pe": 31.97, "price_to_sales": 1.40, "profit_margins": -0.757, "operating_margins": 0.231, "gross_margins": 0.392, "return_on_equity": -0.320, "debt_to_equity": 77.012, "current_ratio": 1.081, "beta": 1.364},
    "VAL": {"market_cap": 4206579200, "current_price": 59.07, "trailing_pe": 10.57, "forward_pe": 15.79, "price_to_sales": 1.74, "profit_margins": 0.165, "operating_margins": 0.211, "gross_margins": 0.325, "return_on_equity": 0.172, "debt_to_equity": 47.486, "current_ratio": 1.871, "beta": 1.179},
    "BA": {"market_cap": 188342337536, "current_price": 240.52, "trailing_pe": 96.59, "forward_pe": 41.74, "price_to_sales": 2.11, "profit_margins": 0.025, "operating_margins": -0.032, "gross_margins": 0.048, "return_on_equity": 2.90, "debt_to_equity": 1035.92, "current_ratio": 1.188, "beta": 1.163},
    "OXY": {"market_cap": 45280272384, "current_price": 46.03, "trailing_pe": 33.79, "forward_pe": 38.53, "price_to_sales": 1.70, "profit_margins": 0.082, "operating_margins": 0.177, "gross_margins": 0.636, "return_on_equity": 0.060, "debt_to_equity": 62.221, "current_ratio": 0.935, "beta": 0.38},
    "STNG": {"market_cap": 3196611328, "current_price": 61.76, "trailing_pe": 10.31, "forward_pe": 10.80, "price_to_sales": 3.59, "profit_margins": 0.320, "operating_margins": 0.342, "gross_margins": 0.627, "return_on_equity": 0.096, "debt_to_equity": 28.769, "current_ratio": 4.806, "beta": -0.284},
    "BORR": {"market_cap": 1405047808, "current_price": 4.58, "trailing_pe": 16.35, "forward_pe": -48.66, "price_to_sales": 1.37, "profit_margins": 0.071, "operating_margins": 0.354, "gross_margins": 0.552, "return_on_equity": 0.068, "debt_to_equity": 180.379, "current_ratio": 1.626, "beta": 1.087},
    "AAPL": {"market_cap": 3798852435968, "current_price": 257.09, "trailing_pe": 34.46, "forward_pe": 28.12, "price_to_sales": 9.13, "profit_margins": 0.269, "operating_margins": 0.316, "gross_margins": 0.469, "return_on_equity": 1.714, "debt_to_equity": 152.411, "current_ratio": 0.893, "beta": 1.093},
    "TSLA": {"market_cap": 1403728560128, "current_price": 422.07, "trailing_pe": 287.12, "forward_pe": 142.22, "price_to_sales": 14.68, "profit_margins": 0.053, "operating_margins": 0.066, "gross_margins": 0.170, "return_on_equity": 0.068, "debt_to_equity": 17.082, "current_ratio": 2.066, "beta": 1.835},
    "APLD": {"market_cap": 10643831808, "current_price": 38.11, "trailing_pe": None, "forward_pe": -42.54, "price_to_sales": 40.32, "profit_margins": -0.474, "operating_margins": -0.245, "gross_margins": 0.196, "return_on_equity": -0.079, "debt_to_equity": 125.912, "current_ratio": 4.823, "beta": 6.924},
}


def create_fundamental_md(ticker: str, data: dict, info: dict) -> str:
    """Create fundamental analysis markdown content."""
    pe_ttm = data.get('trailing_pe', 'N/A')
    pe_fwd = data.get('forward_pe', 'N/A')
    ps = data.get('price_to_sales', 'N/A')

    return f"""# {ticker} Fundamental Analysis

**Date:** 2026-01-29
**Current Price:** ${data.get('current_price', 'N/A')}

## Company Profile
- **Sector:** {info['sector']}
- **Industry:** {info['industry']}
- **Market Cap:** ${data.get('market_cap', 0) / 1e9:.2f}B

## Valuation Metrics
- **P/E (TTM):** {pe_ttm if pe_ttm and pe_ttm > 0 else 'N/A'}
- **P/E (Forward):** {pe_fwd if pe_fwd and pe_fwd > 0 else 'N/A'}
- **Price/Sales:** {ps:.2f}

## Profitability
- **Profit Margin:** {data.get('profit_margins', 0) * 100:.2f}%
- **Operating Margin:** {data.get('operating_margins', 0) * 100:.2f}%
- **Gross Margin:** {data.get('gross_margins', 0) * 100:.2f}%
- **ROE:** {data.get('return_on_equity', 0) * 100:.2f}%

## Financial Health
- **Debt/Equity:** {data.get('debt_to_equity', 'N/A')}
- **Current Ratio:** {data.get('current_ratio', 'N/A')}

## Risk Metrics
- **Beta:** {data.get('beta', 'N/A')}
"""


def create_thesis_md(ticker: str, info: dict) -> str:
    """Create investment thesis markdown content."""
    type_key = "compounder" if info['type'] == 'compounder' else "moonshot"

    theses = {
        "BBAI": "**Thesis:** AI/ML analytics for government and enterprise. Defense sector exposure. Small-cap with 10x potential but unprofitable. High beta (3.2) indicates volatility. Waiting for path to profitability.\n\n**Key Catalysts:** Government AI contracts, commercial adoption, profitability milestone.\n\n**Risks:** Cash burn, competition from larger AI players, dilution.",
        "RIG": "**Thesis:** Offshore drilling cycle recovery. Day rates improving for ultra-deepwater rigs. Fleeted down to high-spec assets. Berkshire-backed energy play via OXY ownership.\n\n**Key Catalysts:** Day rate increases, contract awards, oil price stability.\n\n**Risks:** Cycle downturn, day rate pressure, debt.",
        "VAL": "**Thesis:** Premium offshore drilling with high-spec jackups. Strong dividend potential. Low PE (10.6) compared to peers. Quality compounder in energy services.\n\n**Key Catalysts:** Day rate improvements, contract extensions, shareholder returns.\n\n**Risks:** Cycle volatility, competition.",
        "BA": "**Thesis:** Aerospace turnaround. 737 MAX issues fading, 787 deliveries resuming. New CEO turnaround. Massive moat in duopoly with Airbus. Near-term pain, long-term gain.\n\n**Key Catalysts:** 737 production rate increase, 787 certification, FAA resolution.\n\n**Risks:** Regulatory issues, production delays, debt load.",
        "OXY": "**Thesis:** Berkshire Hathaway-backed energy giant. Carbon capture pioneer (Direct Air Capture). Permian basin assets. Buffett seal of approval.\n\n**Key Catalysts:** Oil prices, carbon capture commercialization, dividend increases.\n\n**Risks:** Oil price volatility, carbon capture economics, debt.",
        "STNG": "**Thesis:** Product tanker leader with modern fleet. Strong dividends. Low PE (10.3). Quality compounder with shareholder returns. Negative beta (-0.28) provides hedge.\n\n**Key Catalysts:** Tanker rates, dividends, fleet utilization.\n\n**Risks:** Rates cyclicality, fuel costs, geopolitical.",
        "BORR": "**Thesis:** Premium jackup drilling focused on North Sea/Middle East. High-spec fleet. Day rate upside. Small-cap moonshot in drilling recovery.\n\n**Key Catalysts:** Day rate increases, contract awards, fleet modernization.\n\n**Risks:** Day rate pressure, debt, competition.",
        "AAPL": "**Thesis:** Ultimate compounder. Ecosystem lock-in unmatched. Services revenue growing. Capital returns via dividends/buybacks. Warren Buffett's largest holding.\n\n**Key Catalysts:** AI iPhone cycle, services growth, emerging market penetration.\n\n**Risks:** China exposure, innovation stagnation, regulation.",
        "TSLA": "**Thesis:** EV leader transitioning to AI/robotics company. FSD potential, Optimus robot, energy storage. Elon Musk vision premium. Moonshot with 10x potential.\n\n**Key Catalysts:** FSD milestones, Optimus progress, Model 2 launch, energy storage growth.\n\n**Risks:** Execution risk, competition, Musk key person, valuation.",
        "APLD": "**Thesis:** AI data center infrastructure play. High-performance computing for AI models. 1000%+ move in past year. Unprofitable but growing.\n\n**Key Catalysts:** AI capex boom, customer wins, profitability.\n\n**Risks:** Competition, customer concentration, dilution, valuation.",
    }

    thesis_content = theses.get(ticker, f"**Thesis:** {info['name']} is a {type_key} in {info['sector']}.\n\n**Research needed.**")

    return f"""# {ticker} Investment Thesis

**Date:** 2026-01-29
**Investment Type:** {type_key}

## Thesis Summary

{thesis_content}

## Strategy Fit

**Analysis needed** - Technical and fundamental analysis will determine strategy classification.
"""


def main():
    """Create missing analytics files for all stocks."""
    for ticker, info in STOCK_INFO.items():
        fund_data = FUNDAMENTAL_DATA.get(ticker, {})
        dir_path = f"analytics/{ticker}"
        os.makedirs(dir_path, exist_ok=True)

        # Create fundamental analysis
        fund_file = f"{dir_path}/{ticker}_fundamental_analysis.md"
        if not os.path.exists(fund_file):
            with open(fund_file, 'w') as f:
                f.write(create_fundamental_md(ticker, fund_data, info))
            print(f"✓ Created {fund_file}")

        # Create investment thesis
        thesis_file = f"{dir_path}/{ticker}_investment_thesis.md"
        if not os.path.exists(thesis_file):
            with open(thesis_file, 'w') as f:
                f.write(create_thesis_md(ticker, info))
            print(f"✓ Created {thesis_file}")

    print("\nAll analytics files created successfully.")


if __name__ == "__main__":
    main()
