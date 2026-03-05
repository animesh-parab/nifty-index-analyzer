"""
Prediction State Management
Stores previous indicator values and market state for direction-based scoring
Created: March 4, 2026
"""

from datetime import datetime, time as dt_time
from typing import Optional, Dict
import pytz

IST = pytz.timezone('Asia/Kolkata')


class PredictionState:
    """
    Singleton class to maintain state between predictions.
    Stores previous indicator values for direction calculations.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Previous indicator values for direction calculation
        self.prev_rsi = None
        self.prev_macd_value = None
        self.prev_macd_signal = None
        self.prev_ema9 = None
        self.prev_ema21 = None
        self.prev_vix = None
        
        # Opening range tracking
        self.opening_range_high = None
        self.opening_range_low = None
        self.opening_range_established = False
        self.opening_range_date = None
        
        # Previous day levels
        self.prev_day_high = None
        self.prev_day_low = None
        self.prev_day_date = None
        
        # Current market regime
        self.current_regime = 'NEUTRAL'
        
        self._initialized = True
    
    def update_indicators(self, rsi: float, macd_value: float, macd_signal: float,
                         ema9: float, ema21: float, vix: float):
        """Update previous indicator values after each prediction"""
        self.prev_rsi = rsi
        self.prev_macd_value = macd_value
        self.prev_macd_signal = macd_signal
        self.prev_ema9 = ema9
        self.prev_ema21 = ema21
        self.prev_vix = vix
    
    def update_opening_range(self, price: float, current_time: datetime):
        """
        Update opening range during 9:30-9:45 window.
        Automatically resets if date changes.
        """
        today = current_time.date()
        
        # Reset if new day
        if self.opening_range_date != today:
            self.reset_opening_range()
            self.opening_range_date = today
        
        # Update range during 9:30-9:45
        hour = current_time.hour
        minute = current_time.minute
        time_minutes = hour * 60 + minute
        
        if 570 <= time_minutes <= 585:  # 9:30-9:45
            if self.opening_range_high is None or price > self.opening_range_high:
                self.opening_range_high = price
            if self.opening_range_low is None or price < self.opening_range_low:
                self.opening_range_low = price
            self.opening_range_established = True
    
    def reset_opening_range(self):
        """Reset opening range (called at start of new day)"""
        self.opening_range_high = None
        self.opening_range_low = None
        self.opening_range_established = False
    
    def update_previous_day_levels(self, high: float, low: float, date):
        """Update previous day high/low at market close or system startup"""
        self.prev_day_high = high
        self.prev_day_low = low
        self.prev_day_date = date
    
    def get_opening_range(self) -> Dict:
        """Get current opening range"""
        return {
            'high': self.opening_range_high,
            'low': self.opening_range_low,
            'established': self.opening_range_established
        }
    
    def get_previous_day_levels(self) -> Dict:
        """Get previous day high/low"""
        return {
            'high': self.prev_day_high,
            'low': self.prev_day_low,
            'date': self.prev_day_date
        }
    
    def has_previous_values(self) -> bool:
        """Check if we have previous values for direction calculations"""
        return all([
            self.prev_rsi is not None,
            self.prev_macd_value is not None,
            self.prev_macd_signal is not None,
            self.prev_ema9 is not None,
            self.prev_ema21 is not None,
            self.prev_vix is not None
        ])
    
    def reset_all(self):
        """Reset all state (for testing or system restart)"""
        self.__init__()
        self._initialized = True


# Global singleton instance
prediction_state = PredictionState()
