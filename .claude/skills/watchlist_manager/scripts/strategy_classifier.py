#!/usr/bin/env python3
"""
Strategy Classifier for Watchlist Manager

Classifies stocks into one of 10 trading strategies based on their metrics.
Each stock gets assigned to its single best-fitting strategy.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass
class StrategyResult:
    """Result of classifying a stock against a strategy."""
    strategy_name: str
    fit_score: int  # 0-100
    holding_period: str
    holding_priority: int  # Higher = longer holding period preferred
    checks: Dict[str, Any]  # Which criteria passed/failed
    missing_data: List[str]  # Metrics that couldn't be evaluated


# Strategy definitions with criteria and holding periods
STRATEGIES: Dict[str, Dict[str, Any]] = {
    # Day Trader / Scalping (1-10 days)
    "gap_and_go": {
        "holding_period": "1-10d",
        "priority": 1,  # Lower priority = shorter holding period
        "description": "Gap & Go - Morning momentum after news catalyst",
        "criteria": {
            "gap_pct_gt_3": {"threshold": 3.0, "direction": "above", "weight": 30},
            "volume_ratio_gt_2": {"threshold": 2.0, "direction": "above", "weight": 30},
            "price_above_prev_high": {"threshold": True, "direction": "exact", "weight": 40},
        }
    },
    "intraday_reversal": {
        "holding_period": "1-10d",
        "priority": 1,
        "description": "Intraday Reversal - Blown out stocks due for bounce",
        "criteria": {
            "rsi_lt_25": {"threshold": 25.0, "direction": "below", "weight": 35},
            "price_below_lower_bb": {"threshold": True, "direction": "exact", "weight": 35},
            "kdj_j_lt_0": {"threshold": 0.0, "direction": "below", "weight": 30},
        }
    },
    "high_relative_vol": {
        "holding_period": "1-10d",
        "priority": 1,
        "description": "High Relative Vol - Fast price action",
        "criteria": {
            "vol_ratio_gt_3": {"threshold": 3.0, "direction": "above", "weight": 35},
            "iv_rank_gt_70": {"threshold": 70.0, "direction": "above", "weight": 35},
            "atr_increasing": {"threshold": True, "direction": "exact", "weight": 30},
        }
    },

    # Swing Trader (2 weeks - 3 months)
    "trend_rider": {
        "holding_period": "2w-3m",
        "priority": 2,
        "description": "Trend Rider - Ride the strongest stocks",
        "criteria": {
            "price_above_ma20": {"threshold": True, "direction": "exact", "weight": 25},
            "ma20_above_ma50": {"threshold": True, "direction": "exact", "weight": 25},
            "rsi_gt_60": {"threshold": 60.0, "direction": "above", "weight": 25},
            "near_52w_high": {"threshold": 5.0, "direction": "within_pct", "weight": 25},
        }
    },
    "mean_reversion": {
        "holding_period": "2w-3m",
        "priority": 2,
        "description": "Mean Reversion - Buy the dip in healthy stocks",
        "criteria": {
            "price_below_ma20": {"threshold": True, "direction": "exact", "weight": 30},
            "rsi_30_40": {"threshold": (30.0, 40.0), "direction": "between", "weight": 35},
            "bullish_macd_cross": {"threshold": True, "direction": "exact", "weight": 35},
        }
    },
    "volatility_squeeze": {
        "holding_period": "2w-3m",
        "priority": 2,
        "description": "Volatility Squeeze - Coiling for breakout",
        "criteria": {
            "bb_width_lt_10": {"threshold": 10.0, "direction": "below", "weight": 50},
            "volume_decreasing": {"threshold": True, "direction": "exact", "weight": 50},
        }
    },

    # Position Trader (3-6 months)
    "canslim": {
        "holding_period": "3-6m",
        "priority": 3,
        "description": "CANSLIM - High-growth leaders with institutional backing",
        "criteria": {
            "eps_growth_gt_25": {"threshold": 25.0, "direction": "above", "weight": 35},
            "sales_growth_gt_25": {"threshold": 25.0, "direction": "above", "weight": 35},
            "rs_rating_gt_80": {"threshold": 80.0, "direction": "above", "weight": 30},
        }
    },
    "golden_cross": {
        "holding_period": "3-6m",
        "priority": 3,
        "description": "Golden Cross - Birth of new bull trend",
        "criteria": {
            "ma50_above_ma200": {"threshold": True, "direction": "exact", "weight": 50},
            "price_above_ma200": {"threshold": True, "direction": "exact", "weight": 50},
        }
    },

    # Long-Term Investor (1 year+)
    "quality_discount": {
        "holding_period": "1y+",
        "priority": 4,  # Highest priority
        "description": "Quality at a Discount - World-class businesses undervalued",
        "criteria": {
            "roe_gt_15": {"threshold": 15.0, "direction": "above", "weight": 40},
            "debt_equity_lt_0.5": {"threshold": 0.5, "direction": "below", "weight": 30},
            "pe_lt_peers": {"threshold": True, "direction": "exact", "weight": 30},  # P/E below sector/peers
        }
    },
    "dividend_aristocrat": {
        "holding_period": "1y+",
        "priority": 4,
        "description": "Dividend Aristocrat - Passive income with safe companies",
        "criteria": {
            "div_yield_gt_3": {"threshold": 3.0, "direction": "above", "weight": 40},
            "payout_ratio_lt_60": {"threshold": 60.0, "direction": "below", "weight": 30},
            "div_10yr_growth": {"threshold": 0.0, "direction": "above", "weight": 30},
        }
    },
}


def get_metric_value(stock_data: Dict[str, Any], metric_key: str) -> Optional[Any]:
    """
    Extract a metric value from stock data.

    Handles various data sources:
    - Direct keys in stock_data
    - Nested in 'metrics' dict
    - Nested in 'fundamentals' or 'technicals' dicts
    """
    # Direct access
    if metric_key in stock_data:
        return stock_data[metric_key]

    # Check in common nested locations
    for nested_key in ['metrics', 'fundamentals', 'technicals', 'price_data']:
        if nested_key in stock_data and metric_key in stock_data[nested_key]:
            return stock_data[nested_key][metric_key]

    # Check in score_card components (legacy data)
    if 'score_card' in stock_data and 'components' in stock_data['score_card']:
        component_map = {
            'growth': 'growth',
            'value': 'value',
            'profitability': 'profitability',
            'momentum': 'momentum',
        }
        if metric_key in component_map:
            return stock_data['score_card']['components'].get(component_map[metric_key])

    return None


def evaluate_criterion(
    stock_data: Dict[str, Any],
    criterion_key: str,
    criterion_def: Dict[str, Any]
) -> tuple[bool, Optional[Any]]:
    """
    Evaluate a single criterion for a stock.

    Returns:
        (passed, actual_value)
    """
    value = get_metric_value(stock_data, criterion_key)

    if value is None:
        return False, None

    threshold = criterion_def['threshold']
    direction = criterion_def['direction']

    if direction == 'above':
        return float(value) > threshold, value
    elif direction == 'below':
        return float(value) < threshold, value
    elif direction == 'exact':
        return bool(value) == bool(threshold), value
    elif direction == 'between':
        low, high = threshold
        return low <= float(value) <= high, value
    elif direction == 'within_pct':
        # For "within X% of 52-week high"
        return float(value) <= threshold, value

    return False, value


def score_strategy(stock_data: Dict[str, Any], strategy_name: str) -> StrategyResult:
    """
    Score a stock against a single strategy.

    Returns:
        StrategyResult with fit score and checks
    """
    if strategy_name not in STRATEGIES:
        return StrategyResult(
            strategy_name=strategy_name,
            fit_score=0,
            holding_period="unknown",
            checks={},
            missing_data=[]
        )

    strategy = STRATEGIES[strategy_name]
    checks = {}
    missing_data = []
    total_weight = 0
    earned_weight = 0

    for criterion_key, criterion_def in strategy['criteria'].items():
        passed, actual_value = evaluate_criterion(stock_data, criterion_key, criterion_def)

        if actual_value is None:
            missing_data.append(criterion_key)
            checks[criterion_key] = {"passed": None, "value": None, "threshold": criterion_def['threshold']}
        else:
            weight = criterion_def['weight']
            total_weight += weight
            if passed:
                earned_weight += weight
            checks[criterion_key] = {
                "passed": passed,
                "value": actual_value,
                "threshold": criterion_def['threshold']
            }

    # Calculate fit score (0-100)
    if total_weight > 0:
        fit_score = int((earned_weight / total_weight) * 100)
    else:
        fit_score = 0

    # Penalize for missing data
    if missing_data:
        fit_score = max(0, fit_score - 20)

    return StrategyResult(
        strategy_name=strategy_name,
        fit_score=fit_score,
        holding_period=strategy['holding_period'],
        holding_priority=strategy['priority'],
        checks=checks,
        missing_data=missing_data
    )


def classify(stock_data: Dict[str, Any], min_fit_score: int = 40) -> Dict[str, Any]:
    """
    Classify a stock into its best-fitting strategy.

    Args:
        stock_data: Dictionary containing stock metrics
        min_fit_score: Minimum fit score to assign a strategy (default: 40)

    Returns:
        Dictionary with strategy classification results
    """
    results = []

    # Score against all strategies
    for strategy_name in STRATEGIES.keys():
        result = score_strategy(stock_data, strategy_name)
        results.append(result)

    # Sort by fit score, then by holding period priority (longer wins ties)
    results.sort(key=lambda r: (r.fit_score, r.holding_priority), reverse=True)

    best = results[0]

    # Determine final classification
    if best.fit_score < min_fit_score:
        # Doesn't fit any strategy well
        return {
            "name": "unclassified",
            "fit_score": best.fit_score,
            "holding_period": "unknown",
            "description": "Stock doesn't meet any strategy criteria",
            "checks": best.checks,
            "missing_data": best.missing_data,
            "top_alternatives": [
                {"strategy": r.strategy_name, "score": r.fit_score}
                for r in results[:3] if r.fit_score > 0
            ]
        }

    return {
        "name": best.strategy_name,
        "fit_score": best.fit_score,
        "holding_period": best.holding_period,
        "description": STRATEGIES[best.strategy_name]['description'],
        "checks": best.checks,
        "missing_data": best.missing_data,
        "top_alternatives": [
            {"strategy": r.strategy_name, "score": r.fit_score}
            for r in results[1:4] if r.fit_score > 0
        ]
    }


def get_strategy_list() -> List[Dict[str, str]]:
    """Return list of all available strategies with metadata."""
    return [
        {
            "name": name,
            "holding_period": s['holding_period'],
            "description": s['description']
        }
        for name, s in STRATEGIES.items()
    ]


if __name__ == "__main__":
    # Test with sample data
    test_stocks = {
        "growth_momentum": {
            "eps_growth": 30.0,
            "sales_growth": 28.0,
            "rs_rating": 85,
            "rsi": 65,
            "price_above_ma20": True,
            "ma20_above_ma50": True,
        },
        "value_stock": {
            "roe": 18.0,
            "debt_equity": 0.3,
            "pe_lt_peers": True,
            "pe": 12.0,
            "rsi": 35,
        },
        "dividend_stock": {
            "div_yield": 4.5,
            "payout_ratio": 55,
            "div_10yr_growth": 8.0,
            "roe": 14.0,
        },
        "oversold": {
            "rsi": 22,
            "price_below_lower_bb": True,
            "kdj_j_lt_0": -10,
        }
    }

    print("Strategy Classifier Tests\n" + "=" * 50)

    for name, data in test_stocks.items():
        result = classify(data)
        print(f"\n{name}:")
        print(f"  Strategy: {result['name']}")
        print(f"  Fit Score: {result['fit_score']}")
        print(f"  Holding Period: {result['holding_period']}")
        print(f"  Description: {result['description']}")
