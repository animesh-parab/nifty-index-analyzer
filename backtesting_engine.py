"""
backtesting_engine.py
Backtesting Engine for AI Prediction Model

Tests prediction accuracy against historical data to evaluate model performance.
Provides detailed metrics, win rate, profit/loss analysis, and visualization.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import json
from typing import Dict, List, Tuple
import logging

from indicators import calculate_all_indicators, get_indicator_summary, detect_candlestick_patterns
from ai_engine_consensus import get_rule_based_prediction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BacktestingEngine:
    """
    Backtesting engine for testing AI predictions against historical data.
    
    Features:
    - Historical data fetching
    - Prediction accuracy testing
    - Win/loss rate calculation
    - Profit/loss simulation
    - Performance metrics
    - Detailed reporting
    """
    
    def __init__(self, symbol: str = "^NSEI", initial_capital: float = 100000):
        """
        Initialize backtesting engine.
        
        Args:
            symbol: Trading symbol (default: ^NSEI for Nifty 50)
            initial_capital: Starting capital for simulation
        """
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.results = []
        self.trades = []
        
    def fetch_historical_data(self, days: int = 30, interval: str = "5m") -> pd.DataFrame:
        """
        Fetch historical data for backtesting.
        
        Args:
            days: Number of days of historical data
            interval: Data interval (5m, 15m, 1h, 1d)
        
        Returns:
            DataFrame with OHLCV data and indicators
        """
        try:
            logger.info(f"Fetching {days} days of historical data for {self.symbol}...")
            
            # Calculate period
            if interval in ["1m", "5m", "15m", "30m"]:
                # Intraday data limited to 60 days
                period = f"{min(days, 60)}d"
            else:
                period = f"{days}d"
            
            # Fetch data
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.error("No historical data fetched")
                return pd.DataFrame()
            
            # Ensure lowercase column names for consistency
            df.columns = [col.lower() if isinstance(col, str) else col for col in df.columns]
            
            # Also keep uppercase versions for compatibility
            if 'close' in df.columns:
                df['Close'] = df['close']
                df['Open'] = df['open']
                df['High'] = df['high']
                df['Low'] = df['low']
                df['Volume'] = df['volume']
            
            # Calculate indicators
            df = calculate_all_indicators(df)
            
            # Filter market hours (9:15 AM - 3:30 PM IST) for intraday
            if interval in ["1m", "5m", "15m", "30m"]:
                try:
                    df = df.between_time("09:15", "15:30")
                except:
                    # If timezone issues, skip filtering
                    pass
            
            logger.info(f"✓ Fetched {len(df)} candles")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return pd.DataFrame()
    
    def generate_prediction(self, df: pd.DataFrame, index: int) -> Dict:
        """
        Generate prediction for a specific point in time.
        
        Args:
            df: Historical data DataFrame
            index: Index of current candle
        
        Returns:
            Prediction dictionary
        """
        try:
            # Get data up to current point (no future data)
            historical_df = df.iloc[:index+1].copy()
            
            # Get indicator summary
            indicator_summary = get_indicator_summary(historical_df)
            
            # Mock options data (simplified for backtesting)
            oi_data = {
                'pcr': 1.0,  # Neutral
                'max_pain': historical_df['Close'].iloc[-1],
                'total_ce_oi': 1000000,
                'total_pe_oi': 1000000,
            }
            
            # Mock VIX data
            vix_data = {'vix': 15.0}
            
            # Mock news sentiment
            news_sentiment = {'score': 0, 'label': 'neutral'}
            
            # Generate prediction using rule-based model
            prediction = get_rule_based_prediction(
                indicator_summary, oi_data, vix_data, news_sentiment
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error generating prediction: {e}")
            return {'direction': 'SIDEWAYS', 'confidence': 0}
    
    def evaluate_prediction(self, prediction: Dict, actual_move: float, 
                          timeframe_minutes: int = 30) -> Dict:
        """
        Evaluate prediction accuracy against actual price movement.
        
        Args:
            prediction: Prediction dictionary
            actual_move: Actual price change (positive = up, negative = down)
            timeframe_minutes: Prediction timeframe
        
        Returns:
            Evaluation results
        """
        direction = prediction.get('direction', 'SIDEWAYS')
        confidence = prediction.get('confidence', 0)
        
        # Determine if prediction was correct
        if direction == 'BULLISH':
            correct = actual_move > 0
            expected_direction = 'UP'
        elif direction == 'BEARISH':
            correct = actual_move < 0
            expected_direction = 'DOWN'
        else:
            # Sideways: correct if move is small (< 0.2%)
            correct = abs(actual_move) < 0.2
            expected_direction = 'SIDEWAYS'
        
        return {
            'predicted_direction': expected_direction,
            'actual_direction': 'UP' if actual_move > 0 else 'DOWN' if actual_move < 0 else 'SIDEWAYS',
            'actual_move_pct': actual_move,
            'correct': correct,
            'confidence': confidence,
            'timeframe': timeframe_minutes
        }
    
    def simulate_trade(self, prediction: Dict, entry_price: float, 
                      exit_price: float, capital: float) -> Dict:
        """
        Simulate a trade based on prediction.
        
        Args:
            prediction: Prediction dictionary
            entry_price: Entry price
            exit_price: Exit price
            capital: Available capital
        
        Returns:
            Trade result
        """
        direction = prediction.get('direction', 'SIDEWAYS')
        confidence = prediction.get('confidence', 0)
        
        # Position sizing based on confidence
        # Higher confidence = larger position
        position_size = capital * (confidence / 100) * 0.1  # Max 10% per trade
        
        # Calculate profit/loss
        if direction == 'BULLISH':
            # Long position
            quantity = position_size / entry_price
            pnl = quantity * (exit_price - entry_price)
            pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        elif direction == 'BEARISH':
            # Short position
            quantity = position_size / entry_price
            pnl = quantity * (entry_price - exit_price)
            pnl_pct = ((entry_price - exit_price) / entry_price) * 100
        else:
            # No trade for sideways
            pnl = 0
            pnl_pct = 0
            quantity = 0
        
        return {
            'direction': direction,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'quantity': quantity,
            'position_size': position_size,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'confidence': confidence
        }
    
    def run_backtest(self, days: int = 30, interval: str = "5m", 
                    timeframe_minutes: int = 30) -> Dict:
        """
        Run complete backtest on historical data.
        
        Args:
            days: Number of days to backtest
            interval: Data interval
            timeframe_minutes: Prediction timeframe
        
        Returns:
            Backtest results
        """
        logger.info(f"Starting backtest: {days} days, {interval} interval, {timeframe_minutes}min predictions")
        
        # Fetch historical data
        df = self.fetch_historical_data(days, interval)
        
        if df.empty:
            return {'error': 'No historical data available'}
        
        # Calculate number of candles for timeframe
        interval_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30, '1h': 60, '1d': 1440
        }.get(interval, 5)
        
        candles_ahead = max(1, timeframe_minutes // interval_minutes)
        
        # Initialize tracking
        self.results = []
        self.trades = []
        capital = self.initial_capital
        
        # Run backtest
        total_predictions = 0
        correct_predictions = 0
        
        for i in range(len(df) - candles_ahead):
            try:
                # Current candle - handle both uppercase and lowercase
                current_candle = df.iloc[i]
                current_price = current_candle.get('Close', current_candle.get('close', 0))
                current_time = current_candle.name
                
                # Generate prediction
                prediction = self.generate_prediction(df, i)
                
                # Future candle (actual outcome)
                future_candle = df.iloc[i + candles_ahead]
                future_price = future_candle.get('Close', future_candle.get('close', 0))
                
                # Calculate actual move
                actual_move_pct = ((future_price - current_price) / current_price) * 100
                
                # Evaluate prediction
                evaluation = self.evaluate_prediction(prediction, actual_move_pct, timeframe_minutes)
                
                # Simulate trade
                trade = self.simulate_trade(prediction, current_price, future_price, capital)
                
                # Update capital
                capital += trade['pnl']
                
                # Store results
                result = {
                    'timestamp': current_time,
                    'entry_price': current_price,
                    'exit_price': future_price,
                    **evaluation,
                    **trade,
                    'capital': capital
                }
                
                self.results.append(result)
                
                if prediction['direction'] != 'SIDEWAYS':
                    self.trades.append(result)
                    total_predictions += 1
                    if evaluation['correct']:
                        correct_predictions += 1
                
                # Progress logging
                if (i + 1) % 100 == 0:
                    logger.info(f"Processed {i + 1}/{len(df) - candles_ahead} candles...")
                    
            except Exception as e:
                logger.error(f"Error at index {i}: {e}")
                continue
        
        # Calculate metrics
        metrics = self.calculate_metrics()
        
        logger.info(f"✓ Backtest complete: {total_predictions} predictions, {correct_predictions} correct")
        
        return {
            'metrics': metrics,
            'results': self.results,
            'trades': self.trades,
            'summary': {
                'total_predictions': total_predictions,
                'correct_predictions': correct_predictions,
                'win_rate': (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0,
                'initial_capital': self.initial_capital,
                'final_capital': capital,
                'total_return': capital - self.initial_capital,
                'return_pct': ((capital - self.initial_capital) / self.initial_capital) * 100
            }
        }
    
    def calculate_metrics(self) -> Dict:
        """
        Calculate detailed performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        if not self.trades:
            return {}
        
        df_trades = pd.DataFrame(self.trades)
        
        # Win/Loss metrics
        winning_trades = df_trades[df_trades['pnl'] > 0]
        losing_trades = df_trades[df_trades['pnl'] < 0]
        
        total_trades = len(df_trades)
        wins = len(winning_trades)
        losses = len(losing_trades)
        
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        # Profit/Loss metrics
        total_pnl = df_trades['pnl'].sum()
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        
        # Risk/Reward
        profit_factor = abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 and losing_trades['pnl'].sum() != 0 else 0
        
        # Drawdown
        df_trades['cumulative_pnl'] = df_trades['pnl'].cumsum()
        df_trades['peak'] = df_trades['cumulative_pnl'].cummax()
        df_trades['drawdown'] = df_trades['cumulative_pnl'] - df_trades['peak']
        max_drawdown = df_trades['drawdown'].min()
        
        # Direction accuracy
        bullish_trades = df_trades[df_trades['predicted_direction'] == 'UP']
        bearish_trades = df_trades[df_trades['predicted_direction'] == 'DOWN']
        
        bullish_accuracy = (bullish_trades['correct'].sum() / len(bullish_trades) * 100) if len(bullish_trades) > 0 else 0
        bearish_accuracy = (bearish_trades['correct'].sum() / len(bearish_trades) * 100) if len(bearish_trades) > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': wins,
            'losing_trades': losses,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'bullish_accuracy': bullish_accuracy,
            'bearish_accuracy': bearish_accuracy,
            'avg_confidence': df_trades['confidence'].mean(),
        }
    
    def generate_report(self, output_file: str = "backtest_report.json"):
        """
        Generate detailed backtest report.
        
        Args:
            output_file: Output file path
        """
        if not self.results:
            logger.warning("No backtest results to report")
            return
        
        metrics = self.calculate_metrics()
        
        report = {
            'backtest_info': {
                'symbol': self.symbol,
                'initial_capital': self.initial_capital,
                'total_candles': len(self.results),
                'total_trades': len(self.trades),
            },
            'performance_metrics': metrics,
            'trades': self.trades[:100],  # First 100 trades
            'summary': {
                'final_capital': self.results[-1]['capital'] if self.results else self.initial_capital,
                'total_return': self.results[-1]['capital'] - self.initial_capital if self.results else 0,
                'return_pct': ((self.results[-1]['capital'] - self.initial_capital) / self.initial_capital * 100) if self.results else 0,
            }
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"✓ Report saved to {output_file}")
        
        return report


def quick_backtest(days: int = 7, interval: str = "5m", timeframe: int = 30):
    """
    Quick backtest function for testing.
    
    Args:
        days: Number of days to backtest
        interval: Data interval
        timeframe: Prediction timeframe in minutes
    """
    print("\n" + "="*70)
    print("BACKTESTING ENGINE - QUICK TEST")
    print("="*70 + "\n")
    
    # Initialize engine
    engine = BacktestingEngine(symbol="^NSEI", initial_capital=100000)
    
    # Run backtest
    results = engine.run_backtest(days=days, interval=interval, timeframe_minutes=timeframe)
    
    if 'error' in results:
        print(f"Error: {results['error']}")
        return
    
    # Print summary
    summary = results['summary']
    metrics = results['metrics']
    
    print(f"Backtest Period: {days} days")
    print(f"Interval: {interval}")
    print(f"Prediction Timeframe: {timeframe} minutes")
    print(f"\n{'─'*70}\n")
    
    print("PERFORMANCE SUMMARY:")
    print(f"  Initial Capital: ₹{summary['initial_capital']:,.2f}")
    print(f"  Final Capital:   ₹{summary['final_capital']:,.2f}")
    print(f"  Total Return:    ₹{summary['total_return']:,.2f} ({summary['return_pct']:.2f}%)")
    print(f"\n{'─'*70}\n")
    
    print("PREDICTION ACCURACY:")
    print(f"  Total Predictions: {summary['total_predictions']}")
    print(f"  Correct:           {summary['correct_predictions']}")
    print(f"  Win Rate:          {summary['win_rate']:.2f}%")
    print(f"\n{'─'*70}\n")
    
    if metrics:
        print("DETAILED METRICS:")
        print(f"  Total Trades:      {metrics['total_trades']}")
        print(f"  Winning Trades:    {metrics['winning_trades']}")
        print(f"  Losing Trades:     {metrics['losing_trades']}")
        print(f"  Avg Win:           ₹{metrics['avg_win']:,.2f}")
        print(f"  Avg Loss:          ₹{metrics['avg_loss']:,.2f}")
        print(f"  Profit Factor:     {metrics['profit_factor']:.2f}")
        print(f"  Max Drawdown:      ₹{metrics['max_drawdown']:,.2f}")
        print(f"  Bullish Accuracy:  {metrics['bullish_accuracy']:.2f}%")
        print(f"  Bearish Accuracy:  {metrics['bearish_accuracy']:.2f}%")
    
    print(f"\n{'='*70}\n")
    
    # Generate report
    engine.generate_report()
    print("✓ Detailed report saved to backtest_report.json")
    
    return results


if __name__ == "__main__":
    # Run quick backtest
    quick_backtest(days=7, interval="5m", timeframe=30)
