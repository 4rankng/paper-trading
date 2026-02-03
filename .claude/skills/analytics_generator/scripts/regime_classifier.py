#!/usr/bin/env python3
"""
Market Regime Classification Module

Detects the current market regime based on technical indicators.
Regimes: trending_up, trending_down, ranging, volatile

Used to adjust signal weights in the technical analysis aggregation system.
"""
from typing import Dict, Tuple, Optional
import numpy as np


class RegimeClassifier:
    """Classify market regime using technical indicators."""

    # Thresholds for regime detection
    ADX_STRONG_TREND = 25
    ADX_WEAK_TREND = 20
    ATR_HIGH_VOLATILITY_PCT = 2.0  # ATR > 2% of price
    ATR_EXTREME_VOLATILITY_PCT = 3.5  # ATR > 3.5% of price
    MA_SLOPE_THRESHOLD = 0.5  # % change for rising/falling MA

    def __init__(self, indicators: Dict):
        """
        Initialize with technical indicators dictionary.

        Args:
            indicators: Dictionary from TechnicalIndicators.calculate_all()
        """
        self.indicators = indicators
        self.regime = None
        self.confidence = 0.0
        self.regime_data = {}

    def classify(self) -> Dict:
        """
        Classify the current market regime.

        Returns:
            Dictionary with regime, confidence, and supporting data
        """
        # Extract key indicators
        adx = self._get_adx()
        atr_pct = self._get_atr_pct()
        price = self.indicators.get('current_price', 0)
        trend = self.indicators.get('trend', {})
        advanced = self.indicators.get('advanced', {})

        # Get trend components
        price_vs_short = trend.get('price_vs_short_ma', 'unknown')
        price_vs_long = trend.get('price_vs_long_ma', 'unknown')
        short_ma_slope = trend.get('short_ma_slope', 'flat')
        long_ma_slope = trend.get('long_ma_slope', 'flat')
        ma_crossover = trend.get('short_ma_vs_long_ma', 'unknown')
        trend_strength = trend.get('strength', 'weak')
        trend_direction = trend.get('trend', 'sideways')

        # Get additional trend indicators
        plus_di = advanced.get('plus_di', 0)
        minus_di = advanced.get('minus_di', 0)
        dx = advanced.get('dx', 0)

        # Calculate volatility score
        volatility_score = self._calculate_volatility_score()

        # Determine regime
        regime, confidence, reasoning = self._determine_regime(
            adx, atr_pct, volatility_score,
            price_vs_short, price_vs_long,
            short_ma_slope, long_ma_slope,
            ma_crossover, trend_strength, trend_direction,
            plus_di, minus_di, dx
        )

        self.regime = regime
        self.confidence = confidence
        self.regime_data = {
            'regime': regime,
            'confidence': confidence,
            'reasoning': reasoning,
            'adx': adx,
            'atr_pct': atr_pct,
            'volatility_score': volatility_score,
            'trend_direction': trend_direction,
            'trend_strength': trend_strength
        }

        return self.regime_data

    def _get_adx(self) -> float:
        """Extract ADX value from indicators."""
        adx_data = self.indicators.get('advanced', {}).get('adx', {})
        return adx_data.get('current', 0.0)

    def _get_atr_pct(self) -> float:
        """Extract ATR percentage from indicators."""
        atr_data = self.indicators.get('atr', {})
        return atr_data.get('current_pct', 0.0)

    def _calculate_volatility_score(self) -> float:
        """
        Calculate a volatility score (0-100) based on multiple indicators.

        Higher = more volatile
        """
        score = 0.0

        # ATR percentage contribution
        atr_pct = self._get_atr_pct()
        if atr_pct > 3.0:
            score += 40
        elif atr_pct > 2.0:
            score += 25
        elif atr_pct > 1.0:
            score += 10

        # Bollinger Bandwidth contribution
        bb = self.indicators.get('bollinger_bands', {})
        if bb:
            bandwidth = bb.get('bandwidth', 0)
            price = self.indicators.get('current_price', 1)
            if price > 0:
                bb_pct = (bandwidth / price) * 100
                if bb_pct > 8:
                    score += 30
                elif bb_pct > 5:
                    score += 20
                elif bb_pct > 3:
                    score += 10

        # 30-day volatility contribution
        stat = self.indicators.get('statistical', {})
        vol_std = stat.get('volatility_std_30d', 0)
        if vol_std > 3.0:
            score += 30
        elif vol_std > 2.0:
            score += 20
        elif vol_std > 1.0:
            score += 10

        return min(score, 100.0)

    def _determine_regime(
        self,
        adx: float,
        atr_pct: float,
        volatility_score: float,
        price_vs_short: str,
        price_vs_long: str,
        short_ma_slope: str,
        long_ma_slope: str,
        ma_crossover: str,
        trend_strength: str,
        trend_direction: str,
        plus_di: float,
        minus_di: float,
        dx: float
    ) -> Tuple[str, float, list]:
        """
        Determine regime based on all indicators.

        Returns:
            Tuple of (regime_name, confidence, reasoning_list)
        """
        reasoning = []
        confidence_scores = {}
        regime_votes = []

        # Check for extreme volatility first (overrides other conditions)
        if volatility_score > 70 or atr_pct > self.ATR_EXTREME_VOLATILITY_PCT:
            regime_votes.append(('volatile', 0.8))
            reasoning.append(f"Extreme volatility detected (score: {volatility_score:.0f}, ATR: {atr_pct:.2f}%)")

        # Check trend strength using ADX
        strong_trend = adx >= self.ADX_STRONG_TREND
        weak_trend = adx < self.ADX_WEAK_TREND

        if strong_trend:
            reasoning.append(f"Strong trend detected (ADX: {adx:.2f})")
        elif weak_trend:
            reasoning.append(f"Weak/no trend (ADX: {adx:.2f})")
        else:
            reasoning.append(f"Developing trend (ADX: {adx:.2f})")

        # Check directional indicators
        bullish_direction = (
            price_vs_short == 'above' and
            price_vs_long == 'above' and
            ma_crossover == 'bullish' and
            plus_di > minus_di
        )

        bearish_direction = (
            price_vs_short == 'below' and
            price_vs_long == 'below' and
            ma_crossover == 'bearish' and
            minus_di > plus_di
        )

        # Check for ranging conditions
        ranging_conditions = (
            weak_trend and
            trend_direction == 'sideways' and
            short_ma_slope == 'flat' and
            long_ma_slope == 'flat'
        )

        # Score each regime possibility
        if strong_trend:
            if bullish_direction:
                score = 0.7
                if trend_strength == 'strong':
                    score += 0.2
                if short_ma_slope == 'rising' and long_ma_slope == 'rising':
                    score += 0.1
                confidence_scores['trending_up'] = score
                regime_votes.append(('trending_up', score))
                reasoning.append("Bullish trend alignment confirmed")

            elif bearish_direction:
                score = 0.7
                if trend_strength == 'strong':
                    score += 0.2
                if short_ma_slope == 'falling' and long_ma_slope == 'falling':
                    score += 0.1
                confidence_scores['trending_down'] = score
                regime_votes.append(('trending_down', score))
                reasoning.append("Bearish trend alignment confirmed")

        if ranging_conditions:
            score = 0.6
            if atr_pct < 1.5:  # Low volatility confirms range
                score += 0.2
            confidence_scores['ranging'] = score
            regime_votes.append(('ranging', score))
            reasoning.append("Ranging market conditions detected")

        # Check for volatile but not trending
        if volatility_score > 50 and weak_trend:
            score = 0.6
            confidence_scores['volatile'] = score
            regime_votes.append(('volatile', score))
            reasoning.append(f"High volatility without trend (vol score: {volatility_score:.0f})")

        # Determine final regime
        if regime_votes:
            # Sort by confidence score
            regime_votes.sort(key=lambda x: x[1], reverse=True)
            final_regime = regime_votes[0][0]
            final_confidence = regime_votes[0][1]
        else:
            # Default to ranging if unclear
            final_regime = 'ranging'
            final_confidence = 0.3
            reasoning.append("Insufficient data - defaulting to ranging")

        return final_regime, min(final_confidence, 1.0), reasoning


def classify_regime(indicators: Dict) -> Dict:
    """
    Convenience function to classify market regime.

    Args:
        indicators: Dictionary from TechnicalIndicators.calculate_all()

    Returns:
        Dictionary with regime, confidence, and supporting data
    """
    classifier = RegimeClassifier(indicators)
    return classifier.classify()


def get_regime_weights(regime: str, config: Dict) -> Dict[str, float]:
    """
    Get signal category weights for a given regime.

    Args:
        regime: The regime name (trending_up, trending_down, ranging, volatile)
        config: Full configuration dictionary

    Returns:
        Dictionary of category weights (momentum, trend, volatility, volume, ob_os)
    """
    return config.get('regimes', {}).get(regime, {
        'momentum': 0.20,
        'trend': 0.20,
        'volatility': 0.20,
        'volume': 0.20,
        'ob_os': 0.20
    })


if __name__ == '__main__':
    # Test the regime classifier
    import sys
    from pathlib import Path

    # Dynamic path resolution
    script_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(script_dir))
    project_root = script_dir.parents[3]  # Go up 3 levels from scripts/ to project root
    csv_path = project_root / 'prices' / 'AAPL.csv'

    if csv_path.exists():
        df = pd.read_csv(csv_path)
        data = []
        for _, row in df.iterrows():
            data.append({
                'date': row['Date'] if 'Date' in row.index else row.iloc[0],
                'open': float(row['Open'] if 'Open' in row.index else row.iloc[1]),
                'high': float(row['High'] if 'High' in row.index else row.iloc[2]),
                'low': float(row['Low'] if 'Low' in row.index else row.iloc[3]),
                'close': float(row['Close'] if 'Close' in row.index else row.iloc[4]),
                'volume': float(row['Volume'] if 'Volume' in row.index else row.iloc[5])
            })

        ti = TechnicalIndicators(data)
        indicators = ti.calculate_all()

        classifier = RegimeClassifier(indicators)
        result = classifier.classify()

        print("Market Regime Classification:")
        print(f"  Regime: {result['regime']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Reasoning:")
        for r in result['reasoning']:
            print(f"    - {r}")
        print(f"  ADX: {result['adx']:.2f}")
        print(f"  ATR %: {result['atr_pct']:.2f}%")
        print(f"  Volatility Score: {result['volatility_score']:.0f}")
    else:
        print(f"Price file not found: {csv_path}")
