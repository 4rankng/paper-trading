#!/usr/bin/env python3
"""
Score Aggregator Module

Combines individual signal scores into category scores and overall
Technical Health Score. Applies regime-based weights and calculates
convergence/divergence metrics.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np


class ScoreAggregator:
    """Aggregate signal scores into unified metrics."""

    def __init__(
        self,
        category_scores: Dict[str, float],
        signal_scores: Dict[str, Dict[str, float]],
        regime: str,
        config: Optional[Dict] = None
    ):
        """
        Initialize with scores and regime.

        Args:
            category_scores: Dict of category name -> score
            signal_scores: Dict of category -> dict of signal -> score
            regime: Current market regime
            config: Configuration dict with regime weights
        """
        self.category_scores = category_scores
        self.signal_scores = signal_scores
        self.regime = regime
        self.config = config or self._default_config()
        self.overall_score = 0.0
        self.weighted_scores = {}
        self.convergence = 0.0
        self.confidence_level = "Low"

    def _default_config(self) -> Dict:
        """Return default regime weights."""
        return {
            'regimes': {
                'trending_up': {'momentum': 0.30, 'trend': 0.35, 'volatility': 0.10, 'volume': 0.15, 'ob_os': 0.10},
                'trending_down': {'momentum': 0.30, 'trend': 0.35, 'volatility': 0.15, 'volume': 0.10, 'ob_os': 0.10},
                'ranging': {'momentum': 0.20, 'trend': 0.10, 'volatility': 0.25, 'volume': 0.20, 'ob_os': 0.25},
                'volatile': {'momentum': 0.15, 'trend': 0.15, 'volatility': 0.30, 'volume': 0.25, 'ob_os': 0.15},
            }
        }

    def aggregate(self) -> Dict:
        """
        Perform aggregation of all scores.

        Returns:
            Dict with overall_score, weighted_scores, convergence, confidence
        """
        # Get regime weights
        regime_weights = self.config.get('regimes', {}).get(
            self.regime,
            self.config['regimes']['ranging']  # Default to ranging
        )

        # Calculate weighted category scores
        total_weight = 0.0
        weighted_sum = 0.0

        for category, score in self.category_scores.items():
            weight = regime_weights.get(category, 0.20)
            weighted_score = score * weight
            self.weighted_scores[category] = {
                'raw_score': score,
                'weight': weight,
                'weighted_score': weighted_score
            }
            weighted_sum += weighted_score
            total_weight += weight

        # Normalize by total weight (in case weights don't sum to 1)
        if total_weight > 0:
            self.overall_score = weighted_sum / total_weight
        else:
            self.overall_score = 0.0

        # Convert to 0-100 scale
        self.overall_score = ((self.overall_score + 1) / 2) * 100

        # Calculate convergence
        self.convergence = self._calculate_convergence()

        # Determine confidence level
        self.confidence_level = self._determine_confidence()

        return {
            'overall_score': round(self.overall_score, 1),
            'weighted_scores': self._format_weighted_scores(),
            'convergence': round(self.convergence * 100, 1),
            'confidence_level': self.confidence_level,
            'classification': self._classify_score()
        }

    def _calculate_convergence(self) -> float:
        """
        Calculate signal convergence (0-1, higher = more aligned).

        Convergence measures how many signals agree in direction.
        """
        all_signals = []
        for category, signals in self.signal_scores.items():
            for signal, score in signals.items():
                if score is not None and not np.isnan(score):
                    all_signals.append(score)

        if not all_signals:
            return 0.0

        # Count bullish (positive) and bearish (negative) signals
        bullish = sum(1 for s in all_signals if s > 0.2)
        bearish = sum(1 for s in all_signals if s < -0.2)
        neutral = sum(1 for s in all_signals if -0.2 <= s <= 0.2)

        total = len(all_signals)
        if total == 0:
            return 0.0

        # Convergence is the max of bullish or bearish proportion
        # (excluding neutrals)
        active = bullish + bearish
        if active == 0:
            return 0.0

        convergence = max(bullish, bearish) / active
        return convergence

    def _determine_confidence(self) -> str:
        """Determine confidence level based on convergence and category alignment."""
        # Count aligned categories
        aligned_categories = 0
        for category, data in self.weighted_scores.items():
            if abs(data['raw_score']) > 0.3:  # Meaningful signal
                aligned_categories += 1

        convergence = self.convergence
        total_categories = len(self.category_scores)

        # High confidence: High convergence + multiple categories aligned
        if convergence >= 0.65 and aligned_categories >= 3:
            return "High"
        elif convergence >= 0.45 and aligned_categories >= 2:
            return "Medium"
        else:
            return "Low"

    def _classify_score(self) -> str:
        """Classify overall score into category."""
        score = self.overall_score

        if score >= 75:
            return "Strongly Bullish"
        elif score >= 60:
            return "Moderately Bullish"
        elif score >= 45:
            return "Neutral"
        elif score >= 30:
            return "Moderately Bearish"
        else:
            return "Strongly Bearish"

    def _format_weighted_scores(self) -> Dict:
        """Format weighted scores for output."""
        formatted = {}
        for category, data in self.weighted_scores.items():
            # Convert raw score from -1,1 to 0-100 scale
            scaled_score = ((data['raw_score'] + 1) / 2) * 100
            formatted[category] = {
                'score': round(scaled_score, 1),
                'weight': round(data['weight'] * 100, 1),
                'classification': self._classify_category(scaled_score)
            }
        return formatted

    def _classify_category(self, score: float) -> str:
        """Classify category score."""
        if score >= 65:
            return "Bullish"
        elif score >= 55:
            return "Mildly Bullish"
        elif score >= 45:
            return "Neutral"
        elif score >= 35:
            return "Mildly Bearish"
        else:
            return "Bearish"

    def get_divergent_signals(self) -> List[Tuple[str, str, float]]:
        """
        Get signals that diverge from the overall trend.

        Returns:
            List of (category, signal_name, score) for divergent signals
        """
        divergent = []
        overall_bias = 1 if self.overall_score >= 50 else -1 if self.overall_score <= 50 else 0

        for category, signals in self.signal_scores.items():
            for signal, score in signals.items():
                if score is None or np.isnan(score):
                    continue

                # Signal diverges if it's strongly opposite to overall bias
                if overall_bias > 0 and score < -0.4:
                    divergent.append((category, signal, score))
                elif overall_bias < 0 and score > 0.4:
                    divergent.append((category, signal, score))

        # Sort by divergence strength
        divergent.sort(key=lambda x: abs(x[2]), reverse=True)
        return divergent[:10]  # Return top 10

    def get_key_signals(self, top_n: int = 5) -> List[Tuple[str, str, float, str]]:
        """
        Get the strongest signals (bullish or bearish).

        Returns:
            List of (category, signal_name, score, classification)
        """
        all_signals = []

        for category, signals in self.signal_scores.items():
            for signal, score in signals.items():
                if score is not None and not np.isnan(score):
                    classification = self._classify_score_single(score)
                    all_signals.append((category, signal, score, classification))

        # Sort by absolute strength
        all_signals.sort(key=lambda x: abs(x[2]), reverse=True)
        return all_signals[:top_n]

    def _classify_score_single(self, score: float) -> str:
        """Classify a single score."""
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


def aggregate_scores(
    category_scores: Dict[str, float],
    signal_scores: Dict[str, Dict[str, float]],
    regime: str,
    config: Optional[Dict] = None
) -> Dict:
    """
    Convenience function to aggregate scores.

    Args:
        category_scores: Dict of category name -> score
        signal_scores: Dict of category -> dict of signal -> score
        regime: Current market regime
        config: Optional configuration dict

    Returns:
        Dict with aggregated results
    """
    aggregator = ScoreAggregator(category_scores, signal_scores, regime, config)
    return aggregator.aggregate()


if __name__ == '__main__':
    # Test the aggregator
    test_category_scores = {
        'momentum': 0.6,
        'trend': 0.8,
        'volatility': -0.2,
        'volume': 0.4,
        'ob_os': 0.1
    }

    test_signal_scores = {
        'momentum': {
            'rsi': 0.5,
            'macd_histogram': 0.7,
            'stochastic_k': 0.6
        },
        'trend': {
            'adx': 0.8,
            'price_vs_ma20': 0.9,
            'ma_cross_short': 0.7
        },
        'volatility': {
            'atr_pct': -0.3,
            'bollinger_bandwidth': -0.1
        },
        'volume': {
            'volume_ratio': 0.5,
            'obv_trend': 0.3
        },
        'ob_os': {
            'stoch_obos': 0.1,
            'week52_range': 0.2
        }
    }

    aggregator = ScoreAggregator(
        test_category_scores,
        test_signal_scores,
        'trending_up'
    )

    result = aggregator.aggregate()

    print("Aggregation Results:")
    print(f"  Overall Score: {result['overall_score']}/100 - {result['classification']}")
    print(f"  Convergence: {result['convergence']}%")
    print(f"  Confidence: {result['confidence_level']}")
    print(f"\nCategory Scores:")
    for cat, data in result['weighted_scores'].items():
        print(f"  {cat}: {data['score']}/100 (weight: {data['weight']}%) - {data['classification']}")
