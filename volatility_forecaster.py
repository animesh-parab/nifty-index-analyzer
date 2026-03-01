"""
volatility_forecaster.py
Advanced Volatility Forecasting for Options Trading

Predicts future volatility using multiple methods:
1. Historical Volatility (HV) - Rolling window calculations
2. GARCH Model - Autoregressive conditional heteroskedasticity
3. Parkinson Volatility - High-Low range based
4. Garman-Klass Volatility - OHLC based estimator
5. VIX-based forecasting - India VIX trends
6. ATR-based volatility - Normalized ATR predictions

Provides volatility forecasts for multiple timeframes: 5min, 15min, 30min, 1day
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")


class VolatilityForecaster:
    """
    Multi-method volatility forecasting engine.
    
    Features:
    - Historical volatility calculation
    - GARCH(1,1) model forecasting
    - High-Low range volatility (Parkinson)
    - OHLC volatility (Garman-Klass)
    - VIX trend analysis
    - ATR-based predictions
    - Volatility regime detection
    """
    
    def __init__(self):
        self.volatility_regimes = {
            'very_low': (0, 0.5),
            'low': (0.5, 1.0),
            'normal': (1.0, 1.5),
            'elevated': (1.5, 2.5),
            'high': (2.5, 4.0),
            'extreme': (4.0, float('inf'))
        }
    
    def calculate_historical_volatility(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """
        Calculate historical volatility using log returns.
        
        Args:
            df: DataFrame with 'close' prices
            window: Rolling window period
        
        Returns:
            Series of annualized volatility percentages
        """
        try:
            # Calculate log returns
            log_returns = np.log(df['close'] / df['close'].shift(1))
            
            # Calculate rolling standard deviation
            rolling_std = log_returns.rolling(window=window).std()
            
            # Annualize (assuming 252 trading days, 375 minutes per day for intraday)
            # For intraday: sqrt(375) ≈ 19.36
            # For daily: sqrt(252) ≈ 15.87
            annualization_factor = np.sqrt(252)
            
            # Convert to percentage
            volatility = rolling_std * annualization_factor * 100
            
            return volatility
            
        except Exception as e:
            logger.error(f"Error calculating historical volatility: {e}")
            return pd.Series(dtype=float)
    
    def calculate_parkinson_volatility(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """
        Parkinson volatility - uses high-low range.
        More efficient than close-to-close volatility.
        
        Formula: sqrt(1/(4*ln(2)) * sum((ln(H/L))^2) / n)
        """
        try:
            # Calculate log of high/low ratio
            hl_ratio = np.log(df['high'] / df['low'])
            
            # Square it
            hl_squared = hl_ratio ** 2
            
            # Rolling sum
            rolling_sum = hl_squared.rolling(window=window).sum()
            
            # Parkinson formula
            parkinson = np.sqrt(rolling_sum / (4 * window * np.log(2)))
            
            # Annualize and convert to percentage
            annualization_factor = np.sqrt(252)
            volatility = parkinson * annualization_factor * 100
            
            return volatility
            
        except Exception as e:
            logger.error(f"Error calculating Parkinson volatility: {e}")
            return pd.Series(dtype=float)
    
    def calculate_garman_klass_volatility(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """
        Garman-Klass volatility - uses OHLC data.
        Most efficient unbiased estimator.
        
        Formula: sqrt(0.5*(ln(H/L))^2 - (2*ln(2)-1)*(ln(C/O))^2)
        """
        try:
            # High-Low component
            hl = np.log(df['high'] / df['low']) ** 2
            
            # Close-Open component
            co = np.log(df['close'] / df['open']) ** 2
            
            # Garman-Klass formula
            gk = 0.5 * hl - (2 * np.log(2) - 1) * co
            
            # Rolling average
            rolling_gk = gk.rolling(window=window).mean()
            
            # Square root and annualize
            annualization_factor = np.sqrt(252)
            volatility = np.sqrt(rolling_gk) * annualization_factor * 100
            
            return volatility
            
        except Exception as e:
            logger.error(f"Error calculating Garman-Klass volatility: {e}")
            return pd.Series(dtype=float)
    
    def calculate_atr_volatility(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        ATR-based volatility measure.
        Normalized by price to get percentage volatility.
        """
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            prev_close = close.shift(1)
            
            # True Range
            tr = pd.concat([
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs()
            ], axis=1).max(axis=1)
            
            # ATR
            atr = tr.ewm(span=period, adjust=False).mean()
            
            # Normalize by price (percentage)
            atr_pct = (atr / close) * 100
            
            # Annualize
            annualization_factor = np.sqrt(252)
            volatility = atr_pct * annualization_factor
            
            return volatility
            
        except Exception as e:
            logger.error(f"Error calculating ATR volatility: {e}")
            return pd.Series(dtype=float)
    
    def simple_garch_forecast(self, returns: pd.Series, horizon: int = 1) -> float:
        """
        Simplified GARCH(1,1) volatility forecast.
        
        GARCH(1,1): σ²(t+1) = ω + α*ε²(t) + β*σ²(t)
        
        Using typical parameters:
        ω = 0.000001 (long-term variance)
        α = 0.1 (reaction to recent shocks)
        β = 0.85 (persistence)
        """
        try:
            # Remove NaN values
            returns = returns.dropna()
            
            if len(returns) < 10:
                return None
            
            # GARCH parameters (typical values)
            omega = 0.000001
            alpha = 0.1
            beta = 0.85
            
            # Calculate current variance
            current_variance = returns.iloc[-20:].var()
            
            # Last return squared (shock)
            last_shock = returns.iloc[-1] ** 2
            
            # GARCH forecast
            forecast_variance = omega + alpha * last_shock + beta * current_variance
            
            # Multi-step forecast (variance increases with horizon)
            for _ in range(horizon - 1):
                forecast_variance = omega + (alpha + beta) * forecast_variance
            
            # Convert to annualized volatility percentage
            forecast_vol = np.sqrt(forecast_variance * 252) * 100
            
            return forecast_vol
            
        except Exception as e:
            logger.error(f"Error in GARCH forecast: {e}")
            return None
    
    def detect_volatility_regime(self, current_vol: float) -> Dict:
        """
        Detect current volatility regime.
        
        Args:
            current_vol: Current volatility percentage
        
        Returns:
            Dict with regime info
        """
        for regime, (low, high) in self.volatility_regimes.items():
            if low <= current_vol < high:
                return {
                    'regime': regime.upper().replace('_', ' '),
                    'level': current_vol,
                    'range': f"{low}-{high}%",
                    'description': self._get_regime_description(regime)
                }
        
        return {
            'regime': 'UNKNOWN',
            'level': current_vol,
            'range': 'N/A',
            'description': 'Unable to classify'
        }
    
    def _get_regime_description(self, regime: str) -> str:
        """Get description for volatility regime"""
        descriptions = {
            'very_low': 'Extremely calm market - Options very cheap',
            'low': 'Low volatility - Good for selling options',
            'normal': 'Normal market conditions',
            'elevated': 'Increased volatility - Caution advised',
            'high': 'High volatility - Options expensive',
            'extreme': 'Extreme volatility - High risk environment'
        }
        return descriptions.get(regime, 'Unknown regime')
    
    def forecast_volatility(self, df: pd.DataFrame, vix_current: float = None) -> Dict:
        """
        Generate comprehensive volatility forecast.
        
        Args:
            df: DataFrame with OHLCV data
            vix_current: Current VIX value (optional)
        
        Returns:
            Dict with forecasts and analysis
        """
        try:
            if df.empty or len(df) < 30:
                return {'error': 'Insufficient data for volatility forecasting'}
            
            # Calculate different volatility measures
            hv_20 = self.calculate_historical_volatility(df, window=20)
            hv_10 = self.calculate_historical_volatility(df, window=10)
            parkinson = self.calculate_parkinson_volatility(df, window=20)
            garman_klass = self.calculate_garman_klass_volatility(df, window=20)
            atr_vol = self.calculate_atr_volatility(df, period=14)
            
            # Current values
            current_hv = hv_20.iloc[-1] if not hv_20.empty else 0
            current_hv_short = hv_10.iloc[-1] if not hv_10.empty else 0
            current_parkinson = parkinson.iloc[-1] if not parkinson.empty else 0
            current_gk = garman_klass.iloc[-1] if not garman_klass.empty else 0
            current_atr = atr_vol.iloc[-1] if not atr_vol.empty else 0
            
            # Calculate log returns for GARCH
            log_returns = np.log(df['close'] / df['close'].shift(1))
            
            # GARCH forecasts for different horizons
            garch_5min = self.simple_garch_forecast(log_returns, horizon=1)
            garch_15min = self.simple_garch_forecast(log_returns, horizon=3)
            garch_30min = self.simple_garch_forecast(log_returns, horizon=6)
            garch_1day = self.simple_garch_forecast(log_returns, horizon=75)  # ~375 min per day
            
            # Ensemble forecast (weighted average of methods)
            weights = {
                'hv': 0.25,
                'parkinson': 0.20,
                'garman_klass': 0.25,
                'atr': 0.15,
                'garch': 0.15
            }
            
            ensemble_current = (
                weights['hv'] * current_hv +
                weights['parkinson'] * current_parkinson +
                weights['garman_klass'] * current_gk +
                weights['atr'] * current_atr +
                weights['garch'] * (garch_5min or current_hv)
            )
            
            # Trend analysis (is volatility increasing or decreasing?)
            vol_trend = self._analyze_volatility_trend(hv_20)
            
            # Volatility regime
            regime = self.detect_volatility_regime(ensemble_current)
            
            # VIX comparison (if available)
            vix_analysis = None
            if vix_current:
                vix_analysis = {
                    'vix': vix_current,
                    'hv_vs_vix': current_hv - vix_current,
                    'interpretation': self._interpret_hv_vix_spread(current_hv, vix_current)
                }
            
            # Forecasts for different timeframes
            forecasts = {
                '5min': {
                    'forecast': garch_5min or ensemble_current,
                    'range_low': (garch_5min or ensemble_current) * 0.8,
                    'range_high': (garch_5min or ensemble_current) * 1.2,
                    'confidence': 'HIGH'
                },
                '15min': {
                    'forecast': garch_15min or ensemble_current * 1.1,
                    'range_low': (garch_15min or ensemble_current * 1.1) * 0.75,
                    'range_high': (garch_15min or ensemble_current * 1.1) * 1.25,
                    'confidence': 'MEDIUM'
                },
                '30min': {
                    'forecast': garch_30min or ensemble_current * 1.2,
                    'range_low': (garch_30min or ensemble_current * 1.2) * 0.7,
                    'range_high': (garch_30min or ensemble_current * 1.2) * 1.3,
                    'confidence': 'MEDIUM'
                },
                '1day': {
                    'forecast': garch_1day or ensemble_current * 1.5,
                    'range_low': (garch_1day or ensemble_current * 1.5) * 0.6,
                    'range_high': (garch_1day or ensemble_current * 1.5) * 1.4,
                    'confidence': 'LOW'
                }
            }
            
            # Trading implications
            implications = self._get_trading_implications(
                ensemble_current, vol_trend, regime['regime']
            )
            
            return {
                'current_volatility': {
                    'ensemble': round(ensemble_current, 2),
                    'historical_20d': round(current_hv, 2),
                    'historical_10d': round(current_hv_short, 2),
                    'parkinson': round(current_parkinson, 2),
                    'garman_klass': round(current_gk, 2),
                    'atr_based': round(current_atr, 2),
                },
                'forecasts': forecasts,
                'regime': regime,
                'trend': vol_trend,
                'vix_analysis': vix_analysis,
                'implications': implications,
                'generated_at': datetime.now(IST).strftime("%H:%M:%S IST"),
                'data_points': len(df)
            }
            
        except Exception as e:
            logger.error(f"Error in volatility forecasting: {e}")
            return {'error': str(e)}
    
    def _analyze_volatility_trend(self, vol_series: pd.Series) -> Dict:
        """Analyze if volatility is increasing or decreasing"""
        try:
            if len(vol_series) < 10:
                return {'trend': 'UNKNOWN', 'strength': 'N/A'}
            
            # Compare recent vs older volatility
            recent = vol_series.iloc[-5:].mean()
            older = vol_series.iloc[-20:-5].mean()
            
            change_pct = ((recent - older) / older) * 100
            
            if change_pct > 15:
                trend = 'RAPIDLY INCREASING'
                strength = 'STRONG'
            elif change_pct > 5:
                trend = 'INCREASING'
                strength = 'MODERATE'
            elif change_pct < -15:
                trend = 'RAPIDLY DECREASING'
                strength = 'STRONG'
            elif change_pct < -5:
                trend = 'DECREASING'
                strength = 'MODERATE'
            else:
                trend = 'STABLE'
                strength = 'WEAK'
            
            return {
                'trend': trend,
                'strength': strength,
                'change_pct': round(change_pct, 2),
                'recent_avg': round(recent, 2),
                'older_avg': round(older, 2)
            }
            
        except Exception as e:
            return {'trend': 'UNKNOWN', 'strength': 'N/A', 'error': str(e)}
    
    def _interpret_hv_vix_spread(self, hv: float, vix: float) -> str:
        """Interpret the spread between historical volatility and VIX"""
        spread = hv - vix
        
        if spread > 5:
            return "HV > VIX: Realized volatility exceeding expectations - Options may be underpriced"
        elif spread < -5:
            return "VIX > HV: Market expecting higher volatility - Options expensive"
        else:
            return "HV ≈ VIX: Realized and implied volatility aligned - Fair pricing"
    
    def _get_trading_implications(self, vol: float, trend: Dict, regime: str) -> Dict:
        """Get trading implications based on volatility analysis"""
        
        implications = {
            'options_strategy': '',
            'position_sizing': '',
            'risk_level': '',
            'recommendations': []
        }
        
        # Based on volatility level
        if 'VERY LOW' in regime or 'LOW' in regime:
            implications['options_strategy'] = 'SELL OPTIONS (Collect premium in low vol)'
            implications['position_sizing'] = 'Can increase position size'
            implications['risk_level'] = 'LOW'
            implications['recommendations'].append('Consider selling strangles/straddles')
            implications['recommendations'].append('Good time for credit spreads')
        
        elif 'HIGH' in regime or 'EXTREME' in regime:
            implications['options_strategy'] = 'BUY OPTIONS (Volatility expansion expected)'
            implications['position_sizing'] = 'Reduce position size'
            implications['risk_level'] = 'HIGH'
            implications['recommendations'].append('Consider buying protective puts')
            implications['recommendations'].append('Avoid selling naked options')
        
        else:
            implications['options_strategy'] = 'NEUTRAL (Normal volatility environment)'
            implications['position_sizing'] = 'Normal position size'
            implications['risk_level'] = 'MEDIUM'
            implications['recommendations'].append('Balanced approach - both buying and selling viable')
        
        # Based on trend
        if 'INCREASING' in trend.get('trend', ''):
            implications['recommendations'].append('⚠️ Volatility rising - Tighten stop losses')
            implications['recommendations'].append('Consider reducing leverage')
        elif 'DECREASING' in trend.get('trend', ''):
            implications['recommendations'].append('✓ Volatility falling - Market stabilizing')
            implications['recommendations'].append('Good environment for directional trades')
        
        return implications


def get_volatility_forecast(df: pd.DataFrame, vix_current: float = None) -> Dict:
    """
    Convenience function to get volatility forecast.
    
    Args:
        df: DataFrame with OHLCV data
        vix_current: Current VIX value
    
    Returns:
        Volatility forecast dictionary
    """
    forecaster = VolatilityForecaster()
    return forecaster.forecast_volatility(df, vix_current)


if __name__ == "__main__":
    # Test with sample data
    print("Volatility Forecaster - Test Mode")
    print("="*70)
    
    # This would normally use real data
    print("\nNote: Use with real OHLCV data from data_fetcher.py")
    print("Example usage:")
    print("  from data_fetcher import get_candle_data")
    print("  from volatility_forecaster import get_volatility_forecast")
    print("  df = get_candle_data()")
    print("  forecast = get_volatility_forecast(df, vix_current=15.5)")
