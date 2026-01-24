#!/usr/bin/env python3
"""Technical indicator calculations using TA-Lib library."""
import sys
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import numpy as np
    import pandas as pd
    import talib
    HAS_TALIB = True
except ImportError:
    HAS_TALIB = False


def get_project_root() -> Path:
    """Get project root directory using marker files."""
    p = Path(__file__).resolve()

    markers = ['prices/', '.git/', 'watchlist.json']

    for parent in [p, *p.parents]:
        if any((parent / m).exists() for m in markers):
            return parent

    if ".claude" in p.parts:
        idx = p.parts.index(".claude")
        return Path(*p.parts[:idx])

    raise RuntimeError("Project root not found")


class TechnicalIndicators:
    """Calculate technical indicators using TA-Lib."""

    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    STOCHASTIC_OVERBOUGHT = 80
    STOCHASTIC_OVERSOLD = 20

    def __init__(self, data: List[Dict]):
        if not HAS_TALIB:
            raise ImportError("TA-Lib required: pip install TA-Lib")
        self.data = data
        self.dates = [d['date'] for d in data]
        self.opens = np.array([d['open'] for d in data], dtype=np.float64)
        self.highs = np.array([d['high'] for d in data], dtype=np.float64)
        self.lows = np.array([d['low'] for d in data], dtype=np.float64)
        self.closes = np.array([d['close'] for d in data], dtype=np.float64)
        self.volumes = np.array([d['volume'] for d in data], dtype=np.float64)

    def sma(self, period: int) -> np.ndarray:
        return talib.SMA(self.closes, timeperiod=period)

    def ema(self, period: int) -> np.ndarray:
        return talib.EMA(self.closes, timeperiod=period)

    def rsi(self, period: int = 14) -> Tuple[np.ndarray, float]:
        rsi_values = talib.RSI(self.closes, timeperiod=period)
        current_rsi = float(rsi_values[-1]) if not np.isnan(rsi_values[-1]) else 50.0
        return rsi_values, current_rsi

    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        macd_line, signal_line, histogram = talib.MACD(self.closes, fastperiod=fast, slowperiod=slow, signalperiod=signal)
        current_macd = float(macd_line[-1]) if not np.isnan(macd_line[-1]) else 0.0
        current_signal = float(signal_line[-1]) if not np.isnan(signal_line[-1]) else 0.0
        current_hist = float(histogram[-1]) if not np.isnan(histogram[-1]) else 0.0
        if current_hist > 0:
            trend = 'strong_bullish' if current_macd > 0 and current_signal > 0 else 'bullish'
        elif current_hist < 0:
            trend = 'strong_bearish' if current_macd < 0 and current_signal < 0 else 'bearish'
        else:
            trend = 'neutral'
        return {'macd_line': round(current_macd, 4), 'signal_line': round(current_signal, 4),
                'histogram': round(current_hist, 4), 'macd_trend': trend}

    def bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> Dict:
        upper, middle, lower = talib.BBANDS(self.closes, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev)
        current_upper = float(upper[-1]) if not np.isnan(upper[-1]) else 0.0
        current_middle = float(middle[-1]) if not np.isnan(middle[-1]) else 0.0
        current_lower = float(lower[-1]) if not np.isnan(lower[-1]) else 0.0
        current_close = float(self.closes[-1])
        position = 'above' if current_close > current_upper else 'below' if current_close < current_lower else 'within'
        return {'upper_band': round(current_upper, 2), 'middle_band': round(current_middle, 2),
                'lower_band': round(current_lower, 2), 'bandwidth': round(current_upper - current_lower, 2),
                'position': position}

    def stochastic(self, k_period: int = 14, d_period: int = 3) -> Dict:
        slow_k, slow_d = talib.STOCH(self.highs, self.lows, self.closes,
                                      fastk_period=k_period, slowk_period=d_period, slowd_period=d_period)
        current_k = float(slow_k[-1]) if not np.isnan(slow_k[-1]) else 50.0
        current_d = float(slow_d[-1]) if not np.isnan(slow_d[-1]) else 50.0
        if current_k >= self.STOCHASTIC_OVERBOUGHT:
            signal = 'overbought'
        elif current_k <= self.STOCHASTIC_OVERSOLD:
            signal = 'oversold'
        else:
            signal = 'neutral'
        return {'k_value': round(current_k, 2), 'd_value': round(current_d, 2), 'signal': signal}

    def atr(self, period: int = 14) -> float:
        atr_values = talib.ATR(self.highs, self.lows, self.closes, timeperiod=period)
        return float(atr_values[-1]) if not np.isnan(atr_values[-1]) else 0.0

    def volume_analysis(self, period: int = 20) -> Dict:
        if len(self.volumes) < period:
            avg_vol = float(np.mean(self.volumes))
        else:
            avg_vol = float(np.mean(self.volumes[-period:]))
        current_vol = float(self.volumes[-1])
        ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
        if len(self.volumes) >= period * 2:
            recent_avg = np.mean(self.volumes[-period:])
            older_avg = np.mean(self.volumes[-period*2:-period])
            if recent_avg > older_avg * 1.1:
                trend = 'increasing'
            elif recent_avg < older_avg * 0.9:
                trend = 'decreasing'
            else:
                trend = 'neutral'
        else:
            trend = 'neutral'
        return {'avg_volume': float(avg_vol), 'current_volume': float(current_vol),
                'volume_ratio': round(ratio, 2), 'trend': trend}

    def support_resistance(self, lookback: int = 50) -> Dict:
        if len(self.lows) < lookback:
            lookback = len(self.lows)
        recent_lows = self.lows[-lookback:]
        recent_highs = self.highs[-lookback:]
        current_price = float(self.closes[-1])
        # Find local minima and maxima using NumPy
        low_min_indices = []
        high_max_indices = []
        for i in range(5, len(recent_lows) - 5):
            if recent_lows[i] == min(recent_lows[i-5:i+6]):
                low_min_indices.append(i)
            if recent_highs[i] == max(recent_highs[i-5:i+6]):
                high_max_indices.append(i)
        support_levels = sorted([float(recent_lows[i]) for i in low_min_indices])
        resistance_levels = sorted([float(recent_highs[i]) for i in high_max_indices], reverse=True)
        if not support_levels or current_price < min(support_levels):
            support_levels.append(float(np.min(recent_lows)))
        if not resistance_levels or current_price > max(resistance_levels):
            resistance_levels.append(float(np.max(recent_highs)))
        support_levels = sorted(set(support_levels))[:3]
        resistance_levels = sorted(set(resistance_levels), reverse=True)[:3]
        supports_below = [s for s in support_levels if s < current_price]
        nearest_support = max(supports_below) if supports_below else min(support_levels)
        resistances_above = [r for r in resistance_levels if r > current_price]
        nearest_resistance = min(resistances_above) if resistances_above else min(resistance_levels)
        return {'support_levels': [round(s, 2) for s in support_levels],
                'resistance_levels': [round(r, 2) for r in resistance_levels],
                'nearest_support': round(nearest_support, 2),
                'nearest_resistance': round(nearest_resistance, 2)}

    def trend_analysis(self, short_ma: int = 20, long_ma: int = 50) -> Dict:
        current_price = float(self.closes[-1])
        short_mas = self.sma(short_ma)
        long_mas = self.sma(long_ma)
        short_ma_val = float(short_mas[-1]) if not np.isnan(short_mas[-1]) else current_price
        long_ma_val = float(long_mas[-1]) if not np.isnan(long_mas[-1]) else current_price
        # Calculate slopes
        slope_lookback = min(5, len(short_mas))
        short_ma_slope = long_ma_slope = 0
        if slope_lookback >= 2 and not np.isnan(short_mas[-slope_lookback]):
            short_ma_slope = (short_mas[-1] - short_mas[-slope_lookback]) / short_mas[-slope_lookback] * 100
            long_ma_slope = (long_mas[-1] - long_mas[-slope_lookback]) / long_mas[-slope_lookback] * 100
        def classify_slope(slope_pct):
            return 'rising' if slope_pct > 0.5 else 'falling' if slope_pct < -0.5 else 'flat'
        short_ma_slope_label = classify_slope(short_ma_slope)
        long_ma_slope_label = classify_slope(long_ma_slope)
        price_vs_short = 'above' if current_price > short_ma_val else 'below'
        price_vs_long = 'above' if current_price > long_ma_val else 'below'
        ma_crossover = 'bullish' if short_ma_val > long_ma_val else 'bearish'
        if price_vs_short == 'above' and price_vs_long == 'above' and ma_crossover == 'bullish' and short_ma_slope_label == 'rising':
            trend, strength = 'uptrend', 'strong'
        elif price_vs_short == 'above' and price_vs_long == 'above' and ma_crossover == 'bullish':
            trend, strength = 'uptrend', 'moderate'
        elif price_vs_short == 'below' and price_vs_long == 'below' and ma_crossover == 'bearish' and short_ma_slope_label == 'falling':
            trend, strength = 'downtrend', 'strong'
        elif price_vs_short == 'below' and price_vs_long == 'below' and ma_crossover == 'bearish':
            trend, strength = 'downtrend', 'moderate'
        elif price_vs_short == 'above' and short_ma_slope_label == 'falling':
            trend, strength = 'sideways', 'weak'
        else:
            trend, strength = 'sideways', 'weak'
        dist_short = ((current_price - short_ma_val) / short_ma_val) * 100 if short_ma_val > 0 else 0
        dist_long = ((current_price - long_ma_val) / long_ma_val) * 100 if long_ma_val > 0 else 0
        return {'trend': trend, 'strength': strength, 'price_vs_short_ma': price_vs_short, 'price_vs_long_ma': price_vs_long,
                'short_ma_vs_long_ma': ma_crossover, 'short_ma_slope': short_ma_slope_label, 'long_ma_slope': long_ma_slope_label,
                'distance_to_short_ma_pct': round(dist_short, 2), 'distance_to_long_ma_pct': round(dist_long, 2)}

    def fibonacci_retracements(self, lookback: int = 100) -> Dict:
        """Calculate Fibonacci retracement levels based on recent price action."""
        if len(self.closes) < lookback:
            lookback = len(self.closes)
        recent_highs = self.closes[-lookback:]
        recent_lows = self.closes[-lookback:]
        swing_high = float(np.max(recent_highs))
        swing_low = float(np.min(recent_lows))
        diff = swing_high - swing_low
        current_price = float(self.closes[-1])
        # Standard Fibonacci retracement levels
        fib_levels = {
            '0% (swing_high)': swing_high,
            '23.6%': swing_high - (0.236 * diff),
            '38.2%': swing_high - (0.382 * diff),
            '50%': swing_high - (0.5 * diff),
            '61.8%': swing_high - (0.618 * diff),
            '78.6%': swing_high - (0.786 * diff),
            '100% (swing_low)': swing_low
        }
        # Determine which Fib level price is near
        nearest_level = 'Unknown'
        min_distance = float('inf')
        for level_name, level_price in fib_levels.items():
            distance = abs(current_price - level_price)
            if distance < min_distance:
                min_distance = distance
                nearest_level = level_name
        return {
            'swing_high': round(swing_high, 2),
            'swing_low': round(swing_low, 2),
            'levels': {k: round(v, 2) for k, v in fib_levels.items()},
            'nearest_level': nearest_level,
            'nearest_level_price': round(fib_levels[nearest_level], 2) if nearest_level != 'Unknown' else current_price
        }

    def pivot_points(self) -> Dict:
        """Calculate classic and Fibonacci pivot points."""
        high = float(self.highs[-1])
        low = float(self.lows[-1])
        close = float(self.closes[-1])
        # Classic pivot points
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        s1 = (2 * pivot) - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        r3 = high + 2 * (pivot - low)
        s3 = low - 2 * (high - pivot)
        # Fibonacci pivot points
        fib_r1 = pivot + (high - low) * 0.382
        fib_r2 = pivot + (high - low) * 0.618
        fib_r3 = pivot + (high - low) * 1.0
        fib_s1 = pivot - (high - low) * 0.382
        fib_s2 = pivot - (high - low) * 0.618
        fib_s3 = pivot - (high - low) * 1.0
        return {
            'classic': {
                'pivot': round(pivot, 2),
                'resistance': {'r1': round(r1, 2), 'r2': round(r2, 2), 'r3': round(r3, 2)},
                'support': {'s1': round(s1, 2), 's2': round(s2, 2), 's3': round(s3, 2)}
            },
            'fibonacci': {
                'pivot': round(pivot, 2),
                'resistance': {'r1': round(fib_r1, 2), 'r2': round(fib_r2, 2), 'r3': round(fib_r3, 2)},
                'support': {'s1': round(fib_s1, 2), 's2': round(fib_s2, 2), 's3': round(fib_s3, 2)}
            }
        }

    def linear_regression_trendline(self, period: int = 50) -> Dict:
        """Calculate linear regression trendline and statistics."""
        if len(self.closes) < period:
            period = len(self.closes)
        y = self.closes[-period:]
        x = np.arange(len(y))
        # Linear regression using TA-Lib
        slope = talib.LINEARREG_SLOPE(y, timeperiod=period)
        intercept = talib.LINEARREG_INTERCEPT(y, timeperiod=period)
        angle = talib.LINEARREG_ANGLE(y, timeperiod=period)
        # Calculate R-squared manually
        y_pred = intercept + slope * x
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        current_slope = float(slope[-1]) if not np.isnan(slope[-1]) else 0.0
        current_intercept = float(intercept[-1]) if not np.isnan(intercept[-1]) else 0.0
        current_angle = float(angle[-1]) if not np.isnan(angle[-1]) else 0.0
        # Trendline value at current point
        trendline_value = current_intercept + (current_slope * (period - 1))
        current_price = float(self.closes[-1])
        deviation_pct = ((current_price - trendline_value) / trendline_value) * 100 if trendline_value > 0 else 0
        return {
            'period': period,
            'slope': round(current_slope, 4),
            'intercept': round(current_intercept, 2),
            'angle': round(current_angle, 2),
            'r_squared': round(float(r_squared), 4),
            'trendline_value': round(trendline_value, 2),
            'price_vs_trendline_pct': round(deviation_pct, 2),
            'trend_direction': 'bullish' if current_slope > 0 else 'bearish' if current_slope < 0 else 'flat'
        }

    def enhanced_support_resistance(self, lookback: int = 100) -> Dict:
        """Calculate enhanced support/resistance using multiple methods."""
        if len(self.closes) < lookback:
            lookback = len(self.closes)
        current_price = float(self.closes[-1])
        recent_data = {
            'highs': self.highs[-lookback:],
            'lows': self.lows[-lookback:],
            'closes': self.closes[-lookback:]
        }
        # Method 1: Pivot highs/lows (already calculated)
        pivot_supports = []
        pivot_resistances = []
        for i in range(5, len(recent_data['highs']) - 5):
            if recent_data['highs'][i] == max(recent_data['highs'][i-5:i+6]):
                pivot_resistances.append(float(recent_data['highs'][i]))
            if recent_data['lows'][i] == min(recent_data['lows'][i-5:i+6]):
                pivot_supports.append(float(recent_data['lows'][i]))
        # Method 2: Volume-weighted price levels (high volume nodes)
        vol_profile = {}
        for i in range(len(recent_data['closes'])):
            price_level = round(recent_data['closes'][i], 2)
            if price_level not in vol_profile:
                vol_profile[price_level] = 0
            vol_profile[price_level] += self.volumes[-lookback:][i]
        # Get top 5 volume levels
        sorted_vol_levels = sorted(vol_profile.items(), key=lambda x: x[1], reverse=True)[:5]
        volume_nodes = [round(level, 2) for level, vol in sorted_vol_levels]
        # Method 3: Round numbers (psychological levels)
        price_range = max(recent_data['highs']) - min(recent_data['lows'])
        round_interval = round(price_range / 10, 2)
        base_round = round(min(recent_data['lows']) / round_interval) * round_interval
        round_levels = []
        for i in range(11):
            round_levels.append(round(base_round + (i * round_interval), 2))
        # Combine all methods
        all_supports = sorted(set([s for s in pivot_supports + volume_nodes + round_levels if s < current_price]))
        all_resistances = sorted(set([r for r in pivot_resistances + volume_nodes + round_levels if r > current_price]), reverse=True)
        # Get nearest 3 levels
        nearest_supports = all_supports[-3:] if len(all_supports) >= 3 else all_supports
        nearest_resistances = all_resistances[:3] if len(all_resistances) >= 3 else all_resistances
        return {
            'support_levels': [round(s, 2) for s in nearest_supports],
            'resistance_levels': [round(r, 2) for r in nearest_resistances],
            'volume_profile_nodes': volume_nodes,
            'psychological_levels': round_levels,
            'pivot_supports': [round(s, 2) for s in pivot_supports[-5:]],
            'pivot_resistances': [round(r, 2) for r in pivot_resistances[:5]]
        }

    def statistical_indicators(self) -> Dict:
        """Calculate statistical indicators using TA-Lib."""
        indicators = {}
        # Beta (requires benchmark - using SPY approximation with its own data)
        # For simplicity, we'll calculate beta against a moving average
        benchmark = self.sma(50)
        if len(benchmark) >= 50 and not np.isnan(benchmark[-1]):
            # Simplified beta calculation
            returns = np.diff(self.closes[-50:]) / self.closes[-50:-1]
            benchmark_returns = np.diff(benchmark[-50:]) / benchmark[-50:-1]
            covariance = np.cov(returns, benchmark_returns)[0][1]
            benchmark_variance = np.var(benchmark_returns)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
            indicators['beta'] = round(float(beta), 2)
        # Correlation (price vs volume)
        if len(self.closes) >= 50:
            price_norm = (self.closes[-50:] - np.mean(self.closes[-50:])) / np.std(self.closes[-50:])
            vol_norm = (self.volumes[-50:] - np.mean(self.volumes[-50:])) / np.std(self.volumes[-50:])
            correlation = np.corrcoef(price_norm, vol_norm)[0][1]
            indicators['price_volume_correlation'] = round(float(correlation), 4) if not np.isnan(correlation) else 0.0
        # Standard deviation (volatility measure)
        returns = np.diff(self.closes[-30:]) / self.closes[-30:-1] if len(self.closes) >= 30 else []
        if len(returns) > 0:
            indicators['volatility_std_30d'] = round(float(np.std(returns)) * 100, 2)
        return indicators

    def cycle_indicators(self) -> Dict:
        """Calculate cycle indicators using TA-Lib Hilbert Transform."""
        indicators = {}
        # HT_DCPERIOD - Hilbert Transform - Dominant Cycle Period
        ht_dcperiod = talib.HT_DCPERIOD(self.closes)
        if not np.isnan(ht_dcperiod[-1]):
            indicators['dc_period'] = round(float(ht_dcperiod[-1]), 2)
        # HT_DCPHASE - Hilbert Transform - Dominant Cycle Phase
        ht_dcphase = talib.HT_DCPHASE(self.closes)
        if not np.isnan(ht_dcphase[-1]):
            indicators['dc_phase'] = round(float(ht_dcphase[-1]), 2)
        # HT_PHASOR - Hilbert Transform - Phasor Components
        ht_phasor_inphase, ht_phasor_quadrature = talib.HT_PHASOR(self.closes)
        if not np.isnan(ht_phasor_inphase[-1]) and not np.isnan(ht_phasor_quadrature[-1]):
            indicators['phasor'] = {
                'inphase': round(float(ht_phasor_inphase[-1]), 2),
                'quadrature': round(float(ht_phasor_quadrature[-1]), 2)
            }
        # HT_SINE - Hilbert Transform - SineWave
        ht_sine, ht_leadsine = talib.HT_SINE(self.closes)
        if not np.isnan(ht_sine[-1]) and not np.isnan(ht_leadsine[-1]):
            indicators['sineWave'] = {
                'sine': round(float(ht_sine[-1]), 2),
                'leadsine': round(float(ht_leadsine[-1]), 2)
            }
        # HT_TRENDMODE - Hilbert Transform - Trend vs Cycle Mode
        ht_trendmode = talib.HT_TRENDMODE(self.closes)
        current_mode = int(ht_trendmode[-1]) if not np.isnan(ht_trendmode[-1]) else 0
        indicators['trend_mode'] = 'trending' if current_mode == 1 else 'cyclical'
        return indicators

    def advanced_indicators(self) -> Dict:
        """Calculate advanced TA-Lib indicators."""
        indicators = {}
        # ADX - Average Directional Index
        adx = talib.ADX(self.highs, self.lows, self.closes, timeperiod=14)
        indicators['adx'] = {'current': round(float(adx[-1]), 2) if not np.isnan(adx[-1]) else 0.0,
                             'signal': 'strong_trend' if adx[-1] > 25 else 'weak_trend' if adx[-1] < 20 else 'trend_developing'}
        # AROON
        aroon_down, aroon_up = talib.AROON(self.highs, self.lows, timeperiod=14)
        indicators['aroon'] = {'up': round(float(aroon_up[-1]), 2), 'down': round(float(aroon_down[-1]), 2),
                               'oscillator': round(float(aroon_up[-1] - aroon_down[-1]), 2)}
        # CCI - Commodity Channel Index
        cci = talib.CCI(self.highs, self.lows, self.closes, timeperiod=14)
        current_cci = float(cci[-1]) if not np.isnan(cci[-1]) else 0.0
        indicators['cci'] = {'current': round(current_cci, 2),
                            'signal': 'overbought' if current_cci > 100 else 'oversold' if current_cci < -100 else 'neutral'}
        # MFI - Money Flow Index
        mfi = talib.MFI(self.highs, self.lows, self.closes, self.volumes, timeperiod=14)
        current_mfi = float(mfi[-1]) if not np.isnan(mfi[-1]) else 50.0
        indicators['mfi'] = {'current': round(current_mfi, 2),
                            'signal': 'overbought' if current_mfi > 80 else 'oversold' if current_mfi < 20 else 'neutral'}
        # WILLR - Williams %R
        willr = talib.WILLR(self.highs, self.lows, self.closes, timeperiod=14)
        current_willr = float(willr[-1]) if not np.isnan(willr[-1]) else -50.0
        indicators['willr'] = {'current': round(current_willr, 2),
                               'signal': 'overbought' if current_willr > -20 else 'oversold' if current_willr < -80 else 'neutral'}
        # OBV - On Balance Volume
        obv = talib.OBV(self.closes, self.volumes)
        obv_values = obv[-20:] if len(obv) >= 20 else obv
        obv_trend = 'increasing' if obv_values[-1] > obv_values[0] else 'decreasing'
        indicators['obv'] = {'current': round(float(obv[-1]), 0), 'trend': obv_trend}
        # AD - Accumulation/Distribution
        ad = talib.AD(self.highs, self.lows, self.closes, self.volumes)
        indicators['ad'] = {'current': round(float(ad[-1]), 0)}
        # NATR - Normalized ATR
        natr = talib.NATR(self.highs, self.lows, self.closes, timeperiod=14)
        indicators['natr'] = {'current': round(float(natr[-1]), 4) if not np.isnan(natr[-1]) else 0.0}
        # APO - Absolute Price Oscillator
        apo = talib.APO(self.closes, fastperiod=12, slowperiod=26, matype=0)
        indicators['apo'] = round(float(apo[-1]), 4) if not np.isnan(apo[-1]) else 0.0
        # AROONOSC - Aroon Oscillator
        aroonosc = talib.AROONOSC(self.highs, self.lows, timeperiod=14)
        indicators['aroonosc'] = round(float(aroonosc[-1]), 2) if not np.isnan(aroonosc[-1]) else 0.0
        # DX - Directional Movement Index
        dx = talib.DX(self.highs, self.lows, self.closes, timeperiod=14)
        indicators['dx'] = round(float(dx[-1]), 2) if not np.isnan(dx[-1]) else 0.0
        # MINUS_DI/DX - Minus Directional Indicator
        minus_di = talib.MINUS_DI(self.highs, self.lows, self.closes, timeperiod=14)
        indicators['minus_di'] = round(float(minus_di[-1]), 2) if not np.isnan(minus_di[-1]) else 0.0
        # PLUS_DI - Plus Directional Indicator
        plus_di = talib.PLUS_DI(self.highs, self.lows, self.closes, timeperiod=14)
        indicators['plus_di'] = round(float(plus_di[-1]), 2) if not np.isnan(plus_di[-1]) else 0.0
        # MINUS_DM - Minus Directional Movement
        minus_dm = talib.MINUS_DM(self.highs, self.lows, timeperiod=14)
        indicators['minus_dm'] = round(float(minus_dm[-1]), 4) if not np.isnan(minus_dm[-1]) else 0.0
        # PLUS_DM - Plus Directional Movement
        plus_dm = talib.PLUS_DM(self.highs, self.lows, timeperiod=14)
        indicators['plus_dm'] = round(float(plus_dm[-1]), 4) if not np.isnan(plus_dm[-1]) else 0.0
        # MOM - Momentum
        mom = talib.MOM(self.closes, timeperiod=10)
        indicators['momentum'] = round(float(mom[-1]), 4) if not np.isnan(mom[-1]) else 0.0
        # PPO - Percentage Price Oscillator
        ppo = talib.PPO(self.closes, fastperiod=12, slowperiod=26, matype=0)
        indicators['ppo'] = round(float(ppo[-1]), 4) if not np.isnan(ppo[-1]) else 0.0
        # ROC - Rate of Change
        roc = talib.ROC(self.closes, timeperiod=10)
        indicators['roc'] = round(float(roc[-1]), 2) if not np.isnan(roc[-1]) else 0.0
        # ROCR - Rate of Change Ratio
        rocr = talib.ROCR(self.closes, timeperiod=10)
        indicators['rocr'] = round(float(rocr[-1]), 4) if not np.isnan(rocr[-1]) else 0.0
        # TRIX - 1-day Rate of Change of a Triple Smooth EMA
        trix = talib.TRIX(self.closes, timeperiod=30)
        indicators['trix'] = round(float(trix[-1]), 4) if not np.isnan(trix[-1]) else 0.0
        # ULTOSC - Ultimate Oscillator
        ultosc = talib.ULTOSC(self.highs, self.lows, self.closes, timeperiod1=7, timeperiod2=14, timeperiod3=28)
        indicators['ultosc'] = round(float(ultosc[-1]), 2) if not np.isnan(ultosc[-1]) else 50.0
        # Additional Volume: ADOSC - Chaikin A/D Oscillator
        adosc = talib.ADOSC(self.highs, self.lows, self.closes, self.volumes, fastperiod=3, slowperiod=10)
        indicators['adosc'] = round(float(adosc[-1]), 0) if not np.isnan(adosc[-1]) else 0.0
        # Price Transform Indicators
        # AVGPRICE - Average Price
        avgprice = talib.AVGPRICE(self.opens, self.highs, self.lows, self.closes)
        indicators['avg_price'] = round(float(avgprice[-1]), 2)
        # MEDPRICE - Median Price
        medprice = talib.MEDPRICE(self.highs, self.lows)
        indicators['med_price'] = round(float(medprice[-1]), 2)
        # TYPPRICE - Typical Price
        typprice = talib.TYPPRICE(self.highs, self.lows, self.closes)
        indicators['typ_price'] = round(float(typprice[-1]), 2)
        # WCLPRICE - Weighted Close Price
        wclprice = talib.WCLPRICE(self.highs, self.lows, self.closes)
        indicators['wcl_price'] = round(float(wclprice[-1]), 2)
        return indicators

    def calculate_all(self, ma_periods: List[int] = None) -> Dict:
        if ma_periods is None:
            ma_periods = [10, 20, 50, 100, 200]
        indicators = {
            'current_price': float(self.closes[-1]),
            'data_points': len(self.closes),
            'period_start': self.dates[0] if self.dates else '',
            'period_end': self.dates[-1] if self.dates else '',
            'price_range': {
                'high': float(np.max(self.highs)),
                'low': float(np.min(self.lows)),
                'change': float(self.closes[-1] - self.closes[0]),
                'change_pct': round(((self.closes[-1] - self.closes[0]) / self.closes[0]) * 100, 2)
            }
        }
        # Moving Averages
        indicators['moving_averages'] = {}
        for period in ma_periods:
            if len(self.closes) >= period:
                ma_values = self.sma(period)
                if not np.isnan(ma_values[-1]):
                    indicators['moving_averages'][f'ma_{period}'] = round(float(ma_values[-1]), 2)
        ema_20 = self.ema(20)
        if not np.isnan(ema_20[-1]):
            indicators['ema_20'] = round(float(ema_20[-1]), 2)
        # Additional Overlap Studies
        # DEMA - Double Exponential Moving Average
        dema_20 = talib.DEMA(self.closes, timeperiod=20)
        if not np.isnan(dema_20[-1]):
            indicators['dema_20'] = round(float(dema_20[-1]), 2)
        # TEMA - Triple Exponential Moving Average
        tema_20 = talib.TEMA(self.closes, timeperiod=20)
        if not np.isnan(tema_20[-1]):
            indicators['tema_20'] = round(float(tema_20[-1]), 2)
        # T3 - Triple Exponential Moving Average (T3)
        t3_20 = talib.T3(self.closes, timeperiod=20, vfactor=0.7)
        if not np.isnan(t3_20[-1]):
            indicators['t3_20'] = round(float(t3_20[-1]), 2)
        # WMA - Weighted Moving Average
        wma_20 = talib.WMA(self.closes, timeperiod=20)
        if not np.isnan(wma_20[-1]):
            indicators['wma_20'] = round(float(wma_20[-1]), 2)
        # KAMA - Kaufman Adaptive Moving Average
        kama = talib.KAMA(self.closes, timeperiod=30)
        if not np.isnan(kama[-1]):
            indicators['kama_30'] = round(float(kama[-1]), 2)
        # MAMA - MESA Adaptive Moving Average
        mama, fama = talib.MAMA(self.closes, fastlimit=0.5, slowlimit=0.05)
        if not np.isnan(mama[-1]):
            indicators['mama'] = round(float(mama[-1]), 2)
        if not np.isnan(fama[-1]):
            indicators['fama'] = round(float(fama[-1]), 2)
        # SAR - Parabolic SAR
        sar = talib.SAR(self.highs, self.lows, acceleration=0.02, maximum=0.2)
        indicators['sar'] = round(float(sar[-1]), 2)
        # Standard Indicators
        rsi_values, current_rsi = self.rsi()
        indicators['rsi'] = {'current': round(current_rsi, 2), 'period': 14,
                            'signal': 'overbought' if current_rsi >= self.RSI_OVERBOUGHT else 'oversold' if current_rsi <= self.RSI_OVERSOLD else 'neutral'}
        indicators['macd'] = self.macd()
        indicators['bollinger_bands'] = self.bollinger_bands()
        indicators['stochastic'] = self.stochastic()
        atr_value = self.atr()
        indicators['atr'] = {'current': round(atr_value, 4),
                            'current_pct': round((atr_value / indicators['current_price']) * 100, 2) if indicators['current_price'] > 0 else 0, 'period': 14}
        indicators['volume'] = self.volume_analysis()
        indicators['support_resistance'] = self.support_resistance()
        indicators['trend'] = self.trend_analysis()
        # Advanced Indicators
        indicators['advanced'] = self.advanced_indicators()
        # New: Fibonacci Retracements
        indicators['fibonacci'] = self.fibonacci_retracements()
        # New: Pivot Points
        indicators['pivot_points'] = self.pivot_points()
        # New: Linear Regression Trendline
        indicators['trendline'] = self.linear_regression_trendline()
        # New: Enhanced Support/Resistance (replaces basic version if enough data)
        if len(self.closes) >= 100:
            indicators['enhanced_support_resistance'] = self.enhanced_support_resistance()
        # New: Statistical Indicators
        indicators['statistical'] = self.statistical_indicators()
        # New: Cycle Indicators
        try:
            indicators['cycle'] = self.cycle_indicators()
        except Exception:
            indicators['cycle'] = {}
        if len(self.closes) >= 252:
            indicators['52_week_range'] = {'high': round(float(np.max(self.closes[-252:])), 2),
                                           'low': round(float(np.min(self.closes[-252:])), 2),
                                           'current_pct_from_high': round(((self.closes[-1] - np.max(self.closes[-252:])) / np.max(self.closes[-252:])) * 100, 2),
                                           'current_pct_from_low': round(((self.closes[-1] - np.min(self.closes[-252:])) / np.min(self.closes[-252:])) * 100, 2)}
        return indicators
