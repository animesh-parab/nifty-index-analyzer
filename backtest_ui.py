"""
backtest_ui.py
Streamlit UI for Backtesting Engine

Provides interactive interface for running backtests and viewing results.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import json

from backtesting_engine import BacktestingEngine


def render_backtest_ui():
    """Render backtesting UI in Streamlit"""
    
    st.markdown("## 📊 Backtesting Engine")
    st.markdown("Test AI prediction accuracy against historical data")
    
    # Configuration
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        symbol = st.selectbox(
            "Index",
            options=["^NSEI", "^NSEBANK"],
            format_func=lambda x: "NIFTY 50" if x == "^NSEI" else "BANK NIFTY",
            help="Select index to backtest"
        )
    
    with col2:
        days = st.number_input(
            "Days",
            min_value=1,
            max_value=60,
            value=7,
            help="Number of days to backtest (max 60 for intraday)"
        )
    
    with col3:
        interval = st.selectbox(
            "Interval",
            options=["5m", "15m", "30m", "1h"],
            help="Candle interval"
        )
    
    with col4:
        timeframe = st.number_input(
            "Prediction Timeframe (min)",
            min_value=5,
            max_value=120,
            value=30,
            step=5,
            help="How far ahead to predict"
        )
    
    # Initial capital
    initial_capital = st.number_input(
        "Initial Capital (₹)",
        min_value=10000,
        max_value=10000000,
        value=100000,
        step=10000,
        help="Starting capital for simulation"
    )
    
    # Run backtest button
    if st.button("🚀 Run Backtest", type="primary", use_container_width=True):
        with st.spinner("Running backtest... This may take a few minutes..."):
            # Initialize engine
            engine = BacktestingEngine(symbol=symbol, initial_capital=initial_capital)
            
            # Run backtest
            results = engine.run_backtest(
                days=days,
                interval=interval,
                timeframe_minutes=timeframe
            )
            
            # Store results in session state
            st.session_state.backtest_results = results
            st.session_state.backtest_engine = engine
    
    # Display results if available
    if 'backtest_results' in st.session_state:
        results = st.session_state.backtest_results
        
        if 'error' in results:
            st.error(f"Error: {results['error']}")
            return
        
        summary = results['summary']
        metrics = results['metrics']
        
        st.markdown("---")
        
        # Summary metrics
        st.markdown("### 📈 Performance Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Return",
                f"₹{summary['total_return']:,.0f}",
                f"{summary['return_pct']:.2f}%"
            )
        
        with col2:
            st.metric(
                "Win Rate",
                f"{summary['win_rate']:.1f}%",
                f"{summary['correct_predictions']}/{summary['total_predictions']}"
            )
        
        with col3:
            st.metric(
                "Final Capital",
                f"₹{summary['final_capital']:,.0f}",
                f"from ₹{summary['initial_capital']:,.0f}"
            )
        
        with col4:
            profit_factor = metrics.get('profit_factor', 0)
            st.metric(
                "Profit Factor",
                f"{profit_factor:.2f}",
                "Good" if profit_factor > 1.5 else "Fair" if profit_factor > 1 else "Poor"
            )
        
        # Detailed metrics
        st.markdown("### 📊 Detailed Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Trade Statistics**")
            st.write(f"Total Trades: {metrics.get('total_trades', 0)}")
            st.write(f"Winning Trades: {metrics.get('winning_trades', 0)}")
            st.write(f"Losing Trades: {metrics.get('losing_trades', 0)}")
            st.write(f"Avg Win: ₹{metrics.get('avg_win', 0):,.2f}")
            st.write(f"Avg Loss: ₹{metrics.get('avg_loss', 0):,.2f}")
        
        with col2:
            st.markdown("**Accuracy by Direction**")
            st.write(f"Bullish Accuracy: {metrics.get('bullish_accuracy', 0):.1f}%")
            st.write(f"Bearish Accuracy: {metrics.get('bearish_accuracy', 0):.1f}%")
            st.write(f"Avg Confidence: {metrics.get('avg_confidence', 0):.1f}%")
            st.write(f"Max Drawdown: ₹{metrics.get('max_drawdown', 0):,.2f}")
        
        # Equity curve
        st.markdown("### 📈 Equity Curve")
        
        trades_df = pd.DataFrame(results['trades'])
        
        if not trades_df.empty:
            # Create equity curve
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=list(range(len(trades_df))),
                y=trades_df['capital'],
                mode='lines',
                name='Capital',
                line=dict(color='#3fb950', width=2),
                fill='tozeroy',
                fillcolor='rgba(63, 185, 80, 0.1)'
            ))
            
            # Add initial capital line
            fig.add_hline(
                y=initial_capital,
                line_dash="dash",
                line_color="#8b949e",
                annotation_text="Initial Capital"
            )
            
            fig.update_layout(
                title="Capital Over Time",
                xaxis_title="Trade Number",
                yaxis_title="Capital (₹)",
                hovermode='x unified',
                template='plotly_dark',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Trade distribution
        st.markdown("### 📊 Trade Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Win/Loss distribution
            fig = go.Figure(data=[
                go.Bar(
                    x=['Wins', 'Losses'],
                    y=[metrics.get('winning_trades', 0), metrics.get('losing_trades', 0)],
                    marker_color=['#3fb950', '#f85149']
                )
            ])
            
            fig.update_layout(
                title="Win/Loss Distribution",
                yaxis_title="Number of Trades",
                template='plotly_dark',
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Direction accuracy
            fig = go.Figure(data=[
                go.Bar(
                    x=['Bullish', 'Bearish'],
                    y=[metrics.get('bullish_accuracy', 0), metrics.get('bearish_accuracy', 0)],
                    marker_color=['#3fb950', '#f85149']
                )
            ])
            
            fig.update_layout(
                title="Direction Accuracy",
                yaxis_title="Accuracy (%)",
                template='plotly_dark',
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent trades table
        st.markdown("### 📋 Recent Trades")
        
        if not trades_df.empty:
            # Format trades for display
            display_df = trades_df[['timestamp', 'predicted_direction', 'actual_direction', 
                                   'entry_price', 'exit_price', 'pnl', 'pnl_pct', 
                                   'confidence', 'correct']].tail(20).copy()
            
            display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            display_df['entry_price'] = display_df['entry_price'].round(2)
            display_df['exit_price'] = display_df['exit_price'].round(2)
            display_df['pnl'] = display_df['pnl'].round(2)
            display_df['pnl_pct'] = display_df['pnl_pct'].round(2)
            display_df['confidence'] = display_df['confidence'].round(0)
            
            # Rename columns
            display_df.columns = ['Time', 'Predicted', 'Actual', 'Entry', 'Exit', 
                                 'P&L (₹)', 'P&L (%)', 'Confidence', 'Correct']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
        
        # Download report
        st.markdown("### 💾 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Download JSON Report", use_container_width=True):
                engine = st.session_state.backtest_engine
                engine.generate_report("backtest_report.json")
                st.success("✓ Report saved to backtest_report.json")
        
        with col2:
            if st.button("📥 Download CSV Trades", use_container_width=True):
                trades_df.to_csv("backtest_trades.csv", index=False)
                st.success("✓ Trades saved to backtest_trades.csv")


if __name__ == "__main__":
    st.set_page_config(page_title="Backtesting Engine", layout="wide")
    render_backtest_ui()
