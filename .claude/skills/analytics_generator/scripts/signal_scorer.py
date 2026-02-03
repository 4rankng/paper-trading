#!/usr/bin/env python3
"""
Signal Scorer Module

Maps individual technical indicators to scores from -1 (strongly bearish)
to +1 (strongly bullish). Groups signals into categories for aggregation.

Categories:
- momentum: RSI, MACD, Stochastic, Williams %R, CCI, MFI, etc.
- trend: ADX, Aroon, MA relationships, SAR, trendline
- volatility: ATR, Bollinger Bandwidth, statistical volatility
- volume: Volume ratio, OBV, A/D, price-volume correlation
- ob_os: Overbought/oversold composite signals
"""
from typing import Dict, List, Tuple, Optional
import numpy as np


class SignalScorer:
    """Score technical indicators on a -1 to +1 scale."""

    def __init__(self, indicators: Dict, config: Optional[Dict] = None):
        """
        Initialize with technical indicators and optional configuration.

        Args:
            indicators: Dictionary from TechnicalIndicators.calculate_all()
            config: Optional configuration dictionary for thresholds
        """
        self.indicators = indicators
        self.config = config or self._default_config()
        self.signal_scores = {}
        self.category_scores = {}

    def _default_config(self) -> Dict:
        """Return default configuration thresholds."""
        return {
            'rsi': {'overbought': 70, 'oversold': 30},
            'stochastic': {'overbought': 80, 'oversold': 20},
            'willr': {'overbought': -20, 'oversold': -80},
            'cci': {'overbought': 100, 'oversold': -100},
            'mfi': {'overbought': 80, 'oversold': 20},
            'adx': {'strong': 25, 'weak': 20},
            'bollinger_bandwidth': {'narrow': 0.02, 'wide': 0.08},
        }

    def score_all(self) -> Dict:
        """
        Score all technical indicators.

        Returns:
            Dictionary with individual signal scores and category aggregates
        """
        # Score individual signals by category
        momentum_signals = self._score_momentum()
        trend_signals = self._score_trend()
        volatility_signals = self._score_volatility()
        volume_signals = self._score_volume()
        obos_signals = self._score_obos()

        self.signal_scores = {
            'momentum': momentum_signals,
            'trend': trend_signals,
            'volatility': volatility_signals,
            'volume': volume_signals,
            'ob_os': obos_signals
        }

        # Calculate category scores
        self.category_scores = {
            'momentum': self._aggregate_category(momentum_signals),
            'trend': self._aggregate_category(trend_signals),
            'volatility': self._aggregate_category(volatility_signals),
            'volume': self._aggregate_category(volume_signals),
            'ob_os': self._aggregate_category(obos_signals)
        }

        return {
            'signal_scores': self.signal_scores,
            'category_scores': self.category_scores
        }

    def _aggregate_category(self, signals: Dict) -> float:
        """Aggregate signal scores within a category."""
        if not signals:
            return 0.0

        # Use weighted average based on signal strength
        # Stronger signals (closer to -1 or +1) get more weight
        values = []
        weights = []

        for name, score in signals.items():
            if score is not None and not np.isnan(score):
                values.append(score)
                # Weight by absolute value (stronger signals count more)
                weights.append(abs(score) + 0.5)

        if not values:
            return 0.0

        weighted_sum = sum(v * w for v, w in zip(values, weights))
        total_weight = sum(weights)

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _score_momentum(self) -> Dict:
        """Score momentum indicators."""
        scores = {}

        # RSI
        rsi_data = self.indicators.get('rsi', {})
        rsi = rsi_data.get('current', 50)
        scores['rsi'] = self._score_rsi(rsi)

        # MACD
        macd = self.indicators.get('macd', {})
        scores['macd_histogram'] = self._score_macd_histogram(
            macd.get('histogram', 0)
        )
        scores['macd_trend'] = self._score_macd_trend(macd.get('macd_trend', 'neutral'))

        # Stochastic
        stoch = self.indicators.get('stochastic', {})
        scores['stochastic_k'] = self._score_stochastic(stoch.get('k_value', 50))

        # Advanced indicators
        adv = self.indicators.get('advanced', {})

        # Williams %R
        willr = adv.get('willr', {})
        scores['willr'] = self._score_willr(willr.get('current', -50))

        # CCI
        cci = adv.get('cci', {})
        scores['cci'] = self._score_cci(cci.get('current', 0))

        # MFI
        mfi = adv.get('mfi', {})
        scores['mfi'] = self._score_mfi(mfi.get('current', 50))

        # Momentum
        mom = adv.get('momentum', 0)
        scores['momentum'] = self._normalize_to_score(mom, -10, 10, clip=True)

        # ROC
        roc = adv.get('roc', 0)
        scores['roc'] = self._normalize_to_score(roc, -5, 5, clip=True)

        # ROCR
        rocr = adv.get('rocr', 1.0)
        scores['rocr'] = self._score_rocr(rocr)

        # PPO
        ppo = adv.get('ppo', 0)
        scores['ppo'] = self._normalize_to_score(ppo, -3, 3, clip=True)

        # APO
        apo = adv.get('apo', 0)
        scores['apo'] = self._normalize_to_score(apo, -5, 5, clip=True)

        # TRIX
        trix = adv.get('trix', 0)
        scores['trix'] = self._normalize_to_score(trix, -0.5, 0.5, clip=True)

        # Ultimate Oscillator
        ultosc = adv.get('ultosc', 50)
        scores['ultimate_oscillator'] = self._score_ultosc(ultosc)

        return scores

    def _score_trend(self) -> Dict:
        """Score trend indicators."""
        scores = {}

        # ADX (trend strength, not direction - but we can combine with direction)
        adv = self.indicators.get('advanced', {})
        adx = adv.get('adx', {}).get('current', 0)

        # Get trend direction from main trend analysis
        trend = self.indicators.get('trend', {})
        trend_dir = trend.get('trend', 'sideways')

        # ADX scores - higher means stronger trend, but we need direction
        if trend_dir == 'uptrend':
            scores['adx'] = self._normalize_to_score(adx, 0, 50, clip=True)
        elif trend_dir == 'downtrend':
            scores['adx'] = -self._normalize_to_score(adx, 0, 50, clip=True)
        else:
            scores['adx'] = 0  # Neutral when sideways

        # Aroon
        aroon = adv.get('aroon', {})
        scores['aroon_oscillator'] = self._score_aroon_oscillator(
            aroon.get('oscillator', 0)
        )

        # Aroon Oscillator separate
        aroonosc = adv.get('aroonosc', 0)
        scores['aroonosc'] = self._normalize_to_score(aroonosc, -100, 100, clip=True)

        # Plus/Minus DI
        plus_di = adv.get('plus_di', 0)
        minus_di = adv.get('minus_di', 0)
        scores['di_difference'] = self._score_di_difference(plus_di, minus_di)

        # DX (Directional Movement Index)
        dx = adv.get('dx', 0)
        if trend_dir == 'uptrend':
            scores['dx'] = self._normalize_to_score(dx, 0, 50, clip=True)
        elif trend_dir == 'downtrend':
            scores['dx'] = -self._normalize_to_score(dx, 0, 50, clip=True)
        else:
            scores['dx'] = 0

        # Price vs MAs
        scores['price_vs_ma20'] = self._score_price_vs_ma(20)
        scores['price_vs_ma50'] = self._score_price_vs_ma(50)
        scores['price_vs_ma200'] = self._score_price_vs_ma(200)

        # MA Crossover (golden cross / death cross)
        ma_data = self.indicators.get('moving_averages', {})
        ma20 = ma_data.get('ma_20', 0)
        ma50 = ma_data.get('ma_50', 0)
        ma200 = ma_data.get('ma_200', 0)
        scores['ma_cross_short'] = self._score_ma_cross(ma20, ma50)
        scores['ma_cross_long'] = self._score_ma_cross(ma50, ma200)

        # MA Slopes
        short_slope = trend.get('short_ma_slope', 'flat')
        long_slope = trend.get('long_ma_slope', 'flat')
        scores['ma_slope_short'] = self._score_ma_slope(short_slope)
        scores['ma_slope_long'] = self._score_ma_slope(long_slope)

        # Parabolic SAR
        sar = self.indicators.get('sar', 0)
        price = self.indicators.get('current_price', 0)
        scores['parabolic_sar'] = self._score_sar(price, sar)

        # Trendline
        trendline = self.indicators.get('trendline', {})
        scores['trendline_slope'] = self._score_trendline_slope(trendline.get('slope', 0))
        scores['trendline_r2'] = self._score_trendline_r2(trendline.get('r_squared', 0))

        return scores

    def _score_volatility(self) -> Dict:
        """Score volatility indicators."""
        scores = {}

        # ATR percentage (higher = more volatile)
        atr = self.indicators.get('atr', {})
        atr_pct = atr.get('current_pct', 0)
        # For volatility, we score the level (not directional)
        # Very low volatility can mean squeeze (bullish for breakout)
        # Very high volatility can mean panic (bearish) or opportunity
        scores['atr_pct'] = self._score_atr_pct(atr_pct)

        # NATR
        adv = self.indicators.get('advanced', {})
        natr = adv.get('natr', {}).get('current', 0)
        scores['natr'] = self._score_atr_pct(natr * 100)  # Convert to pct

        # Bollinger Bandwidth
        bb = self.indicators.get('bollinger_bands', {})
        bb_bandwidth = bb.get('bandwidth', 0)
        price = self.indicators.get('current_price', 1)
        bb_pct = (bb_bandwidth / price * 100) if price > 0 else 0
        scores['bollinger_bandwidth'] = self._score_bb_bandwidth(bb_pct)

        # Bollinger Position
        bb_position = bb.get('position', 'within')
        scores['bollinger_position'] = self._score_bb_position(bb_position)

        # 30-day volatility
        stat = self.indicators.get('statistical', {})
        vol_std = stat.get('volatility_std_30d', 0)
        scores['volatility_std'] = self._score_volatility_std(vol_std)

        return scores

    def _score_volume(self) -> Dict:
        """Score volume indicators."""
        scores = {}

        # Volume ratio
        vol = self.indicators.get('volume', {})
        vol_ratio = vol.get('volume_ratio', 1.0)
        scores['volume_ratio'] = self._score_volume_ratio(vol_ratio)

        # Volume trend
        vol_trend = vol.get('trend', 'neutral')
        scores['volume_trend'] = self._score_volume_trend(vol_trend)

        # OBV
        adv = self.indicators.get('advanced', {})
        obv = adv.get('obv', {})
        obv_trend = obv.get('trend', 'neutral')
        scores['obv_trend'] = self._score_obv_trend(obv_trend)

        # A/D Line
        ad = adv.get('ad', {}).get('current', 0)
        scores['ad_line'] = self._score_ad_line(ad)

        # A/D Oscillator
        adosc = adv.get('adosc', 0)
        scores['adosc'] = self._normalize_to_score(adosc, -1000000, 1000000, clip=True)

        # Price-Volume Correlation
        stat = self.indicators.get('statistical', {})
        pv_corr = stat.get('price_volume_correlation', 0)
        scores['price_volume_correlation'] = self._score_pv_correlation(pv_corr)

        return scores

    def _score_obos(self) -> Dict:
        """Score overbought/oversold composite signals."""
        scores = {}

        # Stochastic %K (already in momentum, but also OB/OS)
        stoch = self.indicators.get('stochastic', {})
        k = stoch.get('k_value', 50)
        scores['stoch_obos'] = self._score_stochastic_obos(k)

        # Ultimate Oscillator
        ultosc = self.indicators.get('advanced', {}).get('ultosc', 50)
        scores['ultosc_obos'] = self._score_ultosc_obos(ultosc)

        # 52-week range position
        range_52w = self.indicators.get('52_week_range', {})
        pct_from_high = range_52w.get('current_pct_from_high', 0)
        pct_from_low = range_52w.get('current_pct_from_low', 0)
        scores['week52_range'] = self._score_52w_range(pct_from_high, pct_from_low)

        # Bollinger Band position (for OB/OS context)
        bb = self.indicators.get('bollinger_bands', {})
        position = bb.get('position', 'within')
        if position == 'above':
            scores['bb_position_obos'] = -0.7  # Overbought
        elif position == 'below':
            scores['bb_position_obos'] = 0.7   # Oversold
        else:
            scores['bb_position_obos'] = 0.0   # Neutral

        return scores

    # ===== Individual Signal Scoring Methods =====

    def _score_rsi(self, rsi: float) -> float:
        """Score RSI (0-100) to -1 to +1."""
        if rsi >= 70:
            # Overbought - bearish, but stronger signal as RSI increases
            return self._normalize_to_score(rsi, 70, 100, clip=True)
        elif rsi <= 30:
            # Oversold - bullish, stronger signal as RSI decreases
            return self._normalize_to_score(rsi, 0, 30, clip=True)
        else:
            # Neutral zone - slight bias toward 50
            return self._normalize_to_score(rsi, 30, 70, clip=True)

    def _score_macd_histogram(self, hist: float) -> float:
        """Score MACD histogram to -1 to +1."""
        return self._normalize_to_score(hist, -2, 2, clip=True)

    def _score_macd_trend(self, trend: str) -> float:
        """Score MACD trend classification."""
        trend_map = {
            'strong_bullish': 1.0,
            'bullish': 0.6,
            'neutral': 0.0,
            'bearish': -0.6,
            'strong_bearish': -1.0
        }
        return trend_map.get(trend, 0.0)

    def _score_stochastic(self, k: float) -> float:
        """Score Stochastic %K to -1 to +1."""
        if k >= 80:
            return self._normalize_to_score(k, 80, 100, clip=True)
        elif k <= 20:
            return self._normalize_to_score(k, 0, 20, clip=True)
        else:
            return self._normalize_to_score(k, 20, 80, clip=True)

    def _score_willr(self, willr: float) -> float:
        """Score Williams %R (-100 to 0) to -1 to +1."""
        # WillR is inverted: -20 = overbought, -80 = oversold
        if willr >= -20:
            return self._normalize_to_score(willr, -20, 0, clip=True)
        elif willr <= -80:
            return self._normalize_to_score(willr, -100, -80, clip=True)
        else:
            return self._normalize_to_score(willr, -80, -20, clip=True)

    def _score_cci(self, cci: float) -> float:
        """Score CCI to -1 to +1."""
        if cci >= 100:
            return self._normalize_to_score(cci, 100, 300, clip=True)
        elif cci <= -100:
            return self._normalize_to_score(cci, -300, -100, clip=True)
        else:
            return self._normalize_to_score(cci, -100, 100, clip=True)

    def _score_mfi(self, mfi: float) -> float:
        """Score Money Flow Index (0-100) to -1 to +1."""
        if mfi >= 80:
            return self._normalize_to_score(mfi, 80, 100, clip=True)
        elif mfi <= 20:
            return self._normalize_to_score(mfi, 0, 20, clip=True)
        else:
            return self._normalize_to_score(mfi, 20, 80, clip=True)

    def _score_rocr(self, rocr: float) -> float:
        """Score Rate of Change Ratio."""
        if rocr > 1.02:  # Up 2%+
            return min((rocr - 1.02) * 25, 1.0)
        elif rocr < 0.98:  # Down 2%+
            return max((rocr - 0.98) * 25, -1.0)
        else:
            return 0.0

    def _score_ultosc(self, ultosc: float) -> float:
        """Score Ultimate Oscillator (0-100)."""
        if ultosc >= 70:
            return self._normalize_to_score(ultosc, 70, 100, clip=True)
        elif ultosc <= 30:
            return self._normalize_to_score(ultosc, 0, 30, clip=True)
        else:
            return self._normalize_to_score(ultosc, 30, 70, clip=True)

    def _score_aroon_oscillator(self, osc: float) -> float:
        """Score Aroon Oscillator (-100 to 100)."""
        return self._normalize_to_score(osc, -100, 100, clip=True)

    def _score_di_difference(self, plus_di: float, minus_di: float) -> float:
        """Score the difference between +DI and -DI."""
        diff = plus_di - minus_di
        return self._normalize_to_score(diff, -30, 30, clip=True)

    def _score_price_vs_ma(self, period: int) -> float:
        """Score price vs moving average position."""
        ma_data = self.indicators.get('moving_averages', {})
        ma_key = f'ma_{period}'
        ma_val = ma_data.get(ma_key)

        if ma_val is None:
            return 0.0

        price = self.indicators.get('current_price', 0)
        if price <= 0:
            return 0.0

        pct_diff = (price - ma_val) / ma_val

        # Score based on distance from MA
        if pct_diff > 0.05:  # >5% above MA
            return min(1.0, pct_diff * 10)
        elif pct_diff < -0.05:  # >5% below MA
            return max(-1.0, pct_diff * 10)
        else:
            return self._normalize_to_score(pct_diff, -0.05, 0.05, clip=True)

    def _score_ma_cross(self, ma_short: float, ma_long: float) -> float:
        """Score MA crossover (golden/death cross)."""
        if ma_short is None or ma_long is None or ma_long == 0:
            return 0.0

        ratio = ma_short / ma_long
        if ratio > 1.02:
            return min(1.0, (ratio - 1.02) * 25)
        elif ratio < 0.98:
            return max(-1.0, (ratio - 0.98) * 25)
        else:
            return self._normalize_to_score(ratio, 0.98, 1.02, clip=True)

    def _score_ma_slope(self, slope: str) -> float:
        """Score MA slope classification."""
        slope_map = {
            'rising': 0.7,
            'flat': 0.0,
            'falling': -0.7
        }
        return slope_map.get(slope, 0.0)

    def _score_sar(self, price: float, sar: float) -> float:
        """Score Parabolic SAR position."""
        if sar is None or price <= 0:
            return 0.0

        # Price above SAR = bullish
        if price > sar:
            pct = (price - sar) / price
            return min(1.0, pct * 50)
        else:
            pct = (sar - price) / price
            return max(-1.0, -pct * 50)

    def _score_trendline_slope(self, slope: float) -> float:
        """Score trendline slope."""
        # Normalize slope to reasonable range
        return self._normalize_to_score(slope, -2, 2, clip=True)

    def _score_trendline_r2(self, r2: float) -> float:
        """Score trendline R² (trend reliability)."""
        # Higher R² is always positive for trend following
        # This is a confidence weight, not directional
        return self._normalize_to_score(r2, 0, 1, clip=True)

    def _score_atr_pct(self, atr_pct: float) -> float:
        """Score ATR percentage (volatility level)."""
        # For volatility: very low = squeeze (bullish), very high = panic (mixed)
        if atr_pct < 1.0:
            # Low volatility - potential squeeze
            return self._normalize_to_score(atr_pct, 0, 1.0, clip=True)
        elif atr_pct > 3.0:
            # High volatility - could be panic selling or breakout
            return -0.5  # Slightly bearish (uncertainty)
        else:
            return 0.0  # Normal volatility

    def _score_bb_bandwidth(self, bb_pct: float) -> float:
        """Score Bollinger Bandwidth."""
        if bb_pct < 2:
            # Very narrow - squeeze (bullish for breakout)
            return 0.8
        elif bb_pct > 8:
            # Very wide - high volatility
            return -0.3
        else:
            return 0.0

    def _score_bb_position(self, position: str) -> float:
        """Score Bollinger Band position."""
        if position == 'above':
            return 0.5  # Slightly overbought
        elif position == 'below':
            return -0.5  # Slightly oversold
        else:
            return 0.0

    def _score_volatility_std(self, vol_std: float) -> float:
        """Score 30-day volatility standard deviation."""
        if vol_std < 1.0:
            # Low volatility - squeeze
            return 0.6
        elif vol_std > 3.0:
            # High volatility - uncertainty
            return -0.4
        else:
            return 0.0

    def _score_volume_ratio(self, ratio: float) -> float:
        """Score volume ratio."""
        # High volume = conviction
        if ratio > 1.5:
            return min(1.0, (ratio - 1.5) * 2 + 0.3)
        elif ratio < 0.7:
            # Low volume = lack of interest
            return max(-0.5, (ratio - 0.7) * 2)
        else:
            return 0.0

    def _score_volume_trend(self, trend: str) -> float:
        """Score volume trend."""
        trend_map = {
            'increasing': 0.5,
            'neutral': 0.0,
            'decreasing': -0.3
        }
        return trend_map.get(trend, 0.0)

    def _score_obv_trend(self, trend: str) -> float:
        """Score OBV trend."""
        trend_map = {
            'increasing': 0.7,
            'decreasing': -0.7,
            'neutral': 0.0
        }
        return trend_map.get(trend, 0.0)

    def _score_ad_line(self, ad: float) -> float:
        """Score Accumulation/Distribution line."""
        # This is relative, so we normalize
        return self._normalize_to_score(ad, -50000000, 50000000, clip=True)

    def _score_pv_correlation(self, corr: float) -> float:
        """Score price-volume correlation."""
        # Positive correlation confirms price trend
        if corr > 0.3:
            return 0.5
        elif corr < -0.3:
            return -0.5
        else:
            return 0.0

    def _score_stochastic_obos(self, k: float) -> float:
        """Score Stochastic for OB/OS."""
        return self._score_stochastic(k)

    def _score_ultosc_obos(self, ultosc: float) -> float:
        """Score Ultimate Oscillator for OB/OS."""
        return self._score_ultosc(ultosc)

    def _score_52w_range(self, pct_from_high: float, pct_from_low: float) -> float:
        """Score 52-week range position."""
        # Near 52-week high = overbought (bearish)
        # Near 52-week low = oversold (bullish)
        if pct_from_high > -10:
            # Within 10% of high
            return -0.7
        elif pct_from_low < 10:
            # Within 10% of low
            return 0.7
        elif pct_from_high < -30:
            # More than 30% below high = room to run
            return 0.5
        else:
            return 0.0

    # ===== Utility Methods =====

    def _normalize_to_score(self, value: float, min_val: float, max_val: float, clip: bool = True) -> float:
        """
        Normalize a value to a -1 to +1 score.

        Args:
            value: The value to normalize
            min_val: Minimum value for normalization (maps to -1)
            max_val: Maximum value for normalization (maps to +1)
            clip: Whether to clip output to [-1, 1]

        Returns:
            Normalized score between -1 and +1
        """
        if value is None or np.isnan(value):
            return 0.0

        # Handle edge case where min == max
        if max_val == min_val:
            return 0.0

        # Normalize to -1 to +1 range
        midpoint = (min_val + max_val) / 2
        half_range = (max_val - min_val) / 2

        if half_range == 0:
            return 0.0

        score = (value - midpoint) / half_range

        if clip:
            score = max(-1.0, min(1.0, score))

        return float(score)

    def get_classification(self, score: float) -> str:
        """Convert numeric score to classification string."""
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

    def get_signal_emoji(self, score: float) -> str:
        """Get emoji for signal score."""
        if score >= 0.6:
            return "🟢"
        elif score >= 0.3:
            return "🟢"
        elif score >= -0.3:
            return "⚪"
        elif score >= -0.6:
            return "🔴"
        else:
            return "🔴"


if __name__ == '__main__':
    # Test the signal scorer
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

        scorer = SignalScorer(indicators)
        result = scorer.score_all()

        print("Category Scores:")
        for cat, score in result['category_scores'].items():
            print(f"  {cat}: {score:.2f} ({scorer.get_classification(score)})")
    else:
        print(f"Price file not found: {csv_path}")
